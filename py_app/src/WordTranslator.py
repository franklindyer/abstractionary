import random

class TrivialTranslator:
    def __init__(self):
        return

    def translate(self, word):
        return "_"

    def reset(self):
        return

class FakeWordTranslator:
    def __init__(self):
        self.fakelist = ["squanch"]
        self.wordmap = {}

    def ingest_data(self, wordlist):
        self.fakelist = [ln.strip() for ln in open(wordlist, 'r').readlines()]

    def translate(self, word):
        if not word in self.wordmap.keys():
            self.wordmap[word] = random.choice(self.fakelist)
        return self.wordmap[word]

    def reset(self):
        self.wordmap = {}
