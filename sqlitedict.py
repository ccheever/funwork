import pickle
import marshal
import sqlite3
import UserDict

class SqliteDictError(Exception):
    pass

class SqliteDict(UserDict.DictMixin):

    def __init__(self, db=None, table="dict", keycol="key", valcol="value"):
        self.keycol = keycol
        self.valcol = valcol
        self.table = table
        if db is None:
            db = sqlite3.connect(":memory:")
        elif isinstance(db, basestring):
            self._dbstr = db
            db = sqlite3.connect(self._dbstr)
        self.db = db

        # Verify that tables and columns exist
        if not self.db.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", (self.table,)).fetchall():
            self.db.execute("CREATE TABLE `%s` (`%s` blob PRIMARY KEY, `%s` blob)" % (table, keycol, valcol))

    def keydumps(self, v):
        return v

    def keyloads(self, s):
        return s

    def valdumps(self, v):
        return buffer(marshal.dumps(v))

    def valloads(self, s):
        return marshal.loads(s)

    def __getitem__(self, key):
        c = self.db.execute("SELECT `%s` FROM `%s` WHERE `%s` = ?" % (self.valcol, self.table, self.keycol), (self.keydumps(key),))
        row = c.fetchone()
        if not row:
            raise KeyError(key)
        else:
            return self.valloads(row[0])

    def __setitem__(self, key, val):
        self.db.execute("INSERT OR REPLACE INTO `%s` (`%s`, `%s`) VALUES (?, ?)" % (self.table, self.keycol, self.valcol), (self.keydumps(key), self.valdumps(val)))

    def __delitem__(self, key):
        if not self.db.execute("DELETE FROM `%s` WHERE `%s` = ?" % (self.table, self.keycol), (self.keydumps(key),)).rowcount:
            raise KeyError(key)

    def keys(self):
        return [self.keyloads(x[0]) for x in self.db.execute("SELECT `%s` FROM `%s`" % (self.keycol, self.table)).fetchall()]

    def begin(self):
        self.db.execute("BEGIN TRANSACTION")

    def commit(self):
        self.db.commit()

