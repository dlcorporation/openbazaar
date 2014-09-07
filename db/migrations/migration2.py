#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net

from os import path, remove
from pysqlcipher import dbapi2 as sqlite
import sys

sys.path.append('node/')
import constants

DB_PATH = constants.DB_PATH

def upgrade(db_path):

    con = sqlite.connect(db_path)
    print db_path
    with con:
        cur = con.cursor()

        # Use PRAGMA key to encrypt / decrypt database.
        cur.execute("PRAGMA key = 'passphrase';")

        try:
            cur.execute("ALTER TABLE contracts "
                        "ADD COLUMN deleted INT DEFAULT 0")
            print 'Upgraded'
            con.commit()
        except:
            pass

def downgrade(db_path):

    con = sqlite.connect(db_path)
    with con:
        cur = con.cursor()

        # Use PRAGMA key to encrypt / decrypt database.
        cur.execute("PRAGMA key = 'passphrase';")

        cur.execute("ALTER TABLE contracts DROP COLUMN deleted")

        print 'Downgraded'
        con.commit()

if __name__ == "__main__":

    if sys.argv[1:] is not None:
        DB_PATH = sys.argv[1:][0]
        if sys.argv[2:] is "downgrade":
            downgrade(DB_PATH)
        else:
            upgrade(DB_PATH)
