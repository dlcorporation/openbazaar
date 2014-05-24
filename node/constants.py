######### KADEMLIA CONSTANTS ###########

#: Small number Representing the degree of parallelism in network calls
alpha = 3

#: Maximum number of contacts stored in a bucket; this should be an even number
k = 8

# Delay between iterations of iterative node lookups (for loose parallelism)  (in seconds)
iterativeLookupDelay = rpcTimeout / 2

#: If a k-bucket has not been used for this amount of time, refresh it (in seconds)
refreshTimeout = 3600 # 1 hour
#: The interval at which nodes replicate (republish/refresh) data they are holding
replicateInterval = refreshTimeout
# The time it takes for data to expire in the network; the original publisher of the data
# will also republish the data at this time if it is still valid
dataExpireTimeout = 86400 # 24 hours

######## IMPLEMENTATION-SPECIFIC CONSTANTS ###########

#: The interval in which the node should check its whether any buckets need refreshing,
#: or whether any data needs to be republished (in seconds)
checkRefreshInterval = refreshTimeout/5
