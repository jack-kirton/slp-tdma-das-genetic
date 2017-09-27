from __future__ import division, print_function

import sqlite3
import types

try:
    import cPickle as pickle
except:
    import pickle

from pyevolve.DBAdapters import DBBaseAdapter
from pyevolve.Statistics import Statistics

from ga import genome

class SQLite3Adapter(DBBaseAdapter, object):
    def __init__(self, dbname='evolution.db', id="", resetDB=False, frequency=1, commit_freq=100):
        super(SQLite3Adapter, self).__init__(frequency, id)
        self._frequency = frequency
        self._identify = id
        self._dbname = dbname
        self._resetDB = resetDB
        self._commit_freq = commit_freq

        self._connection = None
        self._cursor = None

    def close(self):
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        self._connection.close()

    def commit(self):
        self._connection.commit()

    def commitAndClose(self):
        self.commit()
        self.close()

    def createStructure(self, stats):
        c = self.getCursor()

        create_stat = "CREATE TABLE IF NOT EXISTS statistics (id TEXT, generation INT, "
        for k, v in stats.items():
            create_stat += "{} {}, ".format(k, "REAL")
        create_stat = create_stat[:-2] + ")"
        c.execute(create_stat)

        create_best = "CREATE TABLE IF NOT EXISTS best_individuals (id TEXT, generation INT, slots INT, genome BLOB)"
        c.execute(create_best)
        self.commit()

    def resetStructure(self, stats):
        c = self.getCursor()
        c.execute("DROP TABLE IF EXISTS statistics")
        c.execute("DROP TABLE IF EXISTS best_individuals")
        self.commit()
        self.createStructure(stats)

    def resetTableIdentify(self):
        c = self.getCursor()
        delete_stat = "DELETE FROM statistics WHERE id=?"
        c.execute(delete_stat, (self.getIdentify(),))
        delete_best = "DELETE FROM best_individuals WHERE id=?"
        c.execute(delete_best, (self.getIdentify(),))
        self.commit()

    def getCursor(self):
        if self._cursor == None:
            self._cursor = self._connection.cursor()
        return self._cursor

    def insert(self, ga_engine):
        stats = ga_engine.getStatistics()
        population = ga_engine.getPopulation()
        generation = ga_engine.getCurrentGeneration()

        c = self.getCursor()
        insert_stat = "INSERT INTO statistics VALUES (?, ?, "
        for i in xrange(len(stats)):
            insert_stat += "?, "
        insert_stat = insert_stat[:-2] + ")"
        c.execute(insert_stat, (self.getIdentify(), generation) + stats.asTuple())

        insert_best = "INSERT INTO best_individuals VALUES(?, ?, ?, ?)"
        bin_data = pickle.dumps(ga_engine.bestIndividual(), protocol=2)
        c.execute(insert_best, (self.getIdentify(), generation, genome.get_slots_used(ga_engine.bestIndividual()), sqlite3.Binary(bin_data)))

        if (generation % self._commit_freq == 0):
            self.commit()

    def open(self, ga_engine):
        self._connection = sqlite3.connect(self._dbname)
        if self._resetDB:
            self.resetStructure(Statistics())
        else:
            self.createStructure(Statistics())
        self.resetTableIdentify()


def sqlite_retrieve_best_genome(dbname, id):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    retrieve_query = "SELECT id, generation, slots, genome FROM best_individuals WHERE id=? ORDER BY generation DESC"

    c.execute(retrieve_query, (id,))
    row = c.fetchone()
    g = pickle.loads(str(row[3]))
    conn.close()
    return g, int(row[1]) + 1, int(row[2])

