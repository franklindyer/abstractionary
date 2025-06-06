import random
from db_tools import *

class WordRanker:
    def __init__(self, con):
        self.con = con

    def lookup_index(self, word):
        res = db_get_rank(self.con, word)
        return res
