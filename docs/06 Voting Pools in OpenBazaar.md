# Voting Pools in *OpenBazaar*

<img src="https://camo.githubusercontent.com/140995019bcc360028133b09df336bb36e7f9381/687474703a2f2f692e696d6775722e636f6d2f577750555847532e706e67" width="400px"/>

## Introduction

The advent of multisignature transactions within Bitcoin is a monumental achievement for the development of trustless (and near-trustless) systems. Building on top of the multisignature revolution is the possibility to create **voting pools**. A *voting pool* further distributes the role of an arbiter in a multi-party transaction and reduces the risk of fraudulent behavior within a pseudonymous marketplace like *OpenBazaar*.

## Voting Pools

Consider a typical exchange between two parties with an arbiter mediating the transaction, where a 2-of-3 multisignature address is generated. The buyer in this exchange sends bitcoins to the multisignature address, to be released upon the pre-agreed conditions with the seller. While seller or arbiter alone cannot steal these funds, there remains a non-zero risk of collusion between them to defraud the buyer. Unfortunately, soley relying upon reputation systems is not an adequate solution this problem, no matter how well designed. An effective strategy is to minimise the risk of collusion by adding more arbiters to the mix, a *voting pool*. A majority vote by the pool of arbiters makes it more difficult for a corrupted arbiter to defraud the transaction, and is thus a favorable means of managing risk for high value exchanges in *OpenBazaar*.

*Voting pools* in *OpenBazaar* would be created from the list of *preferred arbiters* from the buyer and seller's profile. In the case of an uneven number of arbiters within the pool, the benefit of the doubt goes to chance with the client randomly selecting a well-ranked arbiter. The total size of voting pool is limited to the [maximum number](https://bitcointa.lk/threads/number-of-m-of-n-ouputs-per-transaction.305146/page-2) of parties in a multisignature transaction on the Bitcoin network. An important element in forming a *voting pool* is to prevent the risk of a 'sore loser attack', where the multisignature transaction is constructed without the possiblity of the seller and the arbiters recovering the funds if the buyer fails to initiate the transaction, after receiving a good or losing a bet for example.

For example, Alice wants to sell a diamond ring to Bob valued at 3 BTC. Alice is understandably nervous about the transaction and specifically requires that a *voting pool* is used for arbitration in the exchange. The *voting pool* she desires has 7 participants, with a majority vote of at least 5 required. Bob accepts the contract in *OpenBazaar* and the client begins the process of assembling the voting pool, in this case 3 from Alice, 3 from Bob and one random arbiter. Subsequently, a 8-of-15 multisignature address is formed. Of the total 15 keys in the address, 7 keys belong to the arbiters (one for each member of the voting pool), 4 keys belong to Alice and 4 keys belong to Bob. 

The voting pool does not have a sufficient number of keys (7 < 8) to steal the coins, neither does Alice or Bob (4 < 8 each). In the event of a 5 out of 7 ruling by the arbiters in favor of Alice, Bob cannot remove the funds with his 4 keys + the 2 keys from arbiters who voted in his favor (total: 7 < 8). If all of the arbiters are particularly slow or there is some other reason to lack confidence in their ability, Alice and Bob can sign the funds to another address with new arbiters. 

This setup can be replicated according to the 'Lucas Algorithim':

> Two traders, Alice and Bob, require equal number ("n") of keys, as you do not know a priori who will win the trade (or bet). In general, Alice needs "n" keys, Bob needs "n" keys, and the jury needs "2n - 1" keys. The majority of 2n - 1 is always n. In the simplest case, Alice has one key, Bob has one key, and the jury size (2x1 - 1) is one (i.e., the arbiter decides with Alice or with Bob). In the above example, n = 4. Alice has 4 keys, Bob has 4 keys, and the jury size = (2x4 - 1) = 7. The "best of 7" is of course 4 (= n). The total number of keys is 4n - 1 = 15. The multisig is therefore 8 of 15, which is achieved with Bob + Alice, or Alice + voting pool (majority thereof), or Bob + voting pool (majority thereof). These numbers should work with any integer n > 0.

## Conclusion

While *voting pools* do not eliminate the possiblity that the arbiters will collude with Bob or Alice to steal, it becomes much harder to execute as a fraudulent consensus is required. In combination with *OpenBazaar* reputation systems, *voting pools* is an additional tool for users to manage the risk of peer-to-peer trading of goods and services.
