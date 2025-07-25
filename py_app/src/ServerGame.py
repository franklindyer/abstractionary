from datetime import datetime
import os
import random
import re
import string
from threading import Lock

DESC_LENGTH_LIMIT = int(os.environ.get("DESC_LENGTH_LIMIT")) or 10000
NAME_LENGTH_LIMIT = int(os.environ.get("NAME_LENGTH_LIMIT")) or 10
CHAT_LENGTH_LIMIT = int(os.environ.get("CHAT_LENGTH_LIMIT")) or 100
CHAT_LIMIT = int(os.environ.get("CHAT_LIMIT")) or 50
INACTIVITY_LIMIT_SECONDS = int(os.environ.get("INACTIVITY_LIMIT_SECONDS")) or 60

def rand_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

class ClientPlayer:
    def __init__(self):
        self.id = rand_string(20)
        self.icon = random.randint(0,300)
        self.score = 0
        self.name = "Anon"
        self.sock_id = None
        self.points = 0
        self.last_active = datetime.now()

    def register_activity(self):
        self.last_active = datetime.now()

    def is_inactive(self):
        return (datetime.now() - self.last_active).seconds > INACTIVITY_LIMIT_SECONDS

    def dictify(self):
        return {
            "name": self.name,
            "icon": f"/static/icon_{self.icon}.png",
            "points": self.points,
            "id": self.id[:5]
        }

class ServerGame:
    def __init__(self, text_filter, word_generator):
        self.id = rand_string(20)
        self.active_player_index = 0
        self.desc_field = ""
        self.player_list = []
        self.players = {}
        self.tf = text_filter
        self.wg = word_generator
        self.chat = []
        self.chat_history = []
        self.last_history = "/not/a/path"
        self.num_target_choices = 3
        self.recent_targets = []
        self.recent_targets_length = 50
        self.generate_words()
        self.last_cleaned = datetime.now()
        self.lock = Lock()
        self.words_used_in_round = 0

    def active_player(self):
        return self.player_list[self.active_player_index]

    def get_teaser(self):
        return f"Guess the phrase '{self.tf.filter(self.target_words[0])}'"

    def add_player(self):
        new_player = ClientPlayer()
        self.players[new_player.id] = new_player
        self.player_list = self.player_list + [new_player.id]
        return new_player.id

    def next_player(self):
        self.active_player_index = (self.active_player_index+1) % len(self.player_list)
        self.generate_words()
        self.words_used_in_round = 0

    def delete_player(self, player_id):
        if player_id not in self.players:
            return True
        del self.players[player_id]
        self.player_list.remove(player_id)
        if len(self.players.keys()) == 0:
            return False
        if self.active_player_index >= len(self.player_list) and len(self.player_list) > 0:
            self.active_player_index = self.active_player_index % len(self.player_list)
        return True

    def clean_inactive_players(self):
        ids = [k for k in self.players.keys()]
        for player_id in ids:
            if self.players[player_id].is_inactive():
                self.delete_player(player_id)
        if len(self.players) == 0:
            return True
        return False

    def add_chat(self, msg_type, sender_name, msg):
        self.chat = [(msg_type, sender_name, msg)] + self.chat
        self.chat = self.chat[:CHAT_LIMIT] 
        self.chat_history = self.chat_history + [(msg_type, sender_name, msg)]

    def save_history(self, winning_word):
        filename = f"./history/{winning_word}-{self.id}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"
        self.last_history = filename
        with open(filename, 'w+') as f:
            for cmsg in self.chat_history:
                if cmsg[0] == "HINT":
                    f.write(f"* {cmsg[1]} : {cmsg[2]}\n")
                elif cmsg[0] == "MSG":
                    f.write(f"{cmsg[1]} : {cmsg[2]}\n")
                else:
                    f.write(f"{cmsg[2]}\n")
            f.write(f"At end of round, the description preview said: {self.desc_field}")
        self.chat_history = []

    def get_desc(self):
        return self.desc_field

    def update_desc(self, player_id, new_desc):
        self.desc_field = self.tf.filter(new_desc)

    def get_history(self):
        if not os.path.isfile(self.last_history):
            return "There is no history for your game."
        return open(self.last_history, 'r').read()

    def generate_words(self):
        self.target_words = [self.wg.gen_word() for i in range(self.num_target_choices)]
        # Make sure recently repeated words are avoided
        for i in range(len(self.target_words)):
            while self.target_words[i] in self.recent_targets:
                self.target_words[i] = self.wg.gen_word()
        self.tf.set_target_phrases(self.target_words) 
        self.tf.wt.reset()

    def guess_word(self, player_id, guess_word):
        # Normalize guess word to allow slight variations to be marked as correct
        guess_word = re.sub(r' +', ' ', guess_word.lower().strip())
        if (player_id != self.active_player()) and \
            (player_id in self.players.keys()) and \
            (guess_word in self.target_words):
            return True
        return False
   
    def receive_client_state(self, sid, state):
        if (datetime.now() - self.last_cleaned).seconds > INACTIVITY_LIMIT_SECONDS:
            self.clean_inactive_players()
        player_id = state["player_id"]
        if player_id not in self.players:
            return
        player = self.players[player_id]
        player.register_activity()
        player.sock_id = sid
        if player.name == "Anon" and state["player_name"] != "":
            player.name = state["player_name"][:NAME_LENGTH_LIMIT]
        if player_id == self.active_player():
            if len(self.target_words) > 1 and state["target_word"] in self.target_words:
                # Active player has chosen a target word
                self.target_words = [state["target_word"]]
            if len(self.target_words) == 1:
                # Only send the active player's hint if they have chosen a word 
                self.update_desc(player_id, state["desc_field"][:DESC_LENGTH_LIMIT])
 
    def get_game_state(self, player_id):
        game_state = {
            # "active_player": self.active_player()[:10],
            "num_players": len(self.players.keys()),
            "players": [self.players[id].dictify() for id in self.player_list],
            "chat": self.chat,
            "desc_field": self.desc_field,
            "describer": self.players[self.active_player()].name,
        }
        if player_id == self.active_player():
            game_state["target_words"] = self.target_words
        return game_state

    def receive_chat(self, id, chat_msg):
        chat_msg = chat_msg.strip()
        if len(chat_msg) == 0:
            # Ignore whitespace-only messages
            return
        elif id == self.active_player():
            chat_msg = chat_msg[:DESC_LENGTH_LIMIT]
            self.words_used_in_round = self.words_used_in_round + len(chat_msg.split(' '))
            self.add_chat("HINT", self.players[id].name, self.tf.filter(chat_msg))
        elif chat_msg.lower() in self.target_words:
            chat_msg = chat_msg[:CHAT_LENGTH_LIMIT]
            score = max(0, 200-self.words_used_in_round)
            self.players[id].points += score // 2
            self.players[self.active_player()].points += score
            self.recent_targets = ([chat_msg.lower()] + self.recent_targets)[:self.recent_targets_length]
            win_msg = f"Player {self.players[id].name} has guessed the word: {chat_msg.lower()}!"
            self.add_chat("WIN", "", win_msg)
            self.save_history(chat_msg.lower())
            self.next_player()
        else:
            self.add_chat("MSG", self.players[id].name, chat_msg[:CHAT_LENGTH_LIMIT])
