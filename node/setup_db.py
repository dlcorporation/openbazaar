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

import constants

DB_PATH = constants.DB_PATH

# TODO: Use indexes.
# TODO: Maybe it makes sense to put tags on a different table


def setup_db(db_path):
    if not path.isfile(db_path):
        con = sqlite.connect(db_path)
        with con:
            cur = con.cursor()

            # Use PRAGMA key to encrypt / decrypt database.
            cur.execute("PRAGMA key = 'passphrase';") # TODO: Get passphrase from user.

            cur.execute("CREATE TABLE markets("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "key TEXT, "
                        "value TEXT, "
                        "lastPublished TEXT, "
                        "originallyPublished TEXT, "
                        "originallyPublisherID INT, "
                        "secret TEXT)")

            cur.execute("CREATE TABLE contracts("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "market_id INT, "
                        "item_images TEXT, "
                        "contract_body TEXT, "
                        "signed_contract_body TEXT, "
                        "unit_price INT, "
                        "item_title TEXT, "
                        "item_desc TEXT, "
                        "item_condition TEXT, "
                        "item_quantity_available, "
                        "state TEXT, "
                        "key TEXT, "
                        "FOREIGN KEY(market_id) REFERENCES markets(id))")

            cur.execute("CREATE TABLE products("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "market_id INT, "
                        "productTitle TEXT, "
                        "productDescription TEXT, "
                        "productPrice INT, "
                        "productShippingPrice TEXT, "
                        "imageData BLOB, "
                        "productQuantity INT, "
                        "productTags TEXT, "
                        "key TEXT, "
                        "FOREIGN KEY(market_id) REFERENCES markets(id))")

            cur.execute("CREATE TABLE orders("
                        "id INTEGER PRIMARY KEY "
                        "AUTOINCREMENT, "
                        "order_id INT, "
                        "market_id INT, "
                        "state TEXT, "
                        "type TEXT, "
                        "item_price TEXT, "
                        "shipping_price TEXT, "
                        "address TEXT, "
                        "buyer_order_id TEXT, "
                        "notary TEXT, "
                        "payment_address TEXT, "
                        "shipping_address TEXT, "
                        "buyer TEXT, "
                        "merchant TEXT, "
                        "note_for_merchant TEXT, "
                        "escrows TEXT, "
                        "text TEXT, "
                        "contract_key TEXT, "
                        "signed_contract_body TEXT, "
                        "updated INT, "
                        "created INT, "
                        "FOREIGN KEY(market_id) REFERENCES markets(id))")

            cur.execute("CREATE TABLE peers("
                        "id INTEGER PRIMARY KEY "
                        "AUTOINCREMENT, "
                        "uri TEXT, "
                        "pubkey TEXT, "
                        "nickname TEXT, "
                        "market_id TEXT, "
                        "guid TEXT, "
                        "updated INT, "
                        "created INT)")
            # not sure if peers.market_id is actually supposed to be a TEXT
            # field or an INT with foreign key
            # referencing the markets(id)

            cur.execute("CREATE TABLE settings("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "market_id INT, "
                        "nickname TEXT, "
                        "secret TEXT, "
                        "sin TEXT, "
                        "pubkey TEXT, "
                        "guid TEXT, "
                        "email TEXT, "
                        "PGPPubKey TEXT, "
                        "PGPPubkeyFingerprint TEXT, "
                        "bcAddress TEXT, "
                        "bitmessage TEXT, "
                        "storeDescription TEXT, "
                        "street1 TEXT, "
                        "street2 TEXT, "
                        "city TEXT, "
                        "stateRegion TEXT, "
                        "stateProvinceRegion TEXT, "
                        "zip TEXT, "
                        "country TEXT, "
                        "countryCode TEXT, "
                        "welcome TEXT, "
                        "recipient_name TEXT, "
                        "arbiter BOOLEAN, "
                        "arbiterDescription TEXT, "
                        "trustedArbiters TEXT, "
                        "privkey TEXT, "
                        "obelisk TEXT, "
                        "notaries TEXT, "
                        "notary BOOLEAN, "
                        "FOREIGN KEY(market_id) REFERENCES markets(id))")

            cur.execute("CREATE TABLE escrows("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "order_id INT, "
                        "address TEXT, "
                        "FOREIGN KEY(order_id) REFERENCES orders(id))")

            cur.execute("CREATE TABLE reviews("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "pubKey TEXT, "
                        "subject TEXT, "
                        "signature TEXT, "
                        "text TEXT, "
                        "rating INT)")

            cur.execute("CREATE TABLE datastore("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "market_id INT, "
                        "key TEXT, "
                        "lastPublished TEXT, "
                        "originallyPublished TEXT, "
                        "originalPublisherID TEXT, "
                        "value TEXT, "
                        "FOREIGN KEY(market_id) REFERENCES markets(id))")


def remove_db(db_path):
    remove(db_path)

if __name__ == "__main__":
    if sys.argv[1:] is not None:
        DB_PATH = sys.argv[1:][0]

    print 'DB_PATH', DB_PATH
    setup_db(DB_PATH)
