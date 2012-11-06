import sqlite3
import re
import time
import logging

import MySQLdb

import sqlitedict

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = "rootpass"
MYSQL_PORT = 3306
MYSQL_DB = "elation"

SQLITE_DB_STR = "shareable_medication.db"
#SQLITE_DB_STR = ":memory:"
SQLITE_DB = sqlite3.connect(SQLITE_DB_STR)
SQLITE_BY_ID_TABLE = "shareable_medication_by_id"

_BY_ID = None

logging.basicConfig(level=logging.INFO)

def data_by_id():
    global _BY_ID
    if _BY_ID is None:
        _BY_ID = _data_from_mysql()
    return _BY_ID

def _data_from_mysql():

    # This may need to be refactored if there's a case where this
    # where all this data can't fit into memory at one time

    logging.info("Loading data from MySQL...")

    start_t = time.time()

    db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASS, port=MYSQL_PORT, db=MYSQL_DB)
    cursor = db.cursor()
    # {"genericName": "Amiodarone Hydrochloride", "strength": "200 mg", "displayName": "AMIODARONE 200 mg", "id": 4890951727, "brandName": "Amiodarone"}
    cursor.execute("SELECT id, displayName, brandName, genericName, strength FROM shareable_medication")
    by_id = {}
    for row in cursor.fetchall():
        by_id[row[0]] = {
            "id": row[0],
            "displayName": row[1],
            "brandName": row[2],
            "genericName": row[3],
            "strength": row[4],
        }

    end_t = time.time()

    logging.info("Loaded data from MySQL in %.2f seconds" % (end_t - start_t))


    return by_id

def load_into_sqlite():

    # Clear out old data if it exists since if medications are
    # removed, we want them to disappear and have MySQL be the
    # canonical source
    try:
        SQLITE_DB.execute("DROP TABLE `%s`" % SQLITE_BY_ID_TABLE)
    except sqlite3.OperationalError:
        # Table didn't exist
        pass

    # Update data by id
    by_id = data_by_id()

    logging.info("Loading data into SQLite...")
    start_t = time.time()

    d = sqlitedict.SqliteDict(SQLITE_DB, table=SQLITE_BY_ID_TABLE)
    d.begin()
    d.update(by_id)
    d.commit()
    end_t = time.time()
    logging.info("Loaded data into SQLite in %.2f seconds" % (end_t - start_t))

    start_t = time.time()
    logging.info("Computing prefixes and writing them to SQLite...")

    pd = {}
    td = {}
    n = 0
    for record in by_id.itervalues():
        (ps, ts) = prefixes_and_tokens(record)
        v = record["id"]
        for p in ps:
            if not pd.has_key(p):
                pd[p] = set()
            pd[p].add(v)
        for t in ts:
            if not td.has_key(t):
                td[t] = set()
            td[t].add(v)
        n += 1
        if not n % 10000:
            print n

    end_t = time.time()
    logging.info("Computed prefixes in %.2f seconds" % (end_t - start_t))

    start_t = time.time()
    logging.info("Writing prefixes to SQLite...")

    pds = sqlitedict.SqliteDict(SQLITE_DB, table="prefixes")
    tds = sqlitedict.SqliteDict(SQLITE_DB, table="tokens")
    pds.clear()
    pds.begin()
    pds.update(pd)
    pds.commit()
    tds.clear()
    tds.begin()
    tds.update(td)
    tds.commit()
    end_t = time.time()
    logging.info("Wrote prefixes to SQLite in %.2f seconds" % (end_t - start_t))

def tokenize(s):
    return re.split("[^0-9a-z]", s.lower())

def prefixes_and_tokens(record):
    p = []
    t = []
    for (field, val) in record.iteritems():
        if field == "id":
            continue
        if val is not None:
            tokens = tokenize(val)
            for s in tokens:
                if not s:
                    continue
                for i in xrange(len(s)):
                    prefix = s[:i + 1]
                    p.append(prefix)
                t.append(s)
    return (p, t)

BP = {}
_BP_LOADED = False
def _bp():
    if not _BP_LOADED:
        BP.update(sqlitedict.SqliteDict(SQLITE_DB, table="prefixes"))
    return BP

BI = {}
_BI_LOADED = False
def _bi():
    if not _BI_LOADED:
        BI.update(sqlitedict.SqliteDict(SQLITE_DB, table="shareable_medication_by_id"))
    return BI

def match(q, limit=None):
    results = []
    bp = sqlitedict.SqliteDict(SQLITE_DB, table="prefixes")
    bi = sqlitedict.SqliteDict(SQLITE_DB, table="shareable_medication_by_id")
    bt = sqlitedict.SqliteDict(SQLITE_DB, table="tokens")
    #bp = _bp()
    #bi = _bi()
    tokens = tokenize(q)
    for t in tokens[:-1]:
        # Skip tokens of length 1 because the list is too long
        # TODO: In the future, have a globally popular list of 
        # ~200 things for each letter to return instead of the 
        # overwhelmingly huge list that would be returned now
        if len(t) < 2:
            continue

        # Take the ones where the second part of the tuple is True
        # which means that the string matches a complete token, i.e.
        # "viagra" not "via" (which would just be the beginning of a string)
        results.append(bt[t])

    # For the last token, we take both partial tokens and complete tokens,
    # i.e. "via" and "viagra" both match something that has "viagra" in it
    # TODO: In the future, make it so its not always the last token that 
    # is partial but wherever the cursor is
    if len(tokens[-1]) >= 2:
        results.append(bp[tokens[-1]])

    if not results:
        results.append(set())

    rr1 = set.intersection(*results)

    # If the matching we've done doesn't have any hits, then
    # fallback to looking at the first things you type
    if not limit or len(rr1) < limit:
        r2 = []
        for t in tokens:
            if len(t) >= 2:
                r2.append(bp[t])
        if not r2:
            r2.append(set())
        rr2 = set.intersection(*r2)
        print "rr2=%r" % rr2
        rr2.difference_update(rr1)
    else:
        rr2 = set()

    rr = [bi[x] for x in rr1] + [bi[x] for x in rr2]
    if limit is None:
        return rr
    else:
        return rr[:limit]

