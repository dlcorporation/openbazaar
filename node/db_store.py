#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net

import logging
from pysqlcipher import dbapi2 as sqlite


class Obdb():
    """ Interface for db storage. Serves as segregation of the persistence layer
    and the application logic
    """
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = False
        self.log = logging.getLogger('DB')

    def _connectToDb(self):
        """ Opens a db connection
        """
        self.con = sqlite.connect(self.db_path, detect_types=sqlite.PARSE_DECLTYPES)
        sqlite.register_adapter(bool, int)
        sqlite.register_converter("bool", lambda v: bool(int(v)))
        self.con.row_factory = self._dictFactory

        # Use PRAGMA key to encrypt / decrypt database.
        cur = self.con.cursor()
        cur.execute("PRAGMA key = 'passphrase';")

    def _disconnectFromDb(self):
        """ Close the db connection
        """
        if self.con:
            try:
                self.con.close()
            except Exception:
                pass
        self.con = False

    def _dictFactory(self, cursor, row):
        """ A factory that allows sqlite to return a dictionary instead of a tuple
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            if row[idx] is None:
                d[col[0]] = ""
            else:
                d[col[0]] = row[idx]
        return d

    def _beforeStoring(self, value):
        """ Method called before executing SQL identifiers.
        """
        return unicode(value)

    def getOrCreate(self, table, where_dict, data_dict=False):
        """ This method attempts to grab the record first. If it fails to find it,
        it will create it.
        @param table: The table to search to
        @param get_where_dict: A dictionary with the WHERE/SET clauses
        """
        if not data_dict:
            data_dict = where_dict

        entries = self.selectEntries(table, where_dict)
        if len(entries) == 0:
            self.insertEntry(table, data_dict)
        return self.selectEntries(table, where_dict)[0]

    def updateEntries(self, table, where_dict, set_dict, operator="AND"):
        """ A wrapper for the SQL UPDATE operation
        @param table: The table to search to
        @param whereDict: A dictionary with the WHERE clauses
        @param setDict: A dictionary with the SET clauses
        """

        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            first = True
            sets = ()
            wheres = ()
            for key, value in set_dict.iteritems():
                if type(value) == bool:
                    value = bool(value)
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)

                sets = sets + (value, )
                if first:
                    set_part = "%s = ?" % (key)
                    first = False
                else:
                    set_part = set_part + ", %s = ?" % (key)
            first = True
            for key, value in where_dict.iteritems():
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                wheres = wheres + (value, )
                if first:
                    where_part = "%s = ?" % (key)
                    first = False
                else:
                    where_part = where_part + "%s %s = ?" % (operator, key)
            query = "UPDATE %s SET %s WHERE %s" \
                    % (table, set_part, where_part)
            self.log.debug('query: %s' % query)
            cur.execute(query, sets + wheres)
        self._disconnectFromDb()

    def insertEntry(self, table, update_dict):
        """ A wrapper for the SQL INSERT operation
        @param table: The table to search to
        @param updateDict: A dictionary with the values to set
        """
        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            first = True
            sets = ()
            for key, value in update_dict.iteritems():

                if type(value) == bool:
                    value = bool(value)
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                sets = sets + (value,)
                if first:
                    updatefield_part = "%s" % (key)
                    setfield_part = "?"
                    first = False
                else:
                    updatefield_part = updatefield_part + ", %s" % (key)
                    setfield_part = setfield_part + ", ?"
            query = "INSERT INTO %s(%s) VALUES(%s)"  \
                    % (table, updatefield_part, setfield_part)
            cur.execute(query, sets)
            lastrowid = cur.lastrowid
            self.log.debug("query: %s " % query)
        self._disconnectFromDb()
        if lastrowid:
            return lastrowid

    def selectEntries(self, table, where_dict={"\"1\"": "1"}, operator="AND", order_field="id", order="ASC", limit=None, limit_offset=None, select_fields="*"):
        """ A wrapper for the SQL SELECT operation. It will always return all the
            attributes for the selected rows.
        @param table: The table to search to
        @param whereDict: A dictionary with the WHERE clauses. If ommited it will
        return all the rows of the table
        """
        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            first = True
            wheres = ()
            for key, value in where_dict.iteritems():
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                wheres = wheres + (value, )
                if first:
                    where_part = "%s = ?" % (key)
                    first = False
                else:
                    where_part = where_part + "%s %s = ?" % (operator, key)

                if limit is not None and limit_offset is None:
                    limit_clause = "LIMIT %s" % limit
                elif limit is not None and limit_offset is not None:
                    limit_clause = "LIMIT %s %s %s" % (limit_offset, ",", limit)
                else:
                    limit_clause = ""

            query = "SELECT * FROM %s WHERE %s ORDER BY %s %s %s" \
                    % (table, where_part, order_field, order, limit_clause)
            self.log.debug("query: %s " % query)
            cur.execute(query, wheres)
            rows = cur.fetchall()
        self._disconnectFromDb()
        return rows

    def deleteEntries(self, table, where_dict={"\"1\"": "1"}, operator="AND"):
        """ A wrapper for the SQL DELETE operation. It will always return all the
            attributes for the selected rows.
        @param table: The table to search to
        @param whereDict: A dictionary with the WHERE clauses. If ommited it will
        delete all the rows of the table

        """

        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            first = True
            dels = ()
            for key, value in where_dict.iteritems():
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                dels = dels + (value, )
                if first:
                    where_part = "%s = ?" % (key)
                    first = False
                else:
                    where_part = where_part + "%s %s = ?" % (operator, key)
            query = "DELETE FROM %s WHERE %s" \
                    % (table, where_part)
            self.log.debug('Query: %s' % query)
            cur.execute(query, dels)
        self._disconnectFromDb()

    def numEntries(self, table, where_clause="'1'='1'"):
        self._connectToDb()
        with self.con:
            cur = self.con.cursor()

            query = "SELECT count(*) as count FROM %s WHERE %s" \
                    % (table, where_clause)
            self.log.debug('query: %s' % query)
            cur.execute(query)
            rows = cur.fetchall()
        self._disconnectFromDb()

        return rows[0]['count']
