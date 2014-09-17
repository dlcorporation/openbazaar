import unittest

from node import contact


class TestContact(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.guid = "42"
        cls.uri = "http://contact.io"

    def test_init(self):
        firstComm = 5
        c = contact.Contact(self.guid, self.uri, firstComm=firstComm)
        self.assertEqual(c.guid, self.guid)
        self.assertEqual(c.uri, self.uri)
        self.assertEqual(c.commTime, firstComm)
        self.assertEqual(c.failedRPCs, 0)

    def test_eq_hash(self):
        a = contact.Contact(self.guid, self.uri)
        b = contact.Contact(self.guid, self.uri)
        c = contact.Contact(self.guid, "http://foo.io")
        d = a.guid
        e = self.guid

        self.assertIsNot(a, b, "Separate instantiations produce same objects.")

        self.assertEqual(a, b, "Unequal contacts with same initialization.")
        self.assertEqual(a, c, "Unequal contacts with same GUID.")
        self.assertEqual(a, d, "Contact unequal to own GUID.")
        self.assertEqual(a, e, "Contact unequal to same GUID.")

        alt_guid = "43"
        f = contact.Contact(alt_guid, self.uri)
        g = alt_guid

        self.assertNotEqual(a, f, "Equal contacts with different GUIDs.")
        self.assertNotEqual(a, g, "Contact equal to GUID different from own.")

    def test_repr(self):
        c = contact.Contact(self.guid, self.uri)
        self.assertEqual(c.__repr__(), str(c))


if __name__ == "__main__":
    unittest.main()
