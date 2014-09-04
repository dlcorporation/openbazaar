#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net
import os
import sys
import unittest

# Add root directory of the project to our path in order to import db_store
dir_of_executable = os.path.dirname(__file__)
path_to_project_root = os.path.abspath(os.path.join(dir_of_executable, '..'))
sys.path.insert(0, path_to_project_root)
from node.db_store import Obdb
from node.setup_db import setup_db

TEST_DB_PATH = "test/test_ob.db"


def setUpModule():
    # Create a test db.
    if not os.path.isfile(TEST_DB_PATH):
        print "Creating test db: %s" % TEST_DB_PATH
        setup_db(TEST_DB_PATH)


def tearDownModule():
    # Cleanup.
    print "Cleaning up."
    print os.remove(TEST_DB_PATH)


class TestDbOperations(unittest.TestCase):
    def test_insert_select_operations(self):

        # Initialize our db instance
        db = Obdb(TEST_DB_PATH)

        # Create a dictionary of a random review
        review_to_store = {"pubKey": "123",
                           "subject": "A review",
                           "signature": "a signature",
                           "text": "Very happy to be a customer.",
                           "rating": 10}

        # Use the insert operation to add it to the db
        db.insertEntry("reviews", review_to_store)

        # Try to retrieve the record we just added based on the pubkey
        retrieved_review = db.selectEntries("reviews", {"pubkey": "123"})

        # The above statement will return a list with all the
        # retrieved records as dictionaries
        self.assertEqual(len(retrieved_review), 1)
        retrieved_review = retrieved_review[0]

        # Is the retrieved record the same as the one we added before?
        self.assertEqual(
            review_to_store["pubKey"],
            retrieved_review["pubKey"],
        )
        self.assertEqual(
            review_to_store["subject"],
            retrieved_review["subject"],
        )
        self.assertEqual(
            review_to_store["signature"],
            retrieved_review["signature"],
        )
        self.assertEqual(
            review_to_store["text"],
            retrieved_review["text"],
        )
        self.assertEqual(
            review_to_store["rating"],
            retrieved_review["rating"],
        )

        # Let's do it again with a malicious review.
        review_to_store = {"pubKey": "321",
                           "subject": "Devil''''s review",
                           "signature": "quotes\"\"\"\'\'\'",
                           "text": 'Very """"happy"""""" to be a customer.',
                           "rating": 10}

        # Use the insert operation to add it to the db
        db.insertEntry("reviews", review_to_store)

        # Try to retrieve the record we just added based on the pubkey
        retrieved_review = db.selectEntries("reviews", {"pubkey": "321"})

        # The above statement will return a list with all the
        # retrieved records as dictionaries
        self.assertEqual(len(retrieved_review), 1)
        retrieved_review = retrieved_review[0]

        # Is the retrieved record the same as the one we added before?
        self.assertEqual(
            review_to_store["pubKey"],
            retrieved_review["pubKey"],
        )
        self.assertEqual(
            review_to_store["subject"],
            retrieved_review["subject"],
        )
        self.assertEqual(
            review_to_store["signature"],
            retrieved_review["signature"],
        )
        self.assertEqual(
            review_to_store["text"],
            retrieved_review["text"],
        )
        self.assertEqual(
            review_to_store["rating"],
            retrieved_review["rating"],
        )

        # By ommiting the second parameter, we are retrieving all reviews
        all_reviews = db.selectEntries("reviews")
        self.assertEqual(len(all_reviews), 2)

    def test_update_operation(self):

        # Initialize our db instance
        db = Obdb(TEST_DB_PATH)

        # Retrieve the record with pubkey equal to '123'
        retrieved_review = db.selectEntries("reviews", {"pubkey": "321"})[0]

        # Check that the rating is still '10' as expected
        self.assertEqual(retrieved_review["rating"], 10)

        # Update the record with pubkey equal to '123'
        # and lower its rating to 9
        db.updateEntries("reviews", {"pubkey": "123"}, {"rating": 9})

        # Retrieve the same record again
        retrieved_review = db.selectEntries("reviews", {"pubkey": "123"})[0]

        # Test that the rating has been updated succesfully
        self.assertEqual(retrieved_review["rating"], 9)

    def test_delete_operation(self):

        # Initialize our db instance
        db = Obdb(TEST_DB_PATH)

        # Delete the entry with pubkey equal to '123'
        db.deleteEntries("reviews", {"pubkey": "123"})

        # Looking for this record with will bring nothing
        retrieved_review = db.selectEntries("reviews", {"pubkey": "123"})
        self.assertEqual(len(retrieved_review), 0)

if __name__ == '__main__':
    # Run tests.
    unittest.main()
