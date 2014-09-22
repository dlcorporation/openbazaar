import unittest

#import market
import myprog
import StringIO
import sys
import logging


class TestMarket(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("TestMarket.test_on_listing_results")
        self.held, sys.stdout = sys.stdout, StringIO.StringIO()

    def test_on_listing_results(self):
        results = str('abc')
        self.log.debug('Listings %s' % results)
        self.log.debug("Listings %s", results)
        myprog.A(results)
        print "Listings %s" % results
        self.assertEqual(sys.stdout.getvalue().strip(), 'Listings abc')

    def tearDown(self):
        sys.stdout = self.held


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger("TestMarket.test_on_listing_results").setLevel(logging.DEBUG)
    logging.getLogger("TestMarket.test_on_listing_results").debug('Listings ')
    unittest.main()
