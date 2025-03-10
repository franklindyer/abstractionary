import asyncio
import bs4
import json
import random
import requests
import string
import sys
from threading import Thread
import time
import urllib

import socketio

class MockClient():
    def __init__(self, id, baseurl, joinlink, master=None, chat_len=500):
        self.id = id
        self.name = f"p{id}"
        self.joinlink = joinlink
        self.sock = socketio.Client()
        self.url = urllib.parse.urlparse(baseurl)
        self.master = master
        self.chat_len = chat_len

        self.guess_timeout_ms = 1000
        self.prob_correct = 0.1

        @self.sock.on('gamemsg')
        def foo(data):
            json_dat = json.loads(data)
            if "target_word" in json_dat:
                self.master.target_word = json_dat["target_word"]

    def connect(self):
        addr = f"{self.url.geturl()}{self.joinlink}"
        print(addr)
        self.sock.connect(addr)
        self.sock.sleep(1)

    def send_status(self):
        state_dat = {
            "player_id": self.id,
            "player_name": self.name,
            "desc_field": f"I am the player with ID {self.id}",
        }
        state_str = json.dumps(state_dat)
        self.sock.emit('gamemsg', { "data": state_str })

    def send_chat(self, msg):
        chat_dat = {
            "player_id": self.id,
            "chat_msg": msg,
        }
        chat_str = json.dumps(chat_dat)
        self.sock.emit('chat', { "data": chat_str })

    def event_loop(self, n=-1):
        time_to_guess = 0
        time_to_status = 2000
        while n != 0:
            n += -1
            if time_to_guess <= time_to_status:
                time.sleep(time_to_guess / 1000)
                self.send_status()
                time_to_status += -time_to_guess
                time_to_guess = self.guess_timeout_ms
            else:
                time.sleep(time_to_status / 1000)
                if random.random() < self.prob_correct:
                    self.send_chat(self.master.target_word)
                else:
                    random_chat = ''.join(random.choice(string.ascii_lowercase + " "*10) for _ in range(self.chat_len))
                    self.send_chat(random_chat)
                time_to_guess += -time_to_status
                time_to_status = 2000

class MockClientGame:
    def __init__(self, baseurl, num_msg=10, msg_size=50):
        self.baseurl = baseurl
        self.joinlink = None
        self.clients = []
        self.target_word = ""
        self.rounds = -1

    def make_game(self, n=2, chat_len=500):
        res = requests.get(f"{self.baseurl}/newgame?uncommon=on", allow_redirects=False)
        player_id = res.cookies.get("player_id")
        res = requests.get(f"{self.baseurl}/game", cookies={"player_id": player_id})
        html = bs4.BeautifulSoup(res.content, features="html.parser")
        self.joinlink = html.find("a", {"id": "joinlink"})["href"]
        first_player = MockClient(player_id, self.baseurl, self.joinlink, master=self, chat_len=chat_len) 
        self.clients.append(first_player)
        for i in range(n-1):
            res = requests.get(f"{self.baseurl}{self.joinlink}", allow_redirects=False)
            player_id = res.cookies.get("player_id")
            nth_player = MockClient(player_id, self.baseurl, self.joinlink, master=self)
            nth_player.guess_timeout_ms = 50
            self.clients.append(nth_player)

    def run(self):
        for cli in self.clients:
            cli.connect()
            th = Thread(target = lambda: cli.event_loop(n=self.rounds))
            th.start()

for i in range(10):
    mg = MockClientGame("http://10.0.0.76:5001")
    mg.rounds = 100
    mg.make_game(n=8, chat_len=100)
    mg.run()
