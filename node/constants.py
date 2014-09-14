# ######## KADEMLIA CONSTANTS ###########

# Small number representing the degree of
# parallelism in network calls
alpha = 3

# Maximum number of contacts stored in a bucket
# NOTE: Should be an even number
k = 80

# Timeout for network operations
# [seconds]
rpcTimeout = 0.1

# Delay between iterations of iterative node lookups
# (for loose parallelism)
# [seconds]
iterativeLookupDelay = rpcTimeout / 2

# If a k-bucket has not been used for this amount of time, refresh it.
# [seconds]
refreshTimeout = 60 * 60 * 1000  # 1 hour

# The interval at which nodes replicate (republish/refresh)
# the data they hold
# [seconds]
replicateInterval = refreshTimeout

# The time it takes for data to expire in the network;
# the original publisher of the data  will also republish
# the data at this time if it is still valid
# [seconds]
dataExpireTimeout = 86400  # 24 hours

# ####### IMPLEMENTATION-SPECIFIC CONSTANTS ###########

# The interval in which the node should check whether any buckets
# need refreshing or whether any data needs to be republished
# [seconds]
checkRefreshInterval = refreshTimeout / 5

# Max size of a single UDP datagram.
# Any larger message will be spread accross several UDP packets.
# [bytes]
udpDatagramMaxSize = 8192  # 8 KB

DB_PATH = "db/ob.db"
