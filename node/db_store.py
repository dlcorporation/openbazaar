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


class Obdb(object):
    """ Interface for db storage. Serves as segregation of the persistence layer
    and the application logic
    """
    def __init__(self, db_path, disable_sqlite_crypt=False):
        self.db_path = db_path
        self.con = False
        self.log = logging.getLogger('DB')
        self.disable_sqlite_crypt = disable_sqlite_crypt

    def _connectToDb(self):
        """ Opens a db connection
        """
        self.con = sqlite.connect(
            self.db_path,
            detect_types=sqlite.PARSE_DECLTYPES,
            timeout=10
        )
        sqlite.register_adapter(bool, int)
        sqlite.register_converter("bool", lambda v: bool(int(v)))
        self.con.row_factory = self._dictFactory

        if not self.disable_sqlite_crypt:
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

    @staticmethod
    def _dictFactory(cursor, row):
        """ A factory that allows sqlite to return a dictionary instead of a tuple
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            if row[idx] is None:
                d[col[0]] = ""
            else:
                d[col[0]] = row[idx]
        return d

    @staticmethod
    def _beforeStoring(value):
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
            sets = []
            wheres = []
            where_part = []
            set_part = []
            for key, value in set_dict.iteritems():
                if type(value) == bool:
                    value = bool(value)
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                sets.append(value)
                set_part.append("%s = ?" % key)
            set_part = ",".join(set_part)
            for key, value in where_dict.iteritems():
                sign = "="
                if type(value) is dict:
                    sign = value["sign"]
                    value = value["value"]
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                wheres.append(value)
                where_part.append("%s %s ?" % (key, sign))
            operator = " " + operator + " "
            where_part = operator.join(where_part)
            query = "UPDATE %s SET %s WHERE %s" \
                    % (table, set_part, where_part)
            self.log.debug('query: %s' % query)
            cur.execute(query, tuple(sets + wheres))
        self._disconnectFromDb()

    def insertEntry(self, table, update_dict):
        """ A wrapper for the SQL INSERT operation
        @param table: The table to search to
        @param updateDict: A dictionary with the values to set
        """
        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            sets = []
            updatefield_part = []
            setfield_part = []
            for key, value in update_dict.iteritems():
                if type(value) == bool:
                    value = bool(value)
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                sets.append(value)
                updatefield_part.append(key)
                setfield_part.append("?")
            updatefield_part = ",".join(updatefield_part)
            setfield_part = ",".join(setfield_part)
            query = "INSERT INTO %s(%s) VALUES(%s)"  \
                    % (table, updatefield_part, setfield_part)
            cur.execute(query, tuple(sets))
            lastrowid = cur.lastrowid
            self.log.debug("query: %s " % query)
        self._disconnectFromDb()
        if lastrowid:
            return lastrowid

    def selectEntries(self, table, where_dict=None, operator="AND", order_field="id", order="ASC", limit=None, limit_offset=None, select_fields="*"):
        """
        A wrapper for the SQL SELECT operation. It will always return all the
        attributes for the selected rows.
        @param table: The table to search
        @param whereDict: A dictionary with the WHERE clauses.
                          If ommited it will return all the rows of the table.
        """
        if where_dict is None:
            where_dict = {"\"1\"": "1"}
        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            wheres = []
            where_part = []
            for key, value in where_dict.iteritems():
                sign = "="
                if type(value) is dict:
                    sign = value["sign"]
                    value = value["value"]
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                wheres.append(value)
                where_part.append("%s %s ?" % (key, sign))
                if limit is not None and limit_offset is None:
                    limit_clause = "LIMIT %s" % limit
                elif limit is not None and limit_offset is not None:
                    limit_clause = "LIMIT %s, %s" % (limit_offset, limit)
                else:
                    limit_clause = ""
            operator = " " + operator + " "
            where_part = operator.join(where_part)
            query = "SELECT * FROM %s WHERE %s ORDER BY %s %s %s" \
                    % (table, where_part, order_field, order, limit_clause)
            self.log.debug("query: %s " % query)
            cur.execute(query, tuple(wheres))
            rows = cur.fetchall()
        self._disconnectFromDb()
        return rows

    def deleteEntries(self, table, where_dict=None, operator="AND"):
        """
        A wrapper for the SQL DELETE operation. It will always return all the
        attributes for the selected rows.
        @param table: The table to search
        @param whereDict: A dictionary with the WHERE clauses.
                          If ommited it will delete all the rows of the table.
        """
        if where_dict is None:
            where_dict = {"\"1\"": "1"}

        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            dels = []
            where_part = []
            for key, value in where_dict.iteritems():
                sign = "="
                if type(value) is dict:
                    sign = value["sign"]
                    value = value["value"]
                key = self._beforeStoring(key)
                value = self._beforeStoring(value)
                dels.append(value)
                where_part.append("%s %s ?" % (key, sign))
            operator = " " + operator + " "
            where_part = operator.join(where_part)
            query = "DELETE FROM %s WHERE %s" \
                    % (table, where_part)
            self.log.debug('Query: %s' % query)
            cur.execute(query, dels)
        self._disconnectFromDb()
