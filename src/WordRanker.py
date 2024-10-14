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
                self.data[ln_parts[1]] = index

    def lookup_index(self, word):
        return self.data.get(word)
