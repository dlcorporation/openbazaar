import random
import unittest

from node import constants, kbucket


class AbstractGUID(object):
    def __init__(self, guid, address):
        self.guid = guid
        self.address = address

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.guid == other.guid
        elif isinstance(other, str):
            return self.guid == other
        return False


class TestKbucket(unittest.TestCase):

    @staticmethod
    def _mk_contact_by_num(i):
        return AbstractGUID(str(i), 'http://foo/%d' % i)

    @classmethod
    def setUpClass(cls):
        cls.range_min = 1
        cls.range_max = cls.range_min + 16 * constants.k

        cls.market_id = 42
        cls.default_market_id = 1

        cls.init_contact_count = constants.k - 1

        cls.ghost_contact_id = 0
        cls.ghost_contact = cls._mk_contact_by_num(cls.ghost_contact_id)

    @classmethod
    def _make_kbucket(cls, count=None):
        if count is None:
            count = cls.init_contact_count

        new_kbucket = kbucket.KBucket(
            cls.range_min,
            cls.range_max,
            market_id=cls.market_id
        )

        for i in range(cls.range_min, cls.range_min + count):
            new_kbucket.addContact(cls._mk_contact_by_num(i))

        return new_kbucket

    def setUp(self):
        self.bucket = self._make_kbucket()

    def test_init(self):
        k = kbucket.KBucket(1, 2)
        self.assertEqual(k.lastAccessed, 0)
        self.assertEqual(k.rangeMin, 1)
        self.assertEqual(k.rangeMax, 2)
        self.assertEqual(k.market_id, self.default_market_id)
        self.assertEqual(k.contacts, [])
        self.assertTrue(hasattr(k, 'log'))

        k = kbucket.KBucket(3, 4, market_id=self.market_id)
        self.assertEqual(k.market_id, self.market_id)

    def test_len(self):
        len_self = len(self.bucket)
        len_contacts = len(self.bucket.getContacts())
        self.assertEqual(
            len_self,
            len_contacts,
            "Discrepancy in contact list length: Reported %d\tActual: %d" % (
                len_self,
                len_contacts
            )
        )

    def testAddContact_new(self):
        new_id = self.range_min + self.init_contact_count
        new_contact = self._mk_contact_by_num(new_id)
        prev_count = len(self.bucket.getContacts())

        try:
            self.bucket.addContact(new_contact)
        except kbucket.BucketFull:
            self.fail("Failed to add new contact in non-full bucket.")
            return

        # Assert new contact appears at end of contact list.
        self.assertEqual(
            self.bucket.contacts[-1],
            new_contact,
            "New contact is not at end of list"
        )

        # Naively assert the list didn't lose an element by accident.
        cur_count = len(self.bucket.getContacts())
        self.assertEqual(
            prev_count + 1,
            cur_count,
            "Expected list length: %d\tGot: %d\tInitial: %d" % (
                prev_count + 1,
                cur_count,
                prev_count
            )
        )

    def testAddContact_existing(self):
        new_id = self.range_min
        new_contact = self._mk_contact_by_num(new_id)
        prev_count = len(self.bucket.getContacts())

        try:
            self.bucket.addContact(new_contact)
        except kbucket.BucketFull:
            self.fail("Failed to add existing contact in non-full bucket.")
            return

        # Assert new contact appears at end of contact list.
        self.assertEqual(
            self.bucket.contacts[-1],
            new_contact,
            "New contact is not at end of list"
        )

        # Assert the list didn't change size.
        cur_count = len(self.bucket.getContacts())
        self.assertEqual(
            prev_count,
            cur_count,
            "Expected list length: %d\tGot: %d\tInitial: %d" % (
                prev_count,
                cur_count,
                prev_count
            )
        )

    def testAddContact_full(self):
        self.assertEqual(
            len(self.bucket.getContacts()),
            constants.k - 1,
            "Bucket is not full enough."
        )

        # Adding just one more is OK ...
        new_id1 = self.range_max - 1
        new_contact1 = self._mk_contact_by_num(new_id1)
        try:
            self.bucket.addContact(new_contact1)
        except kbucket.BucketFull:
            self.fail("Bucket burst earlier than expected.")
            return

        # ... but adding one more will force a split
        prev_list = self.bucket.getContacts()
        new_id2 = self.range_max - 2
        new_contact2 = self._mk_contact_by_num(new_id2)

        with self.assertRaises(kbucket.BucketFull):
            self.bucket.addContact(new_contact2)

        # Assert list is intact despite exception.
        cur_list = self.bucket.getContacts()
        self.assertEqual(
            prev_list,
            cur_list,
            "Contact list was modified before raising exception."
        )

    def testGetContact(self):
        for i in range(self.init_contact_count):
            c_id = self.range_min + i
            self.assertEqual(
                self.bucket.getContact(str(c_id)),
                self._mk_contact_by_num(c_id),
                "Did not find requested contact %d." % c_id
            )

        # Assert None is returned upon requesting nonexistent contact.
        self.assertIsNone(
            self.bucket.getContact(self.ghost_contact_id),
            "Nonexistent contact found."
        )

    def _test_GetContact_scenario(self, count_expected, count=-1, bucket=None):
        if bucket is None:
            bucket = self.bucket

        contacts = bucket.getContacts(count=count)
        count_contacts = len(contacts)

        self.assertEqual(
            count_expected,
            count_contacts,
            "Expected contact list size: %d\tGot: %d" % (
                count_expected,
                count_contacts
            )
        )

    def testGetContacts_empty(self):
        empty_bucket = self._make_kbucket(count=0)
        self._test_GetContact_scenario(0, bucket=empty_bucket)

    def testGetContacts_default(self):
        count = self.init_contact_count
        self._test_GetContact_scenario(count, count)

    def testGetContacts_count(self):
        count = self.init_contact_count // 2
        self._test_GetContact_scenario(count, count)

    def testGetContacts_available(self):
        count = self.init_contact_count + 1
        self._test_GetContact_scenario(self.init_contact_count, count)

    def testGetContacts_exclude(self):
        all_contacts = self.bucket.getContacts()
        count_all = len(all_contacts)

        # Pick a random contact and exclude it ...
        target_contact_offset = random.randrange(0, self.init_contact_count)
        target_contact_id = self.range_min + target_contact_offset
        excl_contact = self._mk_contact_by_num(target_contact_id)
        rest_contacts = self.bucket.getContacts(excludeContact=excl_contact)
        count_rest = len(rest_contacts)

        # ... check it was indeed excluded ...
        self.assertNotIn(
            excl_contact,
            rest_contacts,
            "getContacts() did not exclude the contact we asked for"
        )

        # ... naively ensure no other contact was excluded ...
        self.assertEqual(
            self.init_contact_count - 1,
            count_rest,
            "Expected contact list size: %d\tGot: %d\tInitial: %d" % (
                self.init_contact_count,
                count_rest,
                count_all
            )
        )

        # ... and the original list is not affected ...
        self.assertEqual(
            self.init_contact_count,
            count_all,
            "Original list was modified by exclusion."
        )

        # ... and check it's OK to exclude a contact that is not there yet.
        try:
            self.bucket.getContacts(excludeContact=self.ghost_contact)
        except Exception:
            self.fail("Crashed while excluding contact absent from bucket.")

    def testRemoveContact_existing_contact(self):
        rm_contact = self._mk_contact_by_num(self.range_min)
        prev_count = len(self.bucket.getContacts())

        try:
            self.bucket.removeContact(rm_contact)
        except ValueError:
            self.fail("Crashed while removing existing contact.")
            return

        cur_count = len(self.bucket.getContacts())
        self.assertEqual(
            prev_count - 1,
            cur_count,
            "Expected contact list size: %d\tGot: %d\tInitial: %d" % (
                prev_count - 1,
                cur_count,
                prev_count,
            )
        )

    def testRemoveContact_existing_guid(self):
        rm_guid = str(self.range_min)
        prev_count = len(self.bucket.getContacts())

        try:
            self.bucket.removeContact(rm_guid)
        except ValueError:
            self.fail("Crashed while removing existing contact via GUID.")
            return

        cur_count = len(self.bucket.getContacts())
        self.assertEqual(
            prev_count - 1,
            cur_count,
            "Expected contact list size: %d\tGot: %d\tInitial: %d" % (
                prev_count - 1,
                cur_count,
                prev_count,
            )
        )

    def testRemoveContact_absent(self):
        prev_list = self.bucket.getContacts()

        with self.assertRaises(ValueError):
            self.bucket.removeContact(self.ghost_contact)

        cur_list = self.bucket.getContacts()
        self.assertEqual(
            prev_list,
            cur_list,
            "Contact list was modified before raising exception."
        )

    def testkeyInRange(self):
        self.assertTrue(self.bucket.keyInRange(self.range_min))
        self.assertTrue(self.bucket.keyInRange(self.range_max - 1))

        mid_key = self.range_min + (self.range_max - self.range_min) // 2
        self.assertTrue(self.bucket.keyInRange(mid_key))
        self.assertTrue(self.bucket.keyInRange(hex(mid_key)))

        self.assertFalse(self.bucket.keyInRange(self.range_min - 1))
        self.assertFalse(self.bucket.keyInRange(self.range_max))


if __name__ == "__main__":
    unittest.main()
