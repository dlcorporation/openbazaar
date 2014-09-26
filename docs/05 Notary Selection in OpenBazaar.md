<img src="https://blog.openbazaar.org/wp-content/uploads/2014/07/logo.png" width="500px"/>
# Notary Selection in OpenBazaar: Voting Pools, Certification, and Contract Blinding

## 1. Introduction

There is a significant bottleneck in the current workflow for *OpenBazaar*, which is the selection of a third party notary or arbiter. Irrespective whether the notary or arbiter is the same agent, both the <font color="red">merchant</font> and the <font color="blue">buyer</font> are required to come to a consensus in selecting a third party key-holder in a 2-of-3 multisignature escrow address. The fundamental obstacle is the *risk* of possible collusion between one of the parties and the notary, and the subsequent distrust one party has for the other party's notary preference. Unless both parties have preselected the same notary that they both trust, somewhat coincidentally, then a transaction cannot take place. This may result in significant and frustrating delays that run counter to the values that *OpenBazaar* hold for user experience. Worse, there is an elevated risk that one party will use poor judgement in just accepting whoever the other party prefers for a notary in their eagerness for the transaction to progress. 
</br>
A potential solution to this problem is the use of [voting pools](https://gist.github.com/drwasho/c04f16fcc7be9a666e90) made up of <font color="purple">accredited  notaries</font>. The **aim** of this article is to define what an <font color="purple">accredited notary</font> is and how it may be implemented in *OpenBazaar*. We will also describe how certain fields within the Ricardian contract can be blinded from the notary to protect the privacy of the exchanging parties and giving deniability to notary service providers. 

## 2. Voting Pools

The concept of voting pools has been [described previously](https://gist.github.com/drwasho/c04f16fcc7be9a666e90). Briefly, to decrease the overall risk of collusion and increase the redunancy of transactions, a multisignature escrow address is made up of several additional parties on top of the <font color="red">merchant</font> and <font color="blue">buyer</font>. For example, an 8-of-15 multisignature escrow address can be created made up of:

1. 3 notaries selected by the <font color="red">merchant</font> 
2. 3 notaries selected by the <font color="blue">buyer</font>
3. 1 notary selected at random
4. 4 keys from the <font color="red">merchant</font>
5. 4 keys from the <font color="blue">buyer</font>

Signatures from 8 keys are required to release funds from the multisignature escrow address. If the <font color="red">merchant</font> and <font color="blue">buyer</font> have any reason to doubt the pool, they can move the keys to a different multisignature address. If there is a dispute, a majority of signatures is required in combination with one of the parties to release funds from the address. No single party can steal the funds, and the likelihood of collusion is reduced with more parties involved.

Interaction of the notary pool with the arbiter is managed over the *OpenBazaar* client:

<img src="http://s25.postimg.org/t60swkc3z/Arbitration.jpg" width="800px">

The notary pool will received a digitally signed **ruling** from the arbiter. The **ruling** can be *blinded* from the notaries (i.e. encrypted with the public keys of the <font color="red">merchant</font> and <font color="blue">buyer</font>), to maintain the privacy of both parties (discussed in more detail below). Aside from the arbitration notes, the ruling will also contain an unsigned bitcoin transaction with:

1. **Input:** the multisignature escrow address
2. **Output_1:** the winning party from arbitration
3. **Output_2:** notary fee
4. **Output_3:** arbiter fee

In more complex settlements, where both parties receive a portion of the funds, additional outputs are added to the transaction. The bitcoin transaction is digitally signed by either both parties, or the winning party with the notary pool and broadcast to the Bitcoin network.

## 3. Accredited Notaries

Even with a notary pool, the question remains how users will choose notaries within *OpenBazaar*? The most direct way is for users to access the storefront of other nodes in the network, select the 'services' tab and manually add them to their list of preferred notaries. Users can also search for nodes on the network that they wish to add on their list. These approach however, assume that the user already knowns what node to trust as a notary.

One approach is for notaries to be *accredited* by a voluntary private orgaisation, which creates some open standards for notaries to voluntarily subject themselves to in order to earn an 'endorsement badge'. These open standards may include:

1. The notary node has an up-time of >22 hours per day
2. Communication response times are < 12 hours
3. Notaries issue a surety bond held in a multisignature address by the accreditation organisation

This approach is a form of self-regulation, whereby accreditation is earned after demonstrating compliance. The accrediting organisation can also hold the surety bond in the event that an accredited notary defrauds a client. In this scenario, a corrupt notary is excluded from the organisation, their surety bond is forfeit (perhaps used to compensate a defrauded member), and they lose their public accreditation with the association. A notary may choose to become accredited from several such organisations to bootstrap trust.

Technically this can be achieved by the private organisation keep a public record of accredited notaries, digitally signed, that a notary can link to within their 'notary description' field within the client.

From a user's perspective, they can search and filter potential notaries according to the presence or absence of accreditation by various organisations. Of course this does not restrict users from finding and using unaccredited notaries that they prefer.

## 4. Contract Blinding

Data fields within the Ricardian contract can be hashed prior to forwarding to the notary for their digital signature. Nearly all data fields can be hashed with exception to the bitcoin pubkeys necessary to create a multisignature address. Hashing is preferable to encryption with the buyer or seller's public key as the data fields can be easily verified by an arbiter in the event of a dispute, rather than going through additional decryption steps. The goal is to create an immutable record of the product details of the contract while obfuscating them.

## 5. Conclusion

The measures described above are designed to mitigate the risk of collusion taking place over *OpenBazaar*, but they do not replace individual responsibility and vigilence all users must take on the network.
