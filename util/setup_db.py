#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net
import sqlite3
from os import path

DB_PATH = "db/ob.db"

# TODO: Move DB_PATH to constants file.
# TODO: Use actual foreign keys.
# TODO: Use indexes.
# TODO: Maybe it makes sense to put tags on a different table

if not path.isfile(DB_PATH):
    con = sqlite3.connect(DB_PATH)
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE markets(" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "key TEXT, " \
                    "value TEXT, " \
                    "lastPublished TEXT, " \
                    "originallyPublished TEXT, " \
                    "originallyPublisherID INT, " \
                    "secret TEXT)")

        cur.execute("CREATE TABLE contracts(" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "market_id INT, " \
                    "item_images TEXT, " \
                    "contract_body TEXT, " \
                    "signed_contract_body TEXT, " \
                    "unit_price INT, " \
                    "item_title TEXT, " \
                    "item_desc TEXT, " \
                    "item_condition TEXT, " \
                    "item_quantity_available, " \
                    "state TEXT, " \
                    "key TEXT)")

        cur.execute("CREATE TABLE products(" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "market_id INT, " \
                    "productTitle TEXT, "
                    "productDescription TEXT, " \
                    "productPrice INT, " \
                    "productShippingPrice TEXT, " \
                    "imageData BLOB, " \
                    "productQuantity INT, " \
                    "productTags TEXT, " \
                    "key TEXT)")

        cur.execute("CREATE TABLE orders(" \
                    "id INTEGER PRIMARY KEY " \
                    "AUTOINCREMENT, " \
                    "market_id INT, " \
                    "state TEXT, " \
                    "type TEXT, " \
                    "address TEXT, " \
                    "buyer TEXT, " \
                    "seller TEXT, " \
                    "note_for_merchant TEXT, " \
                    "escrows TEXT, " \
                    "text TEXT, " \
                    "contract_key TEXT, " \
                    "signed_contract_body TEXT, " \
                    "updated INT, " \
                    "created INT)")

        cur.execute("CREATE TABLE peers(" \
                    "id INTEGER PRIMARY KEY " \
                    "AUTOINCREMENT, " \
                    "uri TEXT, " \
                    "pubkey TEXT, " \
                    "nickname TEXT, " \
                    "market_id TEXT, " \
                    "guid TEXT, " \
                    "updated INT, " \
                    "created INT)")

        cur.execute("CREATE TABLE settings(" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "market_id INT, " \
                    "nickname TEXT, " \
                    "secret TEXT, " \
                    "sin TEXT, " \
                    "pubkey TEXT, " \
                    "guid TEXT, " \
                    "email TEXT, " \
                    "PGPPubKey TEXT, " \
                    "PGPPubkeyFingerprint TEXT, " \
                    "bcAddress TEXT, " \
                    "bitmessage TEXT, " \
                    "storeDescription TEXT, " \
                    "street1 TEXT, " \
                    "street2 TEXT, " \
                    "city TEXT, " \
                    "stateRegion TEXT, " \
                    "stateProvinceRegion TEXT, " \
                    "zip TEXT, " \
                    "country TEXT, " \
                    "countryCode TEXT, " \
                    "welcome TEXT, " \
                    "arbiter BOOLEAN, " \
                    "arbiterDescription TEXT, "\
                    "trustedArbiters TEXT, " \
                    "privkey TEXT, " \
                    "obelisk TEXT, " \
                    "notaries TEXT, " \
                    "notary BOOLEAN)")

        cur.execute("CREATE TABLE escrows(" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "order_id INT, " \
                    "address TEXT)")

        cur.execute("CREATE TABLE reviews(" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "pubKey TEXT, " \
                    "subject TEXT, " \
                    "signature TEXT, " \
                    "text TEXT, " \
                    "rating INT)")

        cur.execute("CREATE TABLE datastore(" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "market_id INT, " \
                    "key TEXT, " \
                    "lastPublished TEXT, " \
                    "originallyPublished TEXT, " \
                    "originalPublisherID TEXT, " \
                    "value TEXT)")
