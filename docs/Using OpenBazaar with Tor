<img src="https://blog.openbazaar.org/wp-content/uploads/2014/07/logo.png" width="500px"/>
# Using OpenBazaar with Tor

These instructions are intended to serve as a guide to experimenting with OpenBazaar over the Tor network. In theory approach 2 (Onioncat) is also relevant to I2P using the Garlicat software. Once connection relaying/TURN support is built in to OpenBazaar and the ability to receive incoming connections directly is removed then operation in Tor will be simplified considerably.

## WARNING

Before you go any further please consider the following: OpenBazaar is pre-release software and MAY have bugs that could expose your local IP address or your routers public IP address to the OpenBazaar network. Please use it on an isolated machine if the above scenario could be a problem for you. 


## 1. Introduction

There are two methods for getting OpenBazaar working with Tor:

1. Proxychains - Using a socket hooking application called proxychains to redirect all OpenBazaar traffic through a Tor SOCKS proxy
2. Onioncat - Using an application called Onioncat to create an IPv6 TUN interface which is associated with a Tor Hidden Service and then running OpenBazaar

####Proxychains pro's
- Does not require root access to system
- Simpler of the two methods

####Proxychains con's
- Requires the creation of a hidden service (for current releases of OB)
- Does not work correctly yet - the advertised node URI needs to be the hidden services hostname

####Onioncat pro's
- Completely isolated from non Onioncat (thus non-Tor) systems
- Works now as incoming connections are supported

####Onioncat con's
- Requires the creation of a hidden service (for current releases of OB)
- Require creation of bi-directional Onioncat configuration which needs to be defended (firewalled etc)


## 2. PROXYCHAINS

1. Install the Proxychains package
2. Start OpenBazaar with :
` proxychains ./run.sh -j'

## 3. ONIONCAT

1. Create a hidden service for Onioncat
  - Configure as follows: Listen on port 8060. Redirect to 127.0.0.1:8060. 
  - Restart Tor and make a note of the hidden service hostname that is created for you.
2. Install the Onioncat package
3. Edit /etc/default/onioncat and ensure that the following configuration is present (where xxxyyyzzz.onion is the hidden service hostname from step 1<br/>`  ENABLED=yes`<br/>`  DAEMON_OPTS="-U -d 0 xxxyyyzzz.onion"`
4. Restart onioncat
5. Check that a new TUN interface configured with an IPv6 address has been created.
6. Configure your firewall to drop all inbound traffic on that interface except for port tcp/12345
7. Start OpenBazaar specifying your new IPv6 TUN address as follows :<br/>
` ./run.sh -j -i a:b:c:d:e:f:g:h`

