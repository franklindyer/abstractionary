import fileinput
import sys

sys.path.append("./src")

from TextFilter import *
from WordTranslator import *
from WordRanker import *

wr = WordRanker()
wr.ingest_data("data/eng_news_2023_10K-words.txt")
wt = FakeWordTranslator()
wt.ingest_data("data/refined_non_english_words.txt")
tf = TextFilter(wr, wt)
tf.rank_bound = 4000

for line in fileinput.input():
    print(tf.filter(line)) 
