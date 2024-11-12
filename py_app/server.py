from flask import Flask, make_response, redirect, render_template, request, send_from_directory
from flask_socketio import emit, SocketIO
import json
from threading import Lock

import sys

sys.path.append("./src")

from ServerGame import *
from TextFilter import *
from WordTranslator import *
from WordRanker import *
from WordGenerator import *

wr = WordRanker()
wr.ingest_data("data/concreteness-ranking.txt")

MAX_GAMES = 50
MAX_PLAYERS_PER_GAME = 6

class AbsServiceManager:
    def __init__(self):
        self.lock = Lock()
        self.game_map = {}
        self.player_to_game_map = {}
        self.public_games = []

    def build_game(self, category_list, difficulty):
        wt = FakeWordTranslator()
        wt.ingest_data("data/refined_non_english_words.txt")
        text_filter = TextFilter(wr, wt)
        text_filter.set_difficulty(difficulty)
        word_generator = CombinedWordGenerator(category_list)
        return ServerGame(text_filter, word_generator)

    def add_game(self, category_list, difficulty, public=False):
        self.lock.acquire()
        if len(self.game_map.keys()) >= MAX_GAMES:
            self.lock.release()
            return None
        new_game = self.build_game(category_list, difficulty)
        self.game_map[new_game.id] = new_game
        if public:
            self.public_games.append(new_game)
        player_id = new_game.add_player()
        self.player_to_game_map[player_id] = new_game
        self.lock.release()
        return player_id

    def add_player(self, prev_pid, gid):
        self.lock.acquire()
        if not gid in self.game_map:
            self.lock.release()
            return None
        if prev_pid is not None and prev_pid in self.player_to_game_map:
            self.player_to_game_map[prev_pid].delete_player(prev_pid)
            del self.player_to_game_map[prev_pid]
        game = self.game_map[gid]
        if len(game.player_list) >= MAX_PLAYERS_PER_GAME:
            self.lock.release()
            return None
        self.lock.release()
        
        with game.lock:
            player_id = game.add_player()
        
        with self.lock:
            self.player_to_game_map[player_id] = game
        return player_id

    def get_public_games(self):
        return self.public_games

    def purge_games(self):
        self.lock.acquire()
        deleted_ids = []
        for k in self.game_map:
            game = self.game_map[k]
            if len(game.player_list) == 0:
                deleted_ids = deleted_ids + [game.id]
                del game_map[k]
                if game in self.public_games:
                    self.public_games.remove(game)
        for pid in self.player_to_game_map:
            if self.player_to_game_map[pid].id in deleted_ids:
                del player_to_game_map[pid]
        self.lock.release()

    def get_game_with_id(self, gid):
        self.lock.acquire()
        game = self.game_map.get(gid)
        self.lock.release()
        return game

    def get_game_with_player(self, pid):
        self.lock.acquire()
        game = self.player_to_game_map.get(pid)
        self.lock.release()
        return game

sm = AbsServiceManager()
app = Flask(__name__, template_folder="./web")
socketio = SocketIO(app)

@app.route('/')
def serve_index():
    public_games = sm.get_public_games()
    return render_template("index.html", active_games=len(public_games), public_games=public_games)

@app.route('/static/<path:path>')
def serve_file(path):
    return send_from_directory('static', path)

@app.route('/newgame')
def serve_new_game():
    sm.purge_games()
    response = make_response(redirect('/game'))
    query_args = request.args.to_dict()
    categories = [k for k in query_args.keys() if k in generator_map.keys()]
    difficulty = request.args.get('difficulty', 1)
    player_id = sm.add_game(categories, difficulty, public=(query_args.get("public") == 'on'))
    if player_id is None:
        return make_response("Cannot make game. Try again later!", 403)
    response.set_cookie("player_id", player_id)
    return response

@app.route('/join/<game_id>')
def serve_join_game(game_id):
    prev_id = request.cookies.get("player_id")
    player_id = sm.add_player(prev_id, game_id)
    if player_id is None:
        return make_response("Cannot join game. It may be full, or may not exist.", 403) 
    response = make_response(redirect('/game'))
    response.set_cookie("player_id", player_id)
    return response

@app.route('/game')
def serve_game():
    player_id = request.cookies.get("player_id")
    game = sm.get_game_with_player(player_id)
    if game is None:
        return redirect("/")
    return render_template("game.html", game_id = game.id)

@app.route('/history')
def serve_history():
    player_id = request.cookies.get("player_id")
    game = sm.get_game_with_player(player_id)
    if game is None:
        return make_response("History not found.", 404)
    resp = response = make_response(game.get_history(), 200)
    resp.mimetype = "text/plain"
    return resp

@socketio.on('connect')
def socket_connect():
    print("CLIENT IS CONNECTED")

@socketio.on('gamemsg')
def socket_message(data):
    client_state = json.loads(data["data"])
    player_id = client_state.get("player_id")
    game = sm.get_game_with_player(player_id)
    if game is not None:
        game.lock.acquire()
        game.receive_client_state(request.sid, client_state)
        emit('gamemsg', json.dumps(game.get_game_state(player_id)))
        game.lock.release()

@socketio.on('chat')
def socket_chat(data):
    client_msg = json.loads(data["data"])
    player_id = client_msg.get("player_id")
    game = sm.get_game_with_player(player_id)
    if game is not None:
        game.lock.acquire()
        game.receive_chat(player_id, client_msg["chat_msg"])
        game.lock.release()

app.run(host='0.0.0.0', port=5001)
