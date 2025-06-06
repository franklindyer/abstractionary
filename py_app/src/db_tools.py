import math
import random
import sqlite3
from multiprocessing.pool import ThreadPool

DB_READ_POOL = ThreadPool(processes=10)

def unpool_query(con, q, args):
    cur = con.cursor()
    res = cur.execute(q, args).fetchall()
    cur.close()
    return list(res)

def pool_query(con, q, args=()):
    res = DB_READ_POOL.apply(unpool_query, (con, q, args,))
    return res

def db_random_nonsense(con):
    return pool_query(con, "SELECT prompt FROM prompts INNER JOIN lists ON lists.id=prompts.list WHERE lists.name='nonsense' ORDER BY RANDOM() LIMIT 1")[0][0]

def db_get_rank(con, wd):
    res = pool_query(con, "SELECT rank FROM freqs WHERE lemma=?", (wd,))
    if len(res) == 0:
        return None
    else:
        return res[0][0] 

def db_word_cutoff(con, wd, cutoff):
    rank = db_get_rank(con, wd) 
    if rank <= cutoff:
        return db_random_nonsense(con)
    else:
        return wd

def db_random_prompts(con, topics, choices=3):
    sel_topics = [random.choice(topics) for i in range(choices)]
    prompts = [pool_query(con, "SELECT prompt FROM prompts INNER JOIN lists ON lists.id=prompts.list WHERE lists.name=? ORDER BY RANDOM() LIMIT ?", (t, choices,)) for t in sel_topics]
    prompts = [p[0][0] for p in prompts]
    return prompts

def db_topic_list(con):
    sel_topics = pool_query(con, "SELECT name FROM lists WHERE NOT name='nonsense'")
    return [r[0] for r in sel_topics]

def db_topic_titles(con):
    sel_topics = pool_query(con, "SELECT name, title FROM lists WHERE NOT name='nonsense'")
    return list(sel_topics) 
