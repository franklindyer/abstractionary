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

    def ingest_fake_words(self, wordlist):
        self.fakelist = open(wordlist, 'r').readlines()
        self.fakelist = random.shuffle(self.fakelist)

    def translate(self, word):
        if not word in self.wordmap.keys():
            self.wordmap[word] = self.fakelist[0]
            self.fakelist = self.fakelist[1:]
        return self.wordmap[word]
