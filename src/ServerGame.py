import random
import string

def rand_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

class ClientPlayer:
    def __init__(self):
        self.id = rand_string(20)
        self.name = "Anon"
        self.sock_id = None
        self.points = 0

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
        self.generate_word()

    def active_player(self):
        return self.player_list[self.active_player_index]

    def add_player(self):
        new_player = ClientPlayer()
        self.players[new_player.id] = new_player
        self.player_list = self.player_list + [new_player.id]
        return new_player.id

    def next_player(self):
        self.active_player_index = (self.active_player_index+1) % len(self.player_list)
        self.generate_word()

    def delete_player(self, player_id):
        self.player_list.remove(player_id)
        if player_id not in self.players:
            return True
        del self.players[player_id]
        if len(self.players.keys()) == 0:
            return False
        if self.active_player_index > len(self.player_list):
            self.active_player_index = self.active_player_id % len(self.player_list)
        return True

    def get_desc(self):
        return self.desc_field

    def update_desc(self, player_id, new_desc):
        if player_id == self.active_player():
            self.desc_field = self.tf.filter(new_desc)

    def generate_word(self):
        self.target_word = self.wg.gen_word()

    def guess_word(self, player_id, guess_word):
        if (player_id != self.active_player()) and \
            (player_id in self.players.keys()) and \
            (guess_word == self.target_word):
            return True
        return False
   
    def receive_client_state(self, sid, state):
        player_id = state["player_id"]
        if player_id not in self.players:
            return
        player = self.players[player_id]
        player.sock_id = sid
        if player.name == "Anon" and state["player_name"] != "":
            player.name = state["player_name"]
        if player_id == self.active_player():
            # print(f"Got client text: {state['desc_field']}")
            self.update_desc(player_id, state["desc_field"])
 
    def get_game_state(self, player_id):
        game_state = {
            "active_player": self.active_player(),
            "num_players": len(self.players.keys()),
            "player_names": [self.players[id].name for id in self.player_list],
            "desc_field": self.desc_field,
            "chat": self.chat,
            "describer": self.players[self.active_player()].name,
        }
        if player_id == self.active_player():
            game_state["target_word"] = self.target_word
        return game_state

    def receive_chat(self, id, chat_msg):
        if chat_msg.lower() == self.target_word:
            self.chat = [("WIN", "", f"Player {self.players[id].name} has guessed the word: {self.target_word}!")] + self.chat
            self.next_player()
            print(f"Player {id} has guessed the word.")
        else:
            self.chat = [("MSG", self.players[id].name, chat_msg)] + self.chat
        self.chat = self.chat[:20]
