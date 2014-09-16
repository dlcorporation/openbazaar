import unittest

from pybitcointools import main

from node import arithmetic


class TestArithmetic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.privkey_hex = (
            "e9873d79c6d87dc0fb6a5778633389f4453213303da61f20bd67fc233aa33262"
        )

    def test_privtopub(self):
        pubkey_hex1 = arithmetic.privtopub(self.privkey_hex)
        pubkey_hex2 = main.privkey_to_pubkey(self.privkey_hex)

        self.assertEqual(pubkey_hex1, pubkey_hex2)

    def test_changebase(self):
        pubkey_hex = arithmetic.privtopub(self.privkey_hex)
        pubkey_bin1 = main.changebase(pubkey_hex, 16, 256)
        pubkey_bin2 = arithmetic.changebase(pubkey_hex, 16, 256)

        self.assertEqual(pubkey_bin1, pubkey_bin2)


if __name__ == "__main__":
    unittest.main()
