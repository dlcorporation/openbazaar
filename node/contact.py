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

class Contact(object):
    """ Encapsulation for remote contact

    This class contains information on a single remote contact
    """
    def __init__(self, guid, uri, firstComm=0):
        self.guid = guid
        self.uri = uri
        # self._peerConnection = PeerConnection(uri, guid)
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
