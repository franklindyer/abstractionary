from flask import Flask
from flask_socketio import SocketIO

games_dict = {}

app = Flask(__name__)

@app.route('/')
def serve_index():
    return "Well hey there!"

@app.route('/newgame')
def serve_new_game():
    return "NOT IMPLEMENTED"

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
