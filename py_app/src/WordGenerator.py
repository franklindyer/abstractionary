import random

from db_tools import *
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

class FileWordGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.words = self.get_wordlist()
 
    def get_wordlist(self):
        return [ln.lower().strip() for ln in open(self.filename, 'r').readlines()]

    def gen_word(self):
        return random.choice(self.words)

class DBWordGenerator:
    def __init__(self, cur, topic):
        self.cur = cur
        self.topic = topic

    def gen_word(self):
        choice = db_random_prompts(self.cur, [self.topic], choices=1)[0]
        return choice

def make_generator_map(con):
    topic_list = db_topic_list(con)
    generator_map = {}
    for t in topic_list:
        generator_map[t] = DBWordGenerator(con, t)
    return generator_map

class CombinedWordGenerator:
    def __init__(self, grouplist):
        self.gens = [grouplist[k] for k in grouplist]

    def gen_word(self):
        return random.choice(self.gens).gen_word()
