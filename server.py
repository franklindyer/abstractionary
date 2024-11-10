from flask import Flask, make_response, redirect, render_template, request
from flask_socketio import emit, SocketIO
import json

import sys

sys.path.append("./src")

from ServerGame import *
from TextFilter import *
from WordTranslator import *
from WordRanker import *
from WordGenerator import *

wr = WordRanker()
wr.ingest_data("data/concreteness-ranking.txt")

game_map = {}
player_to_game_map = {}

def build_new_game(category_list, difficulty):
    wt = FakeWordTranslator()
    wt.ingest_data("data/refined_non_english_words.txt")
    text_filter = TextFilter(wr, wt)
    text_filter.set_difficulty(difficulty)
    word_generator = CombinedWordGenerator(category_list)
    return ServerGame(text_filter, word_generator)

def purge_games():
    deleted_ids = []
    for k in game_map:
        game = game_map[k]
        if len(game.player_list) == 0:
            deleted_ids = deleted_ids + [game.id]
            del game_map[k]
    for pid in player_to_game_map:
        if player_to_game_map[pid].id in deleted_ids:
            del player_to_game_map[pid]

app = Flask(__name__, template_folder="./web")
socketio = SocketIO(app)

@app.route('/')
def serve_index():
    return render_template("index.html", active_games = len(game_map.keys()))

@app.route('/newgame')
def serve_new_game():
    purge_games()
    gkeys = [k for k in game_map.keys()]
    for game_id in gkeys:
        if game_map[game_id].clean_inactive_players():
            del game_map[game_id]
    response = make_response(redirect('/game'))
    categories = [k for k in request.args.to_dict().keys() if k in generator_map.keys()]
    difficulty = request.args.get('difficulty', 1)
    new_game = build_new_game(categories, difficulty)
    game_map[new_game.id] = new_game
    player_id = new_game.add_player()
    player_to_game_map[player_id] = new_game
    response.set_cookie("player_id", player_id)
    return response

@app.route('/join/<game_id>')
def serve_join_game(game_id):
    if not game_id in game_map.keys():
        return make_response(redirect('/'))
    if "player_id" in request.cookies:
        prev_id = request.cookies["player_id"]
        if prev_id in player_to_game_map:
            player_to_game_map[prev_id].delete_player(prev_id)
            del player_to_game_map[prev_id]
    game = game_map[game_id]
    game.lock.acquire()
    player_id = game.add_player()
    game.lock.release()
    player_to_game_map[player_id] = game
    response = make_response(redirect('/game'))
    response.set_cookie("player_id", player_id)
    return response

@app.route('/game')
def serve_game():
    if not "player_id" in request.cookies:
        return make_response(redirect('/'))
    player_id = request.cookies["player_id"]
    if not player_id in player_to_game_map:
        return make_response(redirect('/'))
    game = player_to_game_map[player_id]
    return render_template("game.html", game_id = game.id)

@app.route('/history')
def serve_history():
    if not "player_id" in request.cookies:
        return make_response("History not found.", 404) 
    player_id = request.cookies["player_id"]
    if not player_id in player_to_game_map:
        return make_response("History not found.", 404) 
    game = player_to_game_map[player_id]
    resp = response = make_response(game.get_history(), 200)
    resp.mimetype = "text/plain"
    return resp

@socketio.on('connect')
def socket_connect():
    print("CLIENT IS CONNECTED")

@socketio.on('gamemsg')
def socket_message(data):
    client_state = json.loads(data["data"])
    if "player_id" not in client_state or client_state["player_id"] not in player_to_game_map:
        return
    player_id = client_state["player_id"]
    game = player_to_game_map[player_id]
    game.lock.acquire()
    game.receive_client_state(request.sid, client_state)
    emit('gamemsg', json.dumps(game.get_game_state(player_id)))
    game.lock.release()

@socketio.on('chat')
def socket_chat(data):
    client_msg = json.loads(data["data"])
    if "player_id" not in client_msg or client_msg["player_id"] not in player_to_game_map:
        # print("ERROR: Player identity not found in socket message.")
        return
    player_id = client_msg["player_id"]
    game = player_to_game_map[player_id]
    game.lock.acquire()
    game.receive_chat(player_id, client_msg["chat_msg"])
    game.lock.release()

app.run(host='0.0.0.0', port=5001)
