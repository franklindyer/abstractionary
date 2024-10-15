import random

class WordRanker:
    def __init__(self):
        self.data = {}

    def ingest_data(self, freq_file):
        with open(freq_file, 'r') as f:
            for ln in f.readlines():
                ln_parts = ln.split('\t')
                index = int(ln_parts[0])-100
                if index < 0:
                    continue
                if ln_parts[1].lower() in self.data.keys():
                    continue
                self.data[ln_parts[1].lower()] = index

    def lookup_index(self, word):
        res = self.data.get(word)
        return res
