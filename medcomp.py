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
    n = 0
    for record in by_id.itervalues():
        for (p, v) in prefixes(record):
            if not pd.has_key(p):
                pd[p] = set()
            pd[p].add(v)
        n += 1
        if not n % 1000:
            print n

    end_t = time.time()
    logging.info("Computed prefixes in %.2f seconds" % (end_t - start_t))

    start_t = time.time()
    logging.info("Writing prefixes to SQLite...")

    pds = sqlitedict.SqliteDict(SQLITE_DB, table="prefixes")
    pds.begin()
    pds.update(pd)
    pds.commit()
    end_t = time.time()
    logging.info("Wrote prefixes to SQLite in %.2f seconds" % (end_t - start_t))

def prefixes(record):
    p = []
    for (field, val) in record.iteritems():
        if field == "id":
            continue
        if val is not None:
            tokens = re.split("[^0-9a-z]", val.lower())
            for s in tokens:
                if not s:
                    continue
                for i in xrange(len(s) - 1):
                    prefix = s[:i + 1]
                    p.append((prefix, (record["id"], False)))
                p.append((s, (record["id"], True)))
    return p
