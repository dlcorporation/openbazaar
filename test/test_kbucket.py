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