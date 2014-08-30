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
        self._log = logging.getLogger('DB')

    def _connectToDb(self):
        """ Opens a db connection
        """
        self.con = sqlite.connect(self.db_path, detect_types=sqlite.PARSE_DECLTYPES)
        sqlite.register_adapter(bool, int)
        sqlite.register_converter("BOOLEAN", lambda v: bool(int(v)))
        self.con.row_factory = self._dictFactory

        # Use PRAGMA key to encrypt / decrypt database.
        cur = self.con.cursor()
        cur.execute("PRAGMA key = 'passphrase';") # TODO: Get passphrase from user.

    def _disconnectFromDb(self):
        """ Close the db connection
        """
        if self.con:
           self.con.close()
        self.con = False

    def _dictFactory(self, cursor, row):
        """ A factory that allows sqlite to return a dictionary instead of a tuple
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            if row[idx] == None:
                d[col[0]] = ""
            else:
                d[col[0]] = row[idx]
        return d

    def getOrCreate(self, table, where_clause, data_dict):
        """ This method attempts to grab the record first. If it fails to find it,
        it will create it.
        @param table: The table to search to
        @param get_where_dict: A dictionary with the WHERE/SET clauses
        """
        entries = self.selectEntries(table, where_clause)
        if len(entries) == 0:
            self.insertEntry(table, data_dict)
        return self.selectEntries(table, where_clause)[0]


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
            for key, value in set_dict.iteritems():
                key = str(key).replace("'", "''");

                if type(value) == bool:
                  value = 1 if value else 0
                else:
                  value = str(value).replace("'", "''");

                if first:
                    set_part = "%s = '%s'" % (key, value)
                    first = False
                else:
                    set_part = set_part + ", %s = '%s'" % (key, value)
            first = True
            for key, value in where_dict.iteritems():
                key = str(key).replace("'", "''");
                value = str(value).replace("'", "''");
                if first:
                    where_part = "%s = '%s'" % (key, value)
                    first = False
                else:
                    where_part = where_part + "%s %s = '%s'" % (operator, key, value)
            query = "UPDATE %s SET %s WHERE %s" \
                    % (table, set_part, where_part)
            self._log.debug('query: %s' % query)
            cur.execute(query)
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
            for key, value in update_dict.iteritems():
                key = str(key).replace("'", "''");

                if type(value) == bool:
                  value = 1 if value else 0
                else:
                  value = str(value).replace("'", "''");

                if first:
                    updatefield_part = "%s" % (key)
                    setfield_part = "'%s'" % (value)
                    first = False
                else:
                    updatefield_part = updatefield_part + ", %s" % (key)
                    setfield_part = setfield_part + ", '%s'" % (value)
            query = "INSERT INTO %s(%s) VALUES(%s)"  \
                    % (table, updatefield_part, setfield_part)
            cur.execute(query)
            lastrowid = cur.lastrowid
            self._log.debug("query: %s "% query)
        self._disconnectFromDb()
        if lastrowid:
            return lastrowid

    def selectEntries(self, table, where_clause="'1'='1'", order_field="id", order="ASC", limit=None, limit_offset=None, select_fields="*"):
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


            if limit != None and limit_offset is None:
                limit_clause = "LIMIT %s" % limit
            elif limit != None and limit_offset is not None:
                  limit_clause = "LIMIT %s %s %s" % (limit_offset, ",", limit)
            else:
                limit_clause = ""

            if select_fields is not "*":
                columns = ",".join(select_fields)
            else:
                columns = "*"

            query = "SELECT %s FROM %s WHERE %s ORDER BY %s %s %s" \
                    % (columns, table, where_clause, order_field, order, limit_clause)

            print query
            self._log.debug("query: %s "% query)
            cur.execute(query)
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
            for key, value in where_dict.iteritems():
                key = str(key).replace("'", "''");
                value = str(value).replace("'", "''");
                if first:
                    where_part = "%s = '%s'" % (key, value)
                    first = False
                else:
                    where_part = where_part + "%s %s = '%s'" % (operator, key, value)
            query = "DELETE FROM %s WHERE %s" \
                    % (table, where_part)
            self._log.debug('Query: %s' % query)
            cur.execute(query)
        self._disconnectFromDb()

    def numEntries(self, table, where_clause="'1'='1'"):
        self._connectToDb()
        with self.con:
            cur = self.con.cursor()
            first = True

            query = "SELECT count(*) as count FROM %s WHERE %s" \
                    % (table, where_clause)
            self._log.debug('query: %s' % query)
            cur.execute(query)
            rows = cur.fetchall()
        self._disconnectFromDb()


        return rows[0]['count']
