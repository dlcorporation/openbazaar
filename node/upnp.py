import miniupnpc


class PortMapper(object):
    '''
    UPnP Port Mapping tool, so we don't need to manually forward ports on a
    router.

    Ideally we'd use a random port within a range of about 1000 possible ports.
    Ideally we'd delete the mapping when we shutdown OpenBazaar but that might
    not be the case.

    Support port mapping for TCP and UDP ports.

    Created on Aug 14, 2014
    @author: gubatron
    '''
    DEBUG = False  # boolean
    upnp = None  # miniupnpc.UPnP
    OPEN_BAZAAR_DESCRIPTION = 'OpenBazaar Server'
    UPNP_DEVICE_AVAILABLE = False

    def debug(self, *s):
        if PortMapper.DEBUG:
            print str(s)

    def debug_upnp_values(self):
        self.debug('discoverdelay', self.upnp.discoverdelay)
        self.debug('lanaddr', self.upnp.lanaddr)
        self.debug('multicastif', self.upnp.multicastif)
        self.debug('minissdpdsocket', self.upnp.minissdpdsocket)

    def debug_addresses(self):
        self.debug('local ip address :', self.upnp.lanaddr)
        self.debug('external ip address :', self.upnp.externalipaddress())

    def __init__(self):
        '''
        Constructor
        '''
        self.upnp = miniupnpc.UPnP()

        self.debug('inital(default) values :')
        self.debug_upnp_values()
        self.upnp.discoverdelay = 200
        self.debug('Discovering... delay=%ums' % self.upnp.discoverdelay)
        self.debug(self.upnp.discover(), 'device(s) detected')

        try:
            self.upnp.selectigd()
            self.UPNP_DEVICE_AVAILABLE = True
        except Exception, e:
            print 'Exception :', e
            self.UPNP_DEVICE_AVAILABLE = False
            return

        # display information about the IGD and the internet connection
        self.debug_addresses()
        self.debug("Status Info:", self.get_status_info())
        self.debug("Connection Type:", self.get_connection_type())
        self.debug_upnp_values()

    def get_status_info(self):
        return self.upnp.statusinfo()

    def get_connection_type(self):
        return self.upnp.connectiontype()

    def add_port_mapping(self, externalPort, internalPort,
                         protocol='TCP', ipToBind=None):
        '''
        Valid protocol values are: 'TCP', 'UDP'
        Usually you'll pass externalPort and internalPort as the same number.
        '''
        result = False

        if self.UPNP_DEVICE_AVAILABLE:
            if protocol not in ('TCP', 'UDP'):
                raise Exception(
                    'PortMapper.add_port_mapping() invalid protocol ' +
                    'exception \'%s\'' %
                    str(protocol)
                )

            if ipToBind is None:
                ipToBind = self.upnp.lanaddr
                self.debug(
                    "INFO: add_port_mapping() -> No alternate ipToBind " +
                    "address passed, using default lan address (",
                    self.upnp.lanaddr, ")"
                )

            try:
                result = self.upnp.addportmapping(
                    externalPort,
                    protocol,
                    ipToBind,
                    internalPort,
                    PortMapper.OPEN_BAZAAR_DESCRIPTION + ' (' + protocol + ')',
                    ''
                )
            except:
                #ConflictInMappingEntry
                result = False

            self.debug("add_port_mapping(%s)?:" % str(externalPort), result)
        return result

    def delete_port_mapping(self, port, protocol='TCP'):
        result = False

        if self.UPNP_DEVICE_AVAILABLE:
            try:
                result = self.upnp.deleteportmapping(port, protocol)
                self.debug(
                    "PortMapper.delete_port_mapping(%d, %s):" % (port, protocol)
                )
                self.debug(result)
            except:
                self.debug(
                    "Could not delete mapping on port",
                    port,
                    "protocol",
                    protocol
                )

        return result

    def get_mapping_list(self):
        ''' Returns -> [PortMappingEntry]'''
        mappings = []

        if self.UPNP_DEVICE_AVAILABLE:
            i = 0
            while True:
                p = self.upnp.getgenericportmapping(i)
                if p is None:
                    break
                port, proto, (ihost, iport), desc, c, d, e = p
                mapping = PortMappingEntry(port, proto, ihost, iport, desc, e)
                self.debug(
                    "port:", port,
                    desc, ihost,
                    "iport:", iport,
                    "c", c,
                    "d", d,
                    "e", e
                )
                i = i + 1
                mappings.append(mapping)

        return mappings

    def clean_my_mappings(self):
        if self.UPNP_DEVICE_AVAILABLE:
            '''Delete previous OpenBazaar UPnP Port mappings if found.'''
            mappings = self.get_mapping_list()
            for m in mappings:
                if m.description.startswith(PortMapper.OPEN_BAZAAR_DESCRIPTION):
                    self.debug('delete_port_mapping -> Found:', str(m))
                    try:
                        self.delete_port_mapping(m.port)
                    except:
                        pass


class PortMappingEntry:
    '''POPO to represent a port mapping entry, tuples are evil when
       used for abstractions'''
    def __init__(self, port, protocol, internalHost, internalPort,
                 description, expiration):
        self.port = port
        self.protocol = protocol
        self.internalHost = internalHost
        self.internalPort = internalPort
        self.description = description
        self.expiration = expiration

    def __str__(self):
        return '{ protocol:' + self.protocol + \
               ', description: ' + self.description + \
               ', port: ' + str(self.port) + \
               ', internalPort: ' + str(self.internalPort) + \
               ', internalHost: ' + self.internalHost + \
               ', expiration: ' + str(self.expiration) + \
               '}'

if __name__ == '__main__':
    #Test code
    PortMapper.DEBUG = True
    mapper = PortMapper()
    print "Adding mapping: External:12345, Internal:8888"
    mapper.add_port_mapping(12345, 8888, 'TCP')
    mappings = mapper.get_mapping_list()
    print len(mappings), "mappings"

    mapper.clean_my_mappings()

    print "---- after deleting the mapping"
    mappings = mapper.get_mapping_list()
    print len(mappings), "mappings"

    print mapper.debug_upnp_values()
