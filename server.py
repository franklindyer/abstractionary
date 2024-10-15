from flask import Flask, make_response, redirect, render_template, request
from flask_socketio import SocketIO

import sys

sys.path.append("./src")

from ServerGame import *
from TextFilter import *
from WordTranslator import *
from WordRanker import *

wr = WordRanker()
wr.ingest_data("data/eng_news_2023_10K-words.txt")
wt = FakeWordTranslator()
wt.ingest_data("data/refined_non_english_words.txt")

game_map = {}
player_to_game_map = {}

app = Flask(__name__, template_folder="./web")
socketio = SocketIO(app)

@app.route('/')
def serve_index():
    return render_template("index.html")

@app.route('/newgame')
def serve_new_game():
    response = make_response(redirect('/game'))
    text_filter = TextFilter(wr, wt)
    text_filter.rank_bound = 2000
    new_game = ServerGame(text_filter)
    game_map[new_game.id] = new_game
    player_id = new_game.add_player()
    player_to_game_map[player_id] = new_game
    response.set_cookie("player", player_id)
    return response

@app.route('/join/<game_id>')
def serve_join_game(game_id):
    if not game_id in game_map.keys():
        return make_response(redirect('/'))
    if "player" in request.cookies:
        prev_id = request.cookies["player"]
        if prev_id in player_to_game_map:
            player_to_game_map[prev_id].delete_player()
            del player_to_game_map[prev_id]
    game = game_map[game_id]
    player_id = game.add_player()
    player_to_game_map[player_id] = game
    response = make_response(redirect('/game'))
    response.set_cookie("player", player_id)
    return response

@app.route('/game')
def serve_game():
    if not "player" in request.cookies:
        return make_response(redirect('/'))
    player_id = request.cookies["player"]
    if not player_id in player_to_game_map:
        return make_response(redirect('/'))
    game = player_to_game_map[player_id]
    return render_template("game.html", game_id = game.id)

# Valid message types from server to client:
# - DESC (clue description updated)
# - CHAT (new chat message)
# - UWIN (your guess was correct)
# - HOST (it is your turn to be the describer)
#
# Valid message types from client to server:
# - GUES (take a guess at the word)
# - DESC (update the description clue)
# - CHAT (new chat message from this user)
 
@socketio.on('connect')
def socket_connect():
    print("NOT IMPLEMENTED")

@socketio.on('message')
def socket_message(data):
    print("NOT IMPLEMENTED")

app.run()
