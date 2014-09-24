#!/usr/bin/env python

from pysqlcipher import dbapi2 as sqlite
import sys

sys.path.append('node/')
import constants

DB_PATH = constants.DB_PATH


def upgrade(db_path):

    con = sqlite.connect(db_path)
    with con:
        cur = con.cursor()

        # Use PRAGMA key to encrypt / decrypt database.
        cur.execute("PRAGMA key = 'passphrase';")

        try:
            cur.execute("CREATE TABLE events("
                        "id INTEGER PRIMARY KEY "
                        "AUTOINCREMENT, "
                        "market_id TEXT, "
                        "event_id TEXT, "
                        "event_description TEXT, "
                        "updated INT, "
                        "created INT)")
            print 'Upgraded'
        except sqlite.Error as e:
            print 'Exception: %s' % e


def downgrade(db_path):

    con = sqlite.connect(db_path)
    with con:
        cur = con.cursor()

        # Use PRAGMA key to encrypt / decrypt database.
        cur.execute("PRAGMA key = 'passphrase';")
        cur.execute("DROP TABLE IF EXISTS events;")

        print 'Downgraded'

if __name__ == "__main__":

    if sys.argv[1:] is not None:
        DB_PATH = sys.argv[1:][0]
        if sys.argv[2:] is "downgrade":
            downgrade(DB_PATH)
        else:
            upgrade(DB_PATH)
