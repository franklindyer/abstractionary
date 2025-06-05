import random

from db_tools import *

class TrivialTranslator:
    def __init__(self):
        return

    def translate(self, word):
        return "_"

    def reset(self):
        return

class FakeWordTranslator:
    def __init__(self, con):
        self.wordmap = {}
        self.con = con

    def translate(self, word):
        if len(word) == 0:
            return ""
        if not word in self.wordmap.keys():
            rand_trans = db_random_nonsense(self.con)
            self.wordmap[word] = rand_trans
        return self.wordmap[word]

    def reset(self):
        self.wordmap = {}
