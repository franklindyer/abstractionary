import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = sqlite3.connect("./data/words.db")
con.row_factory = dict_factory
cur = con.cursor()

## Load up the listing of all available vocab lists
topics = [ln.strip().split('\t') for ln in open("./data/topics.txt").readlines() if len(ln) > 1]

## Get topic slugs and titles from topics file and load words from each topical list
for ln in topics:
    slug = ln[0]
    title = ln[1]
    cur.execute("INSERT INTO lists (name, title) VALUES (?, ?)", (slug, title,))
    id = cur.lastrowid

    words = [ln.strip().lower() for ln in open(f"./data/lists/{slug}.txt").readlines() if len(ln) > 1]
    for w in words:
        cur.execute("INSERT INTO prompts (prompt, list) VALUES (?, ?)", (w, id,)) 

## Get English frequency list and add words with their ranks
en_words = [ln.strip() for ln in open("./data/frequency/en.txt").readlines() if len(ln) > 1]
for i in range(len(en_words)):
    w = en_stem.stemWord(en_words[i])
    cur.execute("INSERT INTO freqs (lemma, rank) VALUES (?, ?)", (w, i+1,))

## Get nonsense words and add to database
nonsense_words = [ln.strip() for ln in open("./data/misc/nonsense.txt").readlines() if len(ln) > 1]
cur.execute("INSERT INTO lists (name, title) VALUES (?, ?)", ("nonsense", "Nonsense words",))
nonsense_id = cur.lastrowid
for w in nonsense_words:
    cur.execute("INSERT INTO prompts (prompt, list) VALUES (?, ?)", (w, nonsense_id,))

con.commit()
con.close()
