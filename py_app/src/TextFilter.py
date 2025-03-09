import math
import re

import nltk
from nltk.corpus import cmudict
nltk.download("cmudict")
cmudict_d = cmudict.dict()

from WordTranslator import TrivialTranslator

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
        for i, c in enumerate(s[len(pre):][::-1]):
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

    def set_target_phrases(self, target_phrases):
        self.blacklist = [wd.strip() for target_phrase in target_phrases for wd in target_phrase.split(' ')]

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

class MonosyllabicFilter:
    def __init__(self, word_ranker, word_translator):
        self.blacklist = []
        self.wr = word_ranker
        self.wt = word_translator     
        self.rank_bound = -1

    def set_difficulty(self, diff_string):
        return

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

    def num_sylls(self, wd):
        # hyphenated = self.hyphenator.inserted(wd)
        # return len(hyphenated.split('-'))
        return [len(list(y for y in x if y[-1].isdigit())) for x in cmudict_d[wd.lower()]][0] == 1 

    def translate_text(self, tokens):
        # print([tt.body for tt in tokens])
        return [TextToken(self.wt.translate(tt.body), pre=tt.pre, post=tt.post) 
                if (self.wr.lookup_index(tt.body) == None)
                or tt.body in self.blacklist
                or self.num_sylls(tt.body) > 1
                else tt 
                for tt in tokens]

    def reassemble_text(self, tokens):
        return ''.join([tt.combine() for tt in tokens])

def make_filter_of_type(filter_type, wr, wt):
    if filter_type in ["easy", "medium", "hard", "insane", "impossible"]:
        tf = TextFilter(wr, wt)
        tf.set_difficulty(filter_type)
        return tf
    elif filter_type == "caveman":
        return MonosyllabicFilter(wr, TrivialTranslator())
