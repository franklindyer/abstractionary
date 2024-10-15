import random

class TrivialTranslator:
    def __init__(self):
        return

    def translate(self, word):
        return "___"

class FakeWordTranslator:
    def __init__(self):
        self.fakelist = ["squanch"]
        self.wordmap = {}

    def ingest_data(self, wordlist):
        self.fakelist = [ln.strip() for ln in open(wordlist, 'r').readlines()]
        random.shuffle(self.fakelist)

    def translate(self, word):
        if not word in self.wordmap.keys():
            self.wordmap[word] = self.fakelist[0]
            self.fakelist = self.fakelist[1:]
        return self.wordmap[word]
