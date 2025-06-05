from flask import Flask, make_response, redirect, render_template, request, send_from_directory, abort
from werkzeug.exceptions import HTTPException
from flask_socketio import emit, SocketIO
import json
import sqlite3
from threading import Lock

import sys

sys.path.append("./src")

from ServerGame import *
from TextFilter import *
from WordTranslator import *
from WordRanker import *
from WordGenerator import *

con = sqlite3.connect("./data/words.db", check_same_thread=False) 
cur = con.cursor()

generator_map = make_generator_map(con)
wr = WordRanker(con)

MAX_GAMES = 50
MAX_PLAYERS_PER_GAME = 6

class AbsServiceManager:
    def __init__(self):
        self.lock = Lock()
        self.game_map = {}
        self.player_to_game_map = {}
        self.public_games = []

    def build_game(self, category_list, difficulty):
        wt = FakeWordTranslator(con)
        # text_filter = TextFilter(wr, wt)
        # text_filter.set_difficulty(difficulty)
        text_filter = make_filter_of_type(difficulty, wr, wt)
        word_generator = CombinedWordGenerator(generator_map)
        return ServerGame(text_filter, word_generator)

    def add_game(self, category_list, difficulty, public=False):
        with self.lock:
            if len(self.game_map.keys()) >= MAX_GAMES:
                return None
            new_game = self.build_game(category_list, difficulty)
            self.game_map[new_game.id] = new_game
            if public:
                self.public_games.append(new_game)
            player_id = new_game.add_player()
            self.player_to_game_map[player_id] = new_game
        return player_id

    def add_player(self, prev_pid, gid):
        with self.lock:
            if not gid in self.game_map:
                return None
            if prev_pid is not None and prev_pid in self.player_to_game_map:
                self.player_to_game_map[prev_pid].delete_player(prev_pid)
                del self.player_to_game_map[prev_pid]
            game = self.game_map[gid]
            if len(game.player_list) >= MAX_PLAYERS_PER_GAME:
                return None
        
        with game.lock:
            player_id = game.add_player()
        
        with self.lock:
            self.player_to_game_map[player_id] = game
        return player_id

    def get_public_games(self):
        return self.public_games

    def purge_games(self):
        with self.lock:
            deleted_ids = []
            game_ids = [k for k in self.game_map.keys()]
            for k in game_ids:
                game = self.game_map[k]
                if len(game.player_list) == 0:
                    deleted_ids = deleted_ids + [game.id]
                    del self.game_map[k]
                    if game in self.public_games:
                        self.public_games.remove(game)
            player_ids = [p for p in self.player_to_game_map.keys()]
            for pid in player_ids:
                if self.player_to_game_map[pid].id in deleted_ids:
                    del self.player_to_game_map[pid]

    def get_game_with_id(self, gid):
        with self.lock:
            game = self.game_map.get(gid)
        return game

    def get_game_with_player(self, pid):
        with self.lock:
            game = self.player_to_game_map.get(pid)
        return game

sm = AbsServiceManager()
app = Flask(__name__, template_folder="./web")
socketio = SocketIO(app)

@app.route('/')
def serve_index():
    public_games = sm.get_public_games()
    return render_template("index.html", active_games=len(public_games), public_games=public_games)

@app.route('/robots.txt')
def serve_robots():
    return send_from_directory('static', 'robots.txt')

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
        return abort(403, "Cannot make game. Try again later!")
    response.set_cookie("player_id", player_id)
    return response

@app.route('/join/<game_id>')
def serve_join_game(game_id):
    user_agent = request.headers.get("User-Agent")
    if "bot" in user_agent.lower():
        return abort(403, "Cannot join the game as a robot. Sorry!")
    prev_id = request.cookies.get("player_id")
    player_id = sm.add_player(prev_id, game_id)
    if player_id is None:
        return abort(403, "Cannot join game. It may be full, or may not exist.") 
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
        return abort(404, "History not found.")
    resp = response = make_response(game.get_history(), 200)
    resp.mimetype = "text/plain"
    return resp

ERROR_PICS = [
    "icon_13.png", "icon_23.png", "icon_27.png", "icon_31.png", "icon_45.png", "icon_64.png", 
    "icon_66.png", "icon_70.png", "icon_73.png", "icon_118.png", "icon_132.png", "icon_148.png",
    "icon_167.png", "icon_177.png", "icon_194.png", "icon_197.png", "icon_204.png", "icon_223.png"
]

@app.errorhandler(HTTPException)
def handle_error(e):
    err_img = random.choice(ERROR_PICS)
    desc = e.description
    return render_template("error.html", error_code=e.code, error_img=err_img, error_msg=desc)

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
