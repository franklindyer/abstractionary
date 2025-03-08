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

uncommon_generator = FreqWordGenerator(googleWordRanker)
uncommon_generator.lower_rank = 5000
uncommon_generator.upper_rank = 9999

common_generator = FreqWordGenerator(googleWordRanker)
common_generator.lower_rank = 0
common_generator.upper_rank = 999

abstract_generator = FileWordGenerator("data/ideas.txt")
celeb_generator = FileWordGenerator("data/celebrities.txt")
country_generator = FileWordGenerator("data/countries.txt")
food_generator = FileWordGenerator("data/foods.txt")
household_generator = FileWordGenerator("data/household.txt")
location_generator = FileWordGenerator("data/locations.txt")
adjective_generator = FileWordGenerator("data/adjectives.txt")
sex_generator = FileWordGenerator("data/sex.txt")
google_generator = FileWordGenerator("data/google_searches.txt")
concrete_generator = FileWordGenerator("data/concreteness-ranking.txt")
concrete_generator.words = concrete_generator.words[5000:]
names_generator = FileWordGenerator("data/names.txt")
wiki_generator = FileWordGenerator("data/wikipedia.txt")

techno_generator = FileWordGenerator("data/techno.txt")
legal_generator = FileWordGenerator("data/legal.txt")
bio_generator = FileWordGenerator("data/biology.txt")
art_generator = FileWordGenerator("data/art.txt")
money_generator = FileWordGenerator("data/money.txt")
engineer_generator = FileWordGenerator("data/engineer.txt")
adult_generator = FileWordGenerator("data/adulting.txt")

generator_map = {
    "uncommon": uncommon_generator,
    "common": common_generator,
    "abstract": abstract_generator,
    "countries": country_generator,
    "celebrities": celeb_generator,
    "foods": food_generator,
    "household": household_generator,
    "locations": location_generator,
    "adjectives": adjective_generator,
    "sex": sex_generator,
    "googles": google_generator,
    "concrete": concrete_generator,
    "names": names_generator,
    "wikipedia": wiki_generator,

    "techno": techno_generator,
    "legal": legal_generator,
    "biology": bio_generator,
    "art": art_generator,
    "money": money_generator,
    "engineer": engineer_generator,
    "adulting": adult_generator,
}

class CombinedWordGenerator:
    def __init__(self, grouplist):
        self.gens = [generator_map[k] for k in grouplist]

    def gen_word(self):
        return random.choice(self.gens).gen_word()
