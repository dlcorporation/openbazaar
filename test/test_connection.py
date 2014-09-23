import unittest

import mock

from node import connection


class TestPeerConnection(unittest.TestCase):

    @staticmethod
    def _mk_address(protocol, hostname, port):
        return "%s://%s:%s" % (protocol, hostname, port)

    @classmethod
    def setUpClass(cls):
        cls.protocol = "tcp"
        cls.hostname = "crypto.io"
        cls.port = 54321
        cls.address = cls._mk_address(cls.protocol, cls.hostname, cls.port)
        cls.nickname = "OpenBazaar LightYear"
        cls.responses_received = {}
        cls.pub = "YELLOW SUBMARINE"
        cls.timeout = 10
        cls.transport = mock.Mock()

        cls.default_nickname = ""

    def setUp(self):
        self.pc1 = connection.PeerConnection(self.transport, self.address)
        self.pc2 = connection.PeerConnection(
            self.transport,
            self.address,
            self.nickname
        )

    def test_init(self):
        self.assertEqual(self.pc1.timeout, self.timeout)
        self.assertEqual(self.pc1.transport, self.transport)
        self.assertEqual(self.pc1.address, self.address)
        self.assertEqual(self.pc1.nickname, self.default_nickname)
        self.assertEqual(self.pc1.responses_received, self.responses_received)
        self.assertIsNotNone(self.pc1.ctx)

        self.assertEqual(self.pc2.nickname, self.nickname)


class TestCryptoPeerConnection(TestPeerConnection):

    @classmethod
    def setUpClass(cls):
        super(TestCryptoPeerConnection, cls).setUpClass()
        cls.guid = "42"
        cls.pub = "YELLOW SUBMARINE"
        cls.sin = "It's a sin"

        cls.default_guid = None
        cls.default_pub = None
        cls.default_sin = None

    @classmethod
    def _mk_default_CPC(cls):
        return connection.CryptoPeerConnection(
            cls.transport,
            cls.address,
        )

    @classmethod
    def _mk_complete_CPC(cls):
        return connection.CryptoPeerConnection(
            cls.transport,
            cls.address,
            cls.pub,
            cls.guid,
            cls.nickname,
            cls.sin,
        )

    def setUp(self):
        self.pc1 = self._mk_default_CPC()
        self.pc2 = self._mk_complete_CPC()

    def test_init(self):
        super(TestCryptoPeerConnection, self).test_init()

        self.assertEqual(self.pc1.ip, self.hostname)
        self.assertEqual(self.pc1.port, self.port)
        self.assertEqual(self.pc1.address, self.address)

        self.assertEqual(self.pc1.pub, self.default_pub)
        self.assertEqual(self.pc1.sin, self.default_sin)
        self.assertEqual(self.pc1.guid, self.default_guid)

        self.assertEqual(self.pc2.pub, self.pub)
        self.assertEqual(self.pc2.guid, self.guid)
        self.assertEqual(self.pc2.sin, self.sin)

    def test_eq(self):
        self.assertEqual(self.pc1, self._mk_default_CPC())

        other_addresses = (
            self._mk_address("http", self.hostname, self.port),
            self._mk_address(self.protocol, "openbazaar.org", self.port),
            self._mk_address(self.protocol, self.hostname, 8080)
        )
        for address in other_addresses:
            self.assertEqual(
                self.pc1,
                connection.CryptoPeerConnection(
                    self.transport,
                    address
                )
            )

        self.assertNotEqual(self.pc1, None)

        self.assertEqual(self.pc2, self._mk_complete_CPC())
        self.assertEqual(self.pc2, self.guid)

        another_guid = "43"
        self.assertNotEqual(
            self.pc2,
            connection.CryptoPeerConnection(
                self.transport,
                self.address,
                self.pub,
                another_guid,
                self.nickname,
                self.sin
            )
        )
        self.assertNotEqual(self.pc1, int(self.guid))

    @unittest.skip(
        "Comparing CryptoPeerConnection with default GUID"
        "to default GUID fails."
    )
    def test_eq_regression_none(self):
        self.assertEqual(self.pc1, self.default_guid)

    def test_repr(self):
        self.assertEqual(self.pc2.__repr__(), str(self.pc2))


if __name__ == "__main__":
    unittest.main()
