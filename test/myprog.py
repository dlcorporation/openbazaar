import logging
import sys

def A(s):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger("MyProg.test_on_listing_results").setLevel(logging.DEBUG)
    logging.getLogger("MyProg.test_on_listing_results").debug('Listings %s', s)
    logging.getLogger("MyProg.test_on_listing_results").warn('Listings %s' % s)
