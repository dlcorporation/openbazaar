"""
    This file is part of OpenBazaar.

    OpenBazaar is an open source project to create a decentralized network for
    commerce online that has no fees and cannot be censored.

    Copyright (C) 2014  The OpenBazaar Team

    OpenBazaar is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    OpenBazaar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest
from node.kbucket import KBucket
from node.contact import Contact

class Test(unittest.TestCase):


    def setUp(self):
        self.bucket = KBucket(1, 20, market_id=1)
        self.bucket.addContact(Contact(1, 'http://foo/1'))
        self.bucket.addContact(Contact(2, 'http://foo/2'))
        self.bucket.addContact(Contact(3, 'http://foo/3'))
        self.bucket.addContact(Contact(4, 'http://foo/4'))
        self.bucket.addContact(Contact(5, 'http://foo/5'))
        self.bucket.addContact(Contact(6, 'http://foo/6'))
        self.bucket.addContact(Contact(7, 'http://foo/7'))
        self.bucket.addContact(Contact(8, 'http://foo/8'))
        self.bucket.addContact(Contact(9, 'http://foo/9'))
        self.bucket.addContact(Contact(10, 'http://foo/10'))
        self.bucket.addContact(Contact(11, 'http://foo/11'))
        self.bucket.addContact(Contact(12, 'http://foo/12'))
        self.bucket.addContact(Contact(13, 'http://foo/13'))
        self.bucket.addContact(Contact(14, 'http://foo/14'))
        self.bucket.addContact(Contact(15, 'http://foo/15'))
        self.bucket.addContact(Contact(16, 'http://foo/16'))
        self.bucket.addContact(Contact(17, 'http://foo/17'))
        self.bucket.addContact(Contact(18, 'http://foo/18'))
        self.bucket.addContact(Contact(19, 'http://foo/19'))
        self.bucket.addContact(Contact(20, 'http://foo/20'))
        pass


    def tearDown(self):
        pass

    def testCantAddContacts(self):
        self.assertEqual(len(self.bucket.getContacts()), 20, "Unexpected contact count")
        pass

    def testGetContacts(self):
        allContacts = self.bucket.getContacts()
        self.assertEqual(len(allContacts), 20, "Unexpected contact count")
        
        #test it will exclude contact
        c18 = Contact(18, 'http://foo/18')
        excluding18 = self.bucket.getContacts(excludeContact=c18)
        
        #check size of contact list
        self.assertEqual(19, len(excluding18), "list size is not 19, should be 20")
        
        #check it did exclude the contact we asked
        self.assertEqual(True, c18 not in excluding18, "getContact() did not exclude the contact we asked for")
        
        #test it won't choke if I tell it to exclude a contact that is not there yet
        self.bucket.getContacts(excludeContact=Contact(21,'http://foo/21'))
        
        pass
    
    def testGetContact(self):
        c14 = Contact(14, 'http://foo/14')
        self.assertEqual(self.bucket.getContact(14), c14,"did not find requested contact.")

if __name__ == "__main__":
    unittest.main()