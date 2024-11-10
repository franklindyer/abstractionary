import gensim
import gensim.downloader
from gensim.models import Word2Vec
import math
import re

class TextToken:
    def __init__(self, body, pre="", post=""):
        self.body = body
        self.pre = pre
        self.post = post

    def combine(self):
        return self.pre + self.body + self.post

    def from_str(s):
        pre = ""
        post = ""
        enum_s = enumerate(s)
        for i, c in enumerate(s):
            if c.isalnum():
                break
            pre = pre + c
        for i, c in enumerate(s[::-1]):
            if c.isalnum():
                break
            post = c + post
        return TextToken(s[len(pre):(len(s)-len(post))], pre=pre, post=post)

difficulty_map = {
    "easy": 2000,
    "medium": 1500,
    "hard": 1000,
    "insane": 300,
    "impossible": 100,
    "default": 2000
}

class TextFilter:
    def __init__(self, word_ranker, word_translator):
        self.wr = word_ranker
        self.blacklist = []
        self.wt = word_translator        
        self.rank_bound = -1

    def set_difficulty(self, diff_string):
        self.rank_bound = difficulty_map.get(diff_string)
        if self.rank_bound == None:
            self.rank_bound = difficulty_map["default"]

    def set_target_phrase(self, target_phrase):
        self.blacklist = [wd.strip() for wd in target_phrase.split(' ')]

    def filter(self, txt):
        return self.reassemble_text(self.translate_text(self.tokenize_text(txt)))

    def tokenize_text(self, txt):
        txt_split = re.split(r"(\s+)", txt.strip()) + [""]
        i = 0
        tokens = []
        next_word = ""
        for w in txt_split:
            if i % 2 == 0:
                next_word = w.lower()
            else:
                next_tok = TextToken.from_str(next_word + w)
                tokens = tokens + [next_tok]
            i += 1 
        return tokens

    def translate_text(self, tokens):
        # print([tt.body for tt in tokens])
        return [TextToken(self.wt.translate(tt.body), pre=tt.pre, post=tt.post) 
                if (self.wr.lookup_index(tt.body) or math.inf) > self.rank_bound
                or tt.body in self.blacklist
                else tt 
                for tt in tokens]

    def reassemble_text(self, tokens):
        return ''.join([tt.combine() for tt in tokens])

vector_sim_map = {
    "easy": 0.2,
    "medium": 0,
    "hard": -0.1,
    "insane": -0.3,
    "impossible": -0.5,
    "default": 0.2
}

# dataset = gensim.downloader.load("text8")
# VECTOR_MODEL = Word2Vec(dataset)

class VectorTextFilter(TextFilter):
    def __init__(self, word_translator):
        self.blacklist = []
        self.target_word = None
        self.wt = word_translator
        self.vector_bound = -1
        self.model = VECTOR_MODEL

    def set_difficulty(self, diff_string):
        self.vector_bound = vector_sim_map.get(diff_string)
        if self.vector_bound == None:
            self.vector_bound = vector_sim_map["default"]
    
    def set_target_phrase(self, target_phrase):
        self.blacklist = [wd.strip() for wd in target_phrase.split(' ')]
    
    def translate_text(self, tokens):
        tokens = [tt for tt in tokens if tt.body in self.model.wv.key_to_index]
        return [TextToken(self.wt.translate(tt.body), pre=tt.pre, post=tt.post) 
                if tt.body in self.blacklist
                or any([self.model.wv.similarity(tt.body, k) > self.vector_bound for k in self.blacklist])
                else tt 
                for tt in tokens]
