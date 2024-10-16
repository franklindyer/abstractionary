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

class FileWordGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.words = self.get_wordlist()
 
    def get_wordlist(self):
        return [ln.lower().strip() for ln in open(self.filename, 'r').readlines()]

    def gen_word(self):
        return random.choice(self.words)

abstract_generator = FileWordGenerator("data/ideas.txt")
celeb_generator = FileWordGenerator("data/celebrities.txt")
country_generator = FileWordGenerator("data/countries.txt")
food_generator = FileWordGenerator("data/foods.txt")
household_generator = FileWordGenerator("data/household.txt")
sex_generator = FileWordGenerator("data/sex.txt")

generator_map = {
    "abstract": abstract_generator,
    "countries": country_generator,
    "celebrities": celeb_generator,
    "foods": food_generator,
    "household": household_generator,
    "sex": sex_generator,
}

class CombinedWordGenerator:
    def __init__(self, grouplist):
        self.gens = [generator_map[k] for k in grouplist]

    def gen_word(self):
        return random.choice(self.gens).gen_word()
