import random

class WordRanker:
    def __init__(self):
        self.data = {}
        self.wordlist = {}

    def ingest_data(self, freq_file):
        with open(freq_file, 'r') as f:
            index = 0
            for ln in f.readlines():
                index += 1
                word = ln.strip().lower()
                if word in self.data.keys():
                    continue
                self.data[word] = index
                self.wordlist[index] = word

    def lookup_index(self, word):
        res = self.data.get(word)
        return res

    def lookup_word(self, ind):
        return self.wordlist.get(ind)

googleWordRanker = WordRanker()
googleWordRanker.ingest_data("data/google-10000-english-usa.txt")
