import unittest

from node import contact


class TestContact(unittest.TestCase):

    def test_init(self):
        guid, uri, firstComm = "42", "http://contact.io", 5
        c = contact.Contact(guid, uri, firstComm=firstComm)
        self.assertEqual(c.guid, guid)
        self.assertEqual(c.uri, uri)
        self.assertEqual(c.commTime, firstComm)
        self.assertEqual(c.failedRPCs, 0)

    def test_eq_hash(self):
        guid, uri = "42", "http://contact.io"
        a = contact.Contact(guid, uri)
        b = contact.Contact(guid, uri)
        c = contact.Contact(guid, "http://foo.io")
        d = a.guid
        e = guid

        self.assertIsNot(a, b, "Separate instantiations produce same objects.")

        self.assertEqual(a, b, "Unequal contacts with same initialization.")
        self.assertEqual(a, c, "Unequal contacts with same GUID.")
        self.assertEqual(a, d, "Contact unequal to own GUID.")
        self.assertEqual(a, e, "Contact unequal to same GUID.")

        alt_guid = "43"
        f = contact.Contact(alt_guid, uri)
        g = alt_guid

        self.assertNotEqual(a, f, "Equal contacts with different GUIDs.")
        self.assertNotEqual(a, g, "Contact equal to GUID different from own.")


if __name__ == "__main__":
    unittest.main()
