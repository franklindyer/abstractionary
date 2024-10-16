import random

from WordRanker import *

class FreqWordGenerator:
    def __init__(self, word_ranker):
        self.wr = word_ranker
        self.lower_rank = 4000
        self.upper_rank = 6000

    def gen_word(self):
        word = None
        while word == None:
            n = random.randint(self.lower_rank, self.upper_rank)
            word = self.wr.lookup_word(n) 
        return word 
