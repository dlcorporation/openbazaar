#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net

import UserDict
import logging
import ast


class DataStore(UserDict.DictMixin):
    """ Interface for classes implementing physical storage (for data
    published via the "STORE" RPC) for the Kademlia DHT

    @note: This provides an interface for a dict-like object
    """
    def keys(self):
        """ Return a list of the keys in this data store """

    def lastPublished(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was last published """

    def originalPublisherID(self, key):
        """ Get the original publisher of the data's node ID

        @param key: The key that identifies the stored data
        @type key: str

        @return: Return the node ID of the original publisher of the
        C{(key, value)} pair identified by C{key}.
        """

    def originalPublishTime(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was originally published """

    def setItem(self, key, value, lastPublished, originallyPublished, originalPublisherID, market_id):
        """ Set the value of the (key, value) pair identified by C{key};
        this should set the "last published" value for the (key, value)
        pair to the current time
        """

    def __getitem__(self, key):
        """ Get the value identified by C{key} """

    def __setitem__(self, key, value):
        """ Convenience wrapper to C{setItem}; this accepts a tuple in the
        format: (value, lastPublished, originallyPublished, originalPublisherID) """
        self.setItem(key, *value)

    def __delitem__(self, key):
        """ Delete the specified key (and its value) """


class DictDataStore(DataStore):
    """ A datastore using an in-memory Python dictionary """
    def __init__(self):
        # Dictionary format:
        # { <key>: (<value>, <lastPublished>, <originallyPublished> <originalPublisherID>) }
        self._dict = {}
        self._log = logging.getLogger(self.__class__.__name__)

    def keys(self):
        """ Return a list of the keys in this data store """
        return self._dict.keys()

    def lastPublished(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was last published """
        return self._dict[key][1]

    def originalPublisherID(self, key):
        """ Get the original publisher of the data's node ID

        @param key: The key that identifies the stored data
        @type key: str

        @return: Return the node ID of the original publisher of the
        C{(key, value)} pair identified by C{key}.
        """
        return self._dict[key][3]

    def originalPublishTime(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was originally published """
        return self._dict[key][2]

    def setItem(self, key, value, lastPublished, originallyPublished, originalPublisherID, market_id):
        """ Set the value of the (key, value) pair identified by C{key};
        this should set the "last published" value for the (key, value)
        pair to the current time
        """
        print 'Here is the key: %s' % key
        self._dict[key] = (value, lastPublished, originallyPublished, originalPublisherID)

    def __getitem__(self, key):
        """ Get the value identified by C{key} """
        return self._dict[key][0]

    def __delitem__(self, key):
        """ Delete the specified key (and its value) """
        del self._dict[key]


class MongoDataStore(DataStore):
    """ Example of a MongoDB database-based datastore
    """
    def __init__(self, db_connection):
        self._db = db_connection
        self._log = logging.getLogger(self.__class__.__name__)

    def keys(self):
        """ Return a list of the keys in this data store """
        keys = []
        try:
            db_keys = self._db.selectEntries("datastore")

            for row in db_keys:
                keys.append(row['key'].decode('hex'))

        finally:
            # self._log.info('Keys: %s' % keys)
            return keys

    def lastPublished(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was last published """
        return int(self._dbQuery(key, 'lastPublished'))

    def originalPublisherID(self, key):
        """ Get the original publisher of the data's node ID

        @param key: The key that identifies the stored data
        @type key: str

        @return: Return the node ID of the original publisher of the
        C{(key, value)} pair identified by C{key}.
        """
        return self._dbQuery(key, 'originalPublisherID')

    def originalPublishTime(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was originally published """
        return int(self._dbQuery(key, 'originallyPublished'))

    def setItem(self, key, value, lastPublished, originallyPublished, originalPublisherID, market_id=1):

        rows = self._db.selectEntries("datastore", "key = '%s' and market_id = '%s'" % (key, market_id.replace("'", "''")))
        if len(rows) == 0:
            # FIXME: Wrap text.
            self._db.insertEntry("datastore", {'key': key, 'market_id': market_id, 'key': key, 'value': value, 'lastPublished': lastPublished, 'originallyPublished': originallyPublished, 'originalPublisherID': originalPublisherID, 'market_id': market_id})
        else:
            self._db.updateEntries("datastore", {'key': key, 'market_id': market_id}, {'key': key, 'value': value, 'lastPublished': lastPublished, 'originallyPublished': originallyPublished, 'originalPublisherID': originalPublisherID, 'market_id': market_id})

        # if self._cursor.fetchone() == None:
        #     self._cursor.execute('INSERT INTO data(key, value, lastPublished, originallyPublished, originalPublisherID) VALUES (?, ?, ?, ?, ?)', (encodedKey, buffer(pickle.dumps(value, pickle.HIGHEST_PROTOCOL)), lastPublished, originallyPublished, originalPublisherID))
        # else:
        #     self._cursor.execute('UPDATE data SET value=?, lastPublished=?, originallyPublished=?, originalPublisherID=? WHERE key=?', (buffer(pickle.dumps(value, pickle.HIGHEST_PROTOCOL)), lastPublished, originallyPublished, originalPublisherID, encodedKey))

    def _dbQuery(self, key, columnName):
        row = self._db.selectEntries("datastore", "key = '%s'" % key.replace("'", "''"))

        if len(row) != 0:
            value = row[0][columnName]
            try:
                value = ast.literal_eval(value)
            except:
                pass
            return value

    def __getitem__(self, key):
        return self._dbQuery(key, 'value')

    def __delitem__(self, key):
        self._db.deleteEntries("datastore", {"key": key.encode("hex")})


class SqliteDataStore(DataStore):
    """ Sqlite database-based datastore
    """
    def __init__(self, db_connection):
        self._db = db_connection
        self._log = logging.getLogger(self.__class__.__name__)

    def keys(self):
        """ Return a list of the keys in this data store """
        keys = []
        try:
            db_keys = self._db.selectEntries("datastore")

            for row in db_keys:
                keys.append(row['key'].decode('hex'))

        finally:
            # self._log.info('Keys: %s' % keys)
            return keys

    def lastPublished(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was last published """
        return int(self._dbQuery(key, 'lastPublished'))

    def originalPublisherID(self, key):
        """ Get the original publisher of the data's node ID

        @param key: The key that identifies the stored data
        @type key: str

        @return: Return the node ID of the original publisher of the
        C{(key, value)} pair identified by C{key}.
        """
        return self._dbQuery(key, 'originalPublisherID')

    def originalPublishTime(self, key):
        """ Get the time the C{(key, value)} pair identified by C{key}
        was originally published """
        return int(self._dbQuery(key, 'originallyPublished'))

    def setItem(self, key, value, lastPublished, originallyPublished, originalPublisherID, market_id=1):

        rows = self._db.selectEntries("datastore", "key = '%s' and market_id = '%s'" % (key, market_id.replace("'", "''")))
        if len(rows) == 0:
            # FIXME: Wrap text.
            self._db.insertEntry("datastore", {'key': key, 'market_id': market_id, 'key': key, 'value': value, 'lastPublished': lastPublished, 'originallyPublished': originallyPublished, 'originalPublisherID': originalPublisherID, 'market_id': market_id})
        else:
            self._db.updateEntries("datastore", {'key': key, 'market_id': market_id}, {'key': key, 'value': value, 'lastPublished': lastPublished, 'originallyPublished': originallyPublished, 'originalPublisherID': originalPublisherID, 'market_id': market_id})

        # if self._cursor.fetchone() == None:
        #     self._cursor.execute('INSERT INTO data(key, value, lastPublished, originallyPublished, originalPublisherID) VALUES (?, ?, ?, ?, ?)', (encodedKey, buffer(pickle.dumps(value, pickle.HIGHEST_PROTOCOL)), lastPublished, originallyPublished, originalPublisherID))
        # else:
        #     self._cursor.execute('UPDATE data SET value=?, lastPublished=?, originallyPublished=?, originalPublisherID=? WHERE key=?', (buffer(pickle.dumps(value, pickle.HIGHEST_PROTOCOL)), lastPublished, originallyPublished, originalPublisherID, encodedKey))

    def _dbQuery(self, key, columnName):
        row = self._db.selectEntries("datastore", "key = '%s'" % key.replace("'", "''"))

        if len(row) != 0:
            value = row[0][columnName]
            try:
                value = ast.literal_eval(value)
            except:
                pass
            return value

    def __getitem__(self, key):
        return self._dbQuery(key, 'value')

    def __delitem__(self, key):
        self._db.deleteEntries("datastore", {"key": key.encode("hex")})
