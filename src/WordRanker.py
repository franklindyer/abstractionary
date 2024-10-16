import random

class WordRanker:
    def __init__(self):
        self.data = {}
        self.wordlist = {}

    def ingest_data(self, freq_file):
        with open(freq_file, 'r') as f:
            for ln in f.readlines():
                ln_parts = ln.split('\t')
                index = int(ln_parts[0])-100
                word = ln_parts[1].lower()
                if index < 0:
                    continue
                if word in self.data.keys():
                    continue
                self.data[word] = index
                self.wordlist[index] = word 

    def lookup_index(self, word):
        res = self.data.get(word)
        return res

    def lookup_word(self, ind):
        return self.wordlist.get(ind)
