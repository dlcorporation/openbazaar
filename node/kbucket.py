import logging
from six import string_types
import constants


class BucketFull(Exception):
    """ Raised when the bucket is full """


class KBucket(object):
    """ Description - later
    """
    def __init__(self, rangeMin, rangeMax, market_id=1):
        """
        @param rangeMin: The lower boundary for the range in the 160-bit ID
                         space covered by this k-bucket
        @param rangeMax: The upper boundary for the range in the ID space
                         covered by this k-bucket
        """

        self.lastAccessed = 0
        self.rangeMin = rangeMin
        self.rangeMax = rangeMax
        self.contacts = list()

        self.log = logging.getLogger('[%s] %s' % (market_id, self.__class__.__name__))

    def addContact(self, contact):
        """ Add contact to _contact list in the right order. This will move the
        contact to the end of the k-bucket if it is already present.

        @raise kademlia.kbucket.BucketFull: Raised when the bucket is full and
                                            the contact isn't in the bucket
                                            already

        @param contact: The contact to add
        @type contact: p2p.PeerConnection
        """
        found = False

        for idx, old_contact in enumerate(self.contacts):
            if contact.guid == old_contact.guid:
                found = True
                foundId = idx
                break

        if found:
            # Move the existing contact to the end of the list
            # - using the new contact to allow add-on data (e.g. optimization-specific stuff) to be updated as well
            del self.contacts[foundId]
            self.contacts.append(contact)
        elif len(self.contacts) < constants.k:
            self.contacts.append(contact)
        else:
            raise BucketFull("No space in bucket to insert contact")

    def getContact(self, contactID):
        """ Get the contact specified node ID"""
        self.log.debug('[getContact] %s' % contactID)
        self.log.debug('contacts %s' % self.contacts)
        for contact in self.contacts:
            if contact.guid == contactID:
                self.log.debug('[getContact] Found %s' % contact)
                return contact
        self.log.debug('[getContact] No Results')

    def getContacts(self, count=-1, excludeContact=None):
        """ Returns a list containing up to the first count number of contacts

        @param count: The amount of contacts to return (if 0 or less, return
                      all contacts)
        @type count: int
        @param excludeContact: A contact to exclude; if this contact is in
                               the list of returned values, it will be
                               discarded before returning. If a C{str} is
                               passed as this argument, it must be the
                               contact's ID.
        @type excludeContact: kademlia.contact.Contact or str


        @raise IndexError: If the number of requested contacts is too large

        @return: Return up to the first count number of contacts in a list
                If no contacts are present an empty is returned
        @rtype: list
        """
        # Return all contacts in bucket
        if count <= 0:
            count = len(self.contacts)

        # Get current contact number
        currentLen = len(self.contacts)

        # If count greater than k - return only k contacts
        if count > constants.k:
            count = constants.k

        # Check if count value in range and,
        # if count number of contacts are available
        if not currentLen:
            contactList = list()

        # length of list less than requested amount
        elif currentLen < count:
            contactList = self.contacts[0:currentLen]
        # enough contacts in list
        else:
            contactList = self.contacts[0:count]

        if excludeContact in contactList:
            try:
                contactList.remove(excludeContact)
            except ValueError:
                print('[kbucket.getContacts() warning] tried to exclude non-existing contact (%s)' % str(excludeContact))
                self.log.debug('[kbucket.getContacts() warning] tried to exclude non-existing contact (%s)' % str(excludeContact))

        return contactList

    def removeContact(self, contact):
        """ Remove given contact from list

        @param contact: The contact to remove, or a string containing the
                        contact's node ID
        @type contact: kademlia.contact.Contact or str

        @raise ValueError: The specified contact is not in this bucket
        """
        self.log.debug('Contacts %s %s' % (contact, self.contacts))
        self.contacts = [x for x in self.contacts if x.guid != contact]
        self.log.debug('Contacts %s %s' % (contact, self.contacts))

    def keyInRange(self, key):
        """ Tests whether the specified key (i.e. node ID) is in the range
        of the 160-bit ID space covered by this k-bucket (in other words, it
        returns whether or not the specified key should be placed in this
        k-bucket)

        @param key: The key to test
        @type key: str or int

        @return: C{True} if the key is in this k-bucket's range, or C{False}
                 if not.
        @rtype: bool
        """
        if isinstance(key, string_types):
            key = long(key, 16)
        return self.rangeMin <= key < self.rangeMax

    def __len__(self):
        return len(self.contacts)
