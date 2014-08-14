import miniupnpc

class PortMapper(object):
    '''
    UPnP Port Mapping tool, so we don't need to manually forward ports on a router.
    
    Ideally we'd use a random port within a range of about 1000 possible ports.
    Ideally we'd delete the mapping when we shutdown OpenBazaar but that might not be the case.
    
    Support port mapping for TCP and UDP ports.
    
    Created on Aug 14, 2014
    @author: gubatron
    '''
    DEBUG = False # boolean
    upnp = None  # miniupnpc.UPnP
    OPEN_BAZAAR_DESCRIPTION='OpenBazaar Server'
    
    def debug(self,*s):
        if PortMapper.DEBUG:
            print str(s)

    def debugUpnpValues(self):
        self.debug('discoverdelay', self.upnp.discoverdelay)
        self.debug('lanaddr', self.upnp.lanaddr)
        self.debug('multicastif', self.upnp.multicastif)
        self.debug('minissdpdsocket', self.upnp.minissdpdsocket)
        
    def debugAddresses(self):
        self.debug('local ip address :', self.upnp.lanaddr)
        self.debug('external ip address :', self.upnp.externalipaddress())

    def __init__(self):
        '''
        Constructor
        '''
        self.upnp = miniupnpc.UPnP()
        
        self.debug('inital(default) values :')
        self.debugUpnpValues()
        self.upnp.discoverdelay = 200;
        self.debug('Discovering... delay=%ums' % self.upnp.discoverdelay)
        self.debug(self.upnp.discover(), 'device(s) detected')

        try:
            self.upnp.selectigd()
        except Exception, e:
            print 'Exception :', e
            import sys
            sys.exit(1)

        # display information about the IGD and the internet connection
        self.debugAddresses()
        self.debug("Status Info:", self.getStatusInfo())
        self.debug("Connection Type:",self.getConnectionType())
        self.debugUpnpValues()
        
    def getStatusInfo(self):
        return self.upnp.statusinfo()
    
    def getConnectionType(self):
        return self.upnp.connectiontype()
    
    def addPortMapping(self, externalPort, internalPort, protocol='TCP', ipToBind=None):
        '''
        Valid protocol values are: 'TCP', 'UDP'
        Usually you'll pass externalPort and internalPort as the same number.
        '''
        if protocol not in ('TCP','UDP'):
            raise Exception('PortMapper.addPortMapping() invalid protocol exception \''+str(protocol)+'\'')
        
        if ipToBind==None:
            ipToBind = self.upnp.lanaddr
            self.debug("INFO: addPortMapping() -> No alternate ipToBind address passed, using default lan address (", self.upnp.lanaddr,")")
        
        result = self.upnp.addportmapping(externalPort,
                                          protocol,
                                          ipToBind,
                                          internalPort,
                                          PortMapper.OPEN_BAZAAR_DESCRIPTION + ' ('+protocol+')',
                                          '')
        self.debug("addPortMapping?:", result)
        return result
    
    def deletePortMapping(self, port, protocol='TCP'):
        result = False
        try:
            result = self.upnp.deleteportmapping(port, protocol)
            self.debug("PortMapper.deletePortMapping(%d,%s):" % (port, protocol))
            self.debug(result)
        except:
            self.debug("Could not delete mapping on port",port,"protocol",protocol)
        return result
    
    def getMappingList(self):
        ''' Returns -> [PortMappingEntry]'''
        i = 0
        mappings = []
        while True:
            p = self.upnp.getgenericportmapping(i)
            if p==None:
                break
            (port, proto, (ihost,iport), desc, c, d, e) = p
            mapping = PortMappingEntry(port, proto, ihost, iport,desc,e)
            self.debug("port:",port, desc, ihost,"iport:", iport, "c",c,"d",d,"e",e)
            i = i + 1
            mappings.append(mapping) 
        return mappings
    
    def cleanMyMappings(self):
        '''Delete previous OpenBazaar UPnP Port mappings if found.'''
        mappings = mapper.getMappingList()
        for m in mappings:
            if m.description.startswith(PortMapper.OPEN_BAZAAR_DESCRIPTION):
                self.debug('Found:',str(m))
                self.deletePortMapping(m.port)
                self.deletePortMapping(m.internalPort)


class PortMappingEntry:
    '''POPO to represent a port mapping entry, tuples are evil when used for abstractions'''
    def __init__(self, port, protocol, internalHost, internalPort, description, expiration):
        self.port = port
        self.protocol = protocol
        self.internalHost = internalHost
        self.internalPort = internalPort
        self.description = description
        self.expiration = expiration
        
    def __str__(self):
        return '{ protocol:'+self.protocol+ \
               ', description:'+self.description+ \
               ', port:'+str(self.port)+ \
               ', internalPort:'+str(self.internalPort)+ \
               ', internalHost:'+self.internalHost+ \
               ', expiration:'+str(self.expiration)+ \
               '}'
    
if __name__=='__main__':
    #Test code
    PortMapper.DEBUG=True
    mapper = PortMapper()
    print "Adding mapping: External:12345, Internal:8888"
    mapper.addPortMapping(12345,8888,'TCP')
    mappings = mapper.getMappingList()
    print len(mappings),"mappings"
    
    mapper.cleanMyMappings()
    
    print "---- after deleting the mapping"
    mappings = mapper.getMappingList()
    print len(mappings),"mappings"
    
    print mapper.debugUpnpValues()
