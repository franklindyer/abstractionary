import random
import string

def rand_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

class ClientPlayer:
    def __init__(self):
        self.id = rand_string(20)
        self.points = 0

class ServerGame:
    def __init__(self, text_filter):
        self.id = rand_string(20)
        self.active_player = ""
        self.target_word = ""
        self.desc_field = ""
        self.players = {}
        self.tf = text_filter
        self.chat = []

    def add_player(self):
        new_player = ClientPlayer()
        self.players[new_player.id] = new_player
        return new_player.id

    def delete_player(self, player_id):
        if player_id not in self.players.keys():
            return True
        del self.players[player_id]
        if len(self.players.keys()) == 0:
            return False
        if self.active_player == player_id:
            self.active_player = self.players.keys()[0]
        return True

    def get_desc(self):
        return self.desc_field

    def update_desc(self, player_id, new_desc):
        if player_id == self.active_player:
            self.desc_field = tf.filter(new_desc)

    def guess_word(self, player_id, guess_word):
        if (player_id != self.active_player) and \
            (player_id in self.players.keys()) and \
            (guess_word == self.target_word):
            return True
        return False
    
    def get_game_state(self):
        return {
            "active_player": self.active_player,
            "desc_field": self.desc_field,
            "chat": self.chat 
        } 
