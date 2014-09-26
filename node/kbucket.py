import logging

from six import string_types
import constants


class BucketFull(Exception):
    """Raised when the bucket is full."""
    pass


class KBucket(object):
    """FILLME"""

    def __init__(self, rangeMin, rangeMax, market_id=1):
        """
        Initialize a new KBucket with a range and a market_id.

        @param rangeMin: The lower boundary for the range in the 160-bit ID
                         space covered by this k-bucket
        @param rangeMax: The upper boundary for the range in the ID space
                         covered by this k-bucket
        @param market_id: FILLME
        """

        self.lastAccessed = 0
        self.rangeMin = rangeMin
        self.rangeMax = rangeMax
        self.contacts = []
        self.market_id = market_id

        self.log = logging.getLogger(
            '[%s] %s' % (market_id, self.__class__.__name__)
        )

    def __len__(self):
        return len(self.contacts)

    def addContact(self, contact):
        """
        Add a contact to the contact list.

        The new contact is always appended to the contact list after removing
        any prior occurences of the same contact.

        @param contact: The contact to add or a string containing the
                        contact's node ID
        @type contact: connection.CryptoPeerConnection or str

        @raise node.kbucket.BucketFull: The bucket is full and the contact
                                        to add is not already in it.
        """
        try:
            # Assume contact exists. Attempt to remove the old one...
            self.contacts.remove(contact)
            # ... and add the new one at the end of the list.
            self.contacts.append(contact)

            # The code above works as follows:
            # Assume C1 is the existing contact and C2 is the new contact.
            # Iff C1 is equal to C2, it will be removed from the list.
            # Since Contact.__eq__ compares only GUIDs, contact C1 will
            # be replaced even if it's not exactly the same as C2.
            # This is the intended behaviour; the fresh contact may have
            # updated add-on data (e.g. optimization-specific stuff).
        except ValueError:
            # The contact wasn't there after all, so add it.
            if len(self.contacts) < constants.k:
                self.contacts.append(contact)
            else:
                raise BucketFull('No space in bucket to insert contact')

    def getContact(self, contactID):
        """
        Return the contact with the specified ID or None if not present.

        @param contactID: The ID to search.
        @type contact: connection.CryptoPeerConnection or str

        @rtype: connection.CryptoPeerConnection or None
        """
        self.log.debug('[getContact] %s' % contactID)
        for contact in self.contacts:
            if contact == contactID:
                self.log.debug('[getContact] Found %s' % contact)
                return contact
        self.log.debug('[getContact] No Results')
        return None

    def getContacts(self, count=-1, excludeContact=None):
        """
        Return a list containing up to the first `count` number of contacts.

        @param count: The amount of contacts to return;
                      if 0 or less, return all contacts.
        @type count: int
        @param excludeContact: A contact to exclude; if this contact is in
                               the list of returned values, it will be
                               discarded before returning. If a C{str} is
                               passed as this argument, it must be the
                               contact's ID.
        @type excludeContact: connection.CryptoPeerConnection or str

        @return: The first `count` contacts in the contact list.
                 This amount is capped by the available contacts
                 and the bucket size, of course. If no contacts
                 are present, an empty list is returned.
        @rtype:  list of connection.CryptoPeerConnection
        """

        currentLen = len(self)
        if not currentLen:
            return []

        if count <= 0:
            count = currentLen
        else:
            count = min(count, currentLen)

        # Return no more contacts than bucket size.
        count = min(count, constants.k)

        contactList = self.contacts[:count]
        if excludeContact is not None:
            try:
                # NOTE: If the excludeContact is removed, the resulting
                # list has one less contact than expected. Not sure if
                # this is a bug.
                contactList.remove(excludeContact)
            except ValueError:
                self.log.debug(
                    '[kbucket.getContacts() warning] '
                    'tried to exclude non-existing contact '
                    '(%s)' % excludeContact
                )
        return contactList

    def removeContact(self, contact):
        """
        Remove given contact from contact list.

        @param contact: The contact to remove, or a string containing the
                        contact's node ID
        @type contact: connection.CryptoPeerConnection or str

        @raise ValueError: The specified contact is not in this bucket
        """
        self.contacts.remove(contact)

    def keyInRange(self, key):
        """
        Tests whether the specified key (i.e. node ID) is in the range
        of the 160-bit ID space covered by this k-bucket (in other words, it
        returns whether or not the specified key should be placed in this
        k-bucket)

        @param key: The key to test
        @type key: str or int

        @return: C{True} if key is in this k-bucket's range,
                 C{False} otherwise.
        @rtype: bool
        """
        if isinstance(key, string_types):
            key = long(key, 16)
        return self.rangeMin <= key < self.rangeMax
