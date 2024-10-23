import asyncio
import bs4
import json
import openai
import os
import random
import requests
import sys
from threading import Thread
import time
import urllib

import socketio

openai.api_key = os.environ["OPENAI_API_KEY"]

ABSTRACTIONARY_SYSTEM_PROMPT = """
    You are playing a word-guessing game that is similar to pictionary or taboo.
    The game is called 'abstractionary'.
    The active player in the game must attempt to make the other players guess a 'target word'
    by describing that word (or phrase) to them.
    However, any words they use in their descriptions that are not among the most common English
    words will be replaced by nonsense words in a one-to-one mapping between uncommon English
    words and nonsense words.
"""

ACTIVE_PLAYER_SYSTEM_PROMPT = """
    You are currently the active player and the target phrase is '{}'.
    You must try to use very simple English words to describe this phrase. Your descriptions
    do not necessarily need to be complete sentences.
    In the chat are your previous attempts at describing it and the other players' guesses.
    Note that some of the words in your previous attempts have been substituted
    for nonsense words because you used words that were too uncommon in the English language.
    After you generate hints, players will try to guess your target phrase.
    Please generate a hint that will help make the players guess the target phrase.
    Your hint does not need to be a complete sentence.
    It should not contain any filler like 'my hint is...' or 'here is my hint...'.
    Keep in mind that if you use any uncommon English words, they might be converted
    into nonsense words.
"""

PASSIVE_PLAYER_SYSTEM_PROMPT = """
    Another player is currently the active player and you are trying to guess the target phrase.
    What follows is the current content of the game's chat.
    In the chat are your and other players' previous guesses, and the active player's attempts
    to describe the target phrase.
    The target word has not yet been guessed.
    Please make another guess.
    Your response should consist ONLY of your guess at the target word or phrase, nothing more or less.
    It should not be a complete sentence. Only one word (or a few words if you think that the
    target phrase includes more than one word).
    Do not include any 'filler' in your response such as "my guess is..." or "I think the word is...".
    Do not repeat any previous guesses either - if they appear in the chat, they are not correct.
"""

class OpenAIGameClient():
    def __init__(self, baseurl, joinlink, name="john doe"):
        self.id = None
        self.name = name
        self.joinlink = joinlink
        self.sock = socketio.Client()
        self.url = urllib.parse.urlparse(baseurl)
        self.ai = openai.OpenAI()
        self.messages = [] 
        self.guesses = []
        self.model = "gpt-3.5-turbo"
        self.is_describer = False
        self.target_word = None
        self.guess_timeout_ms = 20000

        @self.sock.on('gamemsg')
        def foo(data):
            json_dat = json.loads(data)
            if "target_word" in json_dat:
                self.is_describer = True
                self.target_word = json_dat["target_word"]
            else:
                self.is_describer = False
            self.refresh_messages(json_dat)

    def refresh_messages(self, game_dat):
        self.messages = []
        self.messages.append({
            "role": "system",
            "content": ABSTRACTIONARY_SYSTEM_PROMPT,
        })
        if self.is_describer:
            self.messages.append({
                "role": "system",
                "content": ACTIVE_PLAYER_SYSTEM_PROMPT.format(self.target_word),
            })
            for chat_msg in game_dat["chat"]:
                if chat_msg[0] == "WIN":
                    break
                role = "assistant" if chat_msg[0] == "HINT" else "user"
                content = chat_msg[2]
                self.messages.append({
                    "role": role,
                    "content": content,
                })
        else:
            self.messages.append({
                "role": "system",
                "content": PASSIVE_PLAYER_SYSTEM_PROMPT,
            })
            for chat_msg in game_dat["chat"]:
                if chat_msg[0] == "WIN":
                    break
                role = "assistant" if chat_msg[1] == self.name else "user"
                content = f"HINT: {chat_msg[2]}" if chat_msg[0] == "HINT" else chat_msg[2] 
                self.messages.append({
                    "role": role,
                    "content": content,
                })

    def make_message(self):
        if (len(self.messages) < 3) and (not self.is_describer):
            return None
        completion = self.ai.chat.completions.create(model=self.model, messages=self.messages)
        response = completion.choices[0].message.content
        print(response)
        if self.is_describer:
            return response
        else:
            word_guess = response
            if word_guess in self.guesses:
                return None
            self.guesses.append(word_guess)
            self.guesses = self.guesses[-10:]
            return word_guess

    def connect(self):
        res = requests.get(f"{self.url.geturl()}{self.joinlink}", allow_redirects=False)
        self.id = res.cookies.get("player_id")
        addr = f"{self.url.geturl()}/game"
        print(addr)
        self.sock.connect(addr)
        time.sleep(1)

    def send_status(self):
        state_dat = {
            "player_id": self.id,
            "player_name": self.name,
            "desc_field": "",
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

    def event_loop(self):
        time_to_guess = 0
        time_to_status = 2000
        while True:
            if time_to_status <= time_to_guess:
                time.sleep(time_to_status / 1000)
                self.send_status()
                time_to_guess += -time_to_status
                time_to_status = 2000
            else:
                time.sleep(time_to_guess / 1000)
                resp = self.make_message()
                if resp is not None:
                    self.send_chat(resp)
                time_to_status += -time_to_guess
                time_to_guess = self.guess_timeout_ms

baseurl = sys.argv[1]
joinlink = sys.argv[2]

ai_cli = OpenAIGameClient(baseurl, joinlink)
ai_cli.connect()
ai_cli.event_loop()
