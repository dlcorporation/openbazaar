class Contact(object):
    """ Encapsulation for remote contact

    This class contains information on a single remote contact
    """
    def __init__(self, guid, uri, firstComm=0):
        self.guid = guid
        self.uri = uri
        #self._peerConnection = PeerConnection(uri, guid)
        self.commTime = firstComm
        self.failedRPCs = 0

    def __eq__(self, other):
        if isinstance(other, Contact):
            return self.guid == other.guid
        elif isinstance(other, str):
            return self.guid == other
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, Contact):
            return self.guid != other.guid
        elif isinstance(other, str):
            return self.guid != other
        else:
            return True

    def __str__(self):
        return '<%s.%s object; GUID: %s, URI: %s>' % (self.__module__, self.__class__.__name__, self.guid, self.uri)
