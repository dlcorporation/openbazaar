# A pseudonymous trust system for a decentralized anonymous marketplace

Dionysis Zindros, National Technical University of Athens <dionyziz@gmail.com>

## Keywords

pseudonymous anonymous web-of-trust identity trust bitcoin namecoin proof-of-burn timelock decentralized anonymous marketplace openbazaar

## Abstract

Webs-of-trust historically have provided a setting for ensuring correct identity
association with asymmetric cryptographic keys. Traditional webs-of-trust
are not applicable to networks where anonymity is a desired benefit. We
propose a pseudonymous web-of-trust where agents vote for the trust of others. By disclosing
only partial topological information, anonymity is maintained. An inductive
multiplicative property allows propagation of trust through the network without
full disclosure.  We introduce additional global trust measures through proof-of-burn and
proof-of-timelock to thwart Sybil attacks through an artificial cost of
identity creation and maintenance and to bootstrap the network. Existing
blockchains are used to provide friendly names to identities, and the network
is applied to a commercial setting to manage risk.  Finally, we highlight certain
attacks that can compromise the trust of the network under certain assumptions.

## History

Webs-of-trust are traditionally a means to verify ownership of encryption and signing keys by a particular
individual whose real-world identity is known. The first widely deployed web-of-trust is the GPG/PGP web-of-trust [Zimmerman][Feisthammel].
In these webs-of-trust, a digital signature on a public key is employed to indicate a binding between a digital
cryptographic key and an identity. Such a digital signature does not designate trust, but only signifies that
a particular real-world individual is the owner of a digital key.

Webs-of-trust have also been utilized for different purposes in various experimental settings. In Freenet [Clarke], it is used
to guard against spam [Freenet WoT]. In a commercial setting, the Bitcoin OTC web-of-trust successfully attempts a centralized approach to establish
a true trust network [OTC], contrasting identity-only verification webs-of-trust of the past.

## Introduction

The aim of our web-of-trust is to construct a means to measure trustworthiness between individuals in a commercial setting where goods
can be exchanged between agents. The goal of such a measure is to limit, as much as possible, the risk of traders in an online
decentralized anonymous marketplace. We are proposing a system to be used in production code as a module of OpenBazaar [OpenBazaar], a peer-to-peer
decentralized anonymous marketplace that uses bitcoin [Nakamoto] to enable transactions.

Risk management in OpenBazaar is based on two pillars: On one hand, Ricardian contracts are used to limit risk through mediators,
surety bonds, and other means which can be encoded in contract format [Washington]. On the other hand, the identity system is used to establish
trust towards individuals. In this paper, we introduce the latter and explore its underpinnings.

Trust management in OpenBazaar is established through two different types of mutually supporting systems; projected trust and global trust.
Projected trust is trust towards a particular individual which may be different for each user of the network; hence, trust is "projected" from
a viewer onto a target. Global trust is trust towards a particular individual which is seen as the same from all members of the network. Projected
trust is established through a pseudonymous partial knowledge web-of-trust, while global trust is established through proof-of-burn and proof-of-timelock
mechanisms.

## Threat model

The identity system is threat modelled against various adversaries. We are particularly concerned about the malicious agents highlighted in this paragraph,
with their respective abilities.

First, we wish to guard against malicious agents within the network. If there are malicious buyers, sellers, or mediators, the goal is to disallow them from
gaming the network and obtaining undeserved trust.

Second, we wish to guard against malicious developers of the software. If a developer tries to create a bad patch or influence the network, this should be
detectable, and the honest agents should be able to thwart against such an attack by choosing not to upgrade by inspecting the code. The system must not rely
on the good faith of developers; it is open source and decentralized.

Third, we wish to guard against governments and powerful corporations that wish to game or shut down the network. These agents are not always modelled as rational, as their
objectives may involve spending considerable amounts of money and processing power to game the system, with no obvious benefit within the system bounds. 
Their benefits may be legal, economical, or political, but cannot be simply modelled. Their power may be legal and can defeat possible single-points-of-failure on
the network.

However, we assume that the malicious agents have limited power in the following areas. We assume that the bitcoin, namecoin, and tor networks are secure. We assume
that malicious agents have limited processing power, bandwidth, monetary power and connectivity compared to the rest of the network. As long as malicious agents
control a small portion of such power, the network must remain relatively secure.

The limited connectivity assumption requires additional explanation. We assume that a malicious agent will not be able to find and control a graph separator for any
non-trivial induced graph between any two parties on the web-of-trust. This assumption is detailed in the sections below.

Our trust metrics are heuristic; some trust deviation for malicious agents who try to game the system with a lot of power is acceptable. However, it is imperative that trust remains
"more or less" unaffected by local decisions of agents, unless these decisions truly indicate trustworthiness or untrustworthiness. Trust should be primarily
affected by trading behavior, and not by technical influence on the network.

## Web-of-trust

The OpenBazaar web-of-trust maintains three important factors: First, it maintains strict pseudonymity through anonymizing mechanisms; second, it
establishes true trust instead of identity verification; and third, it is completely decentralized.

The OpenBazaar web-of-trust is used in a commercial setting. Trust is used to leverage commercial risk, which involves losing money. Traditional identity-verifying
webs-of-trust such as GPG are in purpose agnostic about the trustworthiness of the web-of-trust participants. That type of web-of-trust verifies the identity of its members
with varying certainty. However, it remains to the individual to associate trust with a particular person for a particular purpose: Whether they can be trusted with money, for example [GPG identity].

In OpenBazaar, the participants are inherently pseudonymous. In this setting, we wish to maintain an identity for each node. This identity is strictly distinct from
the operator's real-world identity. While the operator may choose to disclose the association of their real-world identity with their pseudonymous node identity,
the network gives certain assurances that such pseudonymity will not be broken. Hence, pseudonymity is closely related to anonymity: Pseudonymity allows the creation
and maintenance of an online "persona" identity with a certain history; anonymity ensures the real-world identity of the persona operator remains unassociated with
the persona. Hence, our goal is to provide both pseudonymity and anonymity.

A true web-of-trust is a directed graph where nodes are individuals and edges signify trust relationships. In contrast to identity-verifying webs-of-trust,
in a true web-of-trust, edges do not signify identity verification; they signify that the edge target can be trusted in a commercial setting. For example, when
trust is given to a vendor, it signifies that the vendor is trustworthy and will not scam buyers by not delivering goods. When given to a mediator, it signifies
that the mediator is trustworthy will resolve conflicts between transacting parties with a neutral point of view judgment. And when given to a buyer, it signifies that the
buyer is trustworthy and will pay the money she owes. Clearly, trust is not symmetric.

While identity verification is a concept successfully leveraged by individuals for secure communications and other transactions, it is meaningless to try to
verify the identity of a pseudonymous entity, because a pseudonymous entity is the cryptographic key in and of itself, and therefore identity verification would constitute a
tautology. It is therefore required to adopt a different meaning of "trust" than in a traditional setting of real-world identities.
Hence, trust in this case signifies the trustworthiness of an individual in a commercial setting, their financial dependability, their reliability as mediators,
and their credibility as trust issuers [1] [2].

## Pseudonymity

Each node in OpenBazaar is identified by its GUID, which uniquely corresponds to an asymmetric ECDSA key pair. This GUID is the cryptographically secure hash
of the public key. The anonymity goal is to ensure this GUID remains unassociated for any real-world identity-revealing information such as IP addresses. 

Each GUID is associated with a user-friendly name. These user-friendly names can be used as mnemonic names: If someone loses their trust network by reinstalling
the node without first exporting, they know that certain agents remain trustworthy. Furthermore, user-friendly names are used in the trust bootstrapping procedure
in which it becomes easier to peer-review that the bootstrapped nodes are the correct ones. Finally, user-friendly names can be exchanged between users out
of the software usage scope; for example, a user can directly recommend a vendor by their user-friendly name to one of their friends via e-mail.

To maintain a cryptographically secure association between node GUIDs and user-friendly names, we utilize the Namecoin [Gilson] blockchain. A node can opt-in for
a user-friendly name if they so choose. To create a user-friendly name for their GUID, they must register in the "id/" namecoin namespace [Namecoin ID] with their user-friendly
name. For example, if one wishes to use the name "dionyziz", they must register the "id/dionyziz" name on Namecoin. The value of this registration is a JSON
dictionary containing the key "OpenBazaar" which has the GUID as its value. As Namecoin ids are used for multiple purposes, this JSON may contain additional 
keys for other services. The namecoin blockchain ensures unforgeable cryptographic ownership of the identity. When a node broadcasts its information over the
OpenBazaar network, they include their user-friendly name if it exists. If a node claims a user-friendly name, each client verifies its ownership by performing
a lookup on the namecoin blockchain. If the lookup succeeds, the name is displayed on the OpenBazaar GUI and the information is relayed; otherwise the information
is discarded.

As namecoin names can be transferred, this allows for participants to transfer their identity to other parties if they so desire; for example, a vendor can 
transfer the ownership of their store by selling it.

## A naive solution

The most obvious and naive choice for a trust system in a commercial setting is a global voting system. While this solution is obviously flawed, it constitutes an important
foundation upon which the next ideas are built. In this section we describe this idea in order to determine its flaws, which are solved in our next proposal.

In typical centralized systems, including eBay and Bitcoin OTC, there is a global rating which is determined as the sum of the individual ratings of others towards an
individual. Attacks of fake ratings are taken care in the system in an ad hoc fashion which is enabled by the centralized nature of the system.

In decentralized systems, Sybil attacks [Douceur] make this situation particularly more challenging and without an easy way to resolve. Hence, this naive solution
is undesirable. The solution to this problem is to first introduce a cost of identity creation and maintenance for global trust, and allow for the trust through
edges to be projected. We explore these solutions below.

## Partial topological knowledge

It is a conclusive result in the literature that, by analyzing graph relationships between several nodes, given certain associations between nodes and real identities, it becomes
possible to deduce the real identities behind other nodes. In particular, if an attacker is given only global topological information about a web-of-trust as well as some pseudonymous identity associations with real-world identities, they can deduce the real-world identities of other nodes [Narayanan]. Hence, by revealing the complete topology of the web-of-trust graph between pseudonymous identities,
an important loss of anonymity arises. For this reason, we propose a web-of-trust with partial topological knowledge for each node. Under this notion, every node
only has knowledge of its direct graph neighbourhood – they are aware of the direct trust edges that begin from them and end in any target. This does not disclose
any information about the total graph, as they are arbitrarily selected by each node. These ideas have been explored previously in the literature as friend-to-friend
networks [Popescu].

## Trust association

In the pseudonymous [3] web-of-trust, each node indicates their trust towards other nodes that they understand are trustworthy. This understanding can come from
real-life associations among friends who know the real identity of the pseudonymous entity. An indication of trust does not harm anonymity in this context. This
understanding can also come from external recommendations about vendors using friendly names. For instance, under a threat model that trusts some centralized third
parties, it is possible to establish trust in this manner. As an example, if a vendor is popular on eBay, and a buyer trusts eBay, the vendor can disclose their
OpenBazaar user-friendly name on their eBay profile, and the buyer may opt to trust that identity directly.

Trust is indicated as edges with a source, a target, and a weight. The weight is a floating-point number from -1 to 1, inclusive, with 0 indicating a neutral opinion,
-1 indicating complete distrust, and 1 indicating complete trust. These can be displayed in a graphical user interface in a more simplistic manner; for example,
the canonical client may opt to present a star-based interface for positive trust, and flagging for negative trust; or, alternatively, it may choose to present
a simple thumbs-up and thumbs-down option, indicating discrete trust of 1 or -1 if employed, or 0 if not used [4]. These trust edges remain local and are not
disclosed to third parties. We call the direct edges "direct trust" and the weights will be denoted as `w(A, B)` to indicate the direct trust from node `A` to node
`B`.

## Trust transitivity

As topological knowledge is partial, we resolve the projected trust between nodes through induction. Let `t(A, B)` denote the projected trust as seen by node `A`
towards node `B`. Projected trust is then defined as follows:

```
t(A, B) = w(A, B), if w(A, B) != 0
t(A, B) = a Σ w(A, C) t(C, B) / |N(A)|, for C in N(A), if t(A, B) > 0
```

Where:
* `t(A, B)` denotes the projected trust from A to B.
* `w(A, B)` denotes the direct trust from A to B.
* `N(A)` denotes the neighbourhood of A; the set of nodes to which A has direct trust edges.
* `|N(A)|` denotes the size of the neighbourhood of A.
* `α` is an attenuation factor which is constant throughout the network.

The meaning of the above equation is very simple: If Alice trusts Bob directly, then Alice's trust towards Bob is clear. If Alice does not trust Bob directly,
then, since we wish to retain only partial topological knowledge, Alice can deduce how much to indirectly trust Bob from her friends. She asks her friends how much they trust
Bob, directly or indirectly; the trust from each friend is then added together to produce the projected trust. However, the trust contributed by each friend
is weighted based on the local direct trust towards them; if Alice trusts Charlie directly and Charlie trusts Bob (directly or indirectly) then the projected trust
that Alice sees towards Bob is weighted based on her trust towards Charlie; for example, if Alice trusts Charlie a little, he's not allowed to vouch for Bob a lot.
Finally, the projected trust is normalized based on the number of friends one has, so that it remains within the range from -1 to 1.

The condition `t(A, B) > 0` is imposed so that negatively trusted neighbours are unable to vouch for their trust towards others – otherwise they would be able to
lie about their trust towards others if they knew they were negatively trusted and impose onto them the opposite trust from what they claim.

The attenuation factor `α` is used to attenuate trust as it propagates through the network. Thereby, nodes further away from the source gain less trust if more hops
are traversed. We recommend a network-wide parameter of `α = 0.4` as is used by Freenet, but this can be tweaked based on the network's needs.

This simple[5] algorithm assumes that trust is transitive; if Alice trusts Charlie and Charlie trusts Bob, then Alice trusts Bob[7]. This is a strong assumption and may
not always hold in the real world. Nevertheless, we believe it constitutes a strong heuristic that allows a network to deduce trust with partial topological knowledge.

## A comparison to other webs-of-trust

It seems worthy to compare this approach to existing webs-of-trust to point out their differences. In contrast to GPG [GPG identity], our proposal maintains both anonymity and true
trust. In contrast to Freenet, trust is used for commercial purposes and not just to fight spam. In contrast to Bitcoin OTC, the network is decentralized, the topology
is only partially known, and the trust is only projected and not global.

Certain services provide webs-of-trust in a centralized way, but they do not advertise them as such. eBay ratings provide webs-of-trust, but the topology is globally
known and the platform is centralized. Facebook's social graph provides trust through friendships. Interestingly, Facebook's social graph allows partial topological
knowledge depending on the privacy settings of the participants. However, centralization is still a problem. In centralized solutions, pseudonymous identities through
user-friendly names can also be maintained without a blockchain. The simplicity of implementation benefit is also a strong one.

Centralized solutions have the drawback of a single-point-of-failure. As one of the goals of OpenBazaar is to avoid Achilles' heels (single points of failure), centralized solutions become 
unacceptable. The purpose is, for instance, to eliminate the ability for government intervention in the web-of-trust through secret warrants served to the
administrators of such a centralized system that may require the handover of private encryption and signing keys.

## Man-in-the-middle vendors
This framework is susceptible to a man-in-the-middle attack which is unavoidable in pseudonymous settings. The attack works as follows: A malicious agent wishes
to gain trust as a vendor without really being a trustworthy vendor. They first create an OpenBazaar vendor identity. Next, they choose one other vendor that
they want to impersonate. They subsequently replicate their product listing as their own. They also monitor the actual vendor's catalog for product changes, and they
relay messages between buyers and the actual vendor when buyers message them. When a buyer purchases a product for them, the rogue vendor also forwards the purchase
to the real vendor. Notice that this problem does not directly apply to mediators.

If, after the purchase, the buyer and seller rate each other positively, this rating will not impact the actual parties, but will only be reflected on the rogue vendor.
Hence, the rogue vendor will gain trust as both a seller and a buyer without actually being either. This process can be automated. At a later time, the rogue vendor
can use the man-in-the-middle position to read encrypted messages between buyers and sellers and may sacrifice their maliciously gained reputation to cheat on a
desired buyer or seller. Continuous operation of such rogue nodes can undermine the network.

It is difficult to guard against such attacks. The question of whether someone "really" knows a pseudonymous vendor becomes philosophical; what does it mean to know
someone who is pseudonymous to you? And if a man-in-the-middle vendor is always delivering goods, are they not also a trustworthy agent? It is recommended that users
establish direct trust only with pseudonymous vendors whose real identity they already know, or have signals that the pseudonymous vendor is not being man-in-the-middled. The
latter is difficult to establish, but may be possible through independent verification on different networks and a continued trustworthy history. If we assume that the
delivery of products will not be intercepted, the product delivery itself may be used as a mechanism to include a physical copy of key fingerprints in order to establish
that no man-in-the-middle is being present.

Nevertheless, negative trust is semantically a different notion from positive trust. Negative trust can be attached to vendors whose identity is unknown; if
a man-in-the-middle behaves in an untrustworthy manner, it is imperative to rate them negatively. This distinction between positive and negative trust is
made clear in the condition for `t(A, B) > 0` to be positive in the equations above. It is a challenging problem to communicate this difference to the user
via a clear user interface.

## Feedback
Feedback can be given by buyers to vendors, by vendors to buyers, and by buyers and vendors to mediators in text form. Feedback is a piece of text from a particular
source pertaining to a particular target. Keeping the above man-in-the-middle vendor attack in mind, it may in cases not make sense to rate
vendors or buyers directly if their real identity is unknown by the rater, even if they trade fairly, unless they can establish an existing trust relationship towards
them in order to at least determine their legitimacy.

To avoid fake feedback, feedback must only be relayed by the OpenBazaar client if it is from a node that has transacted with the target. Therefore, feedback must
be digitally signed and include a reference to the transaction that took place – the hash of the final Ricardian contract in question, as well as the bitcoin
transaction where it was realized.

However, given that transactions are free to execute, to avoid Sybil attacks from vendors or buyers who transact with themselves, feedback must only be trusted
when it is given from parties that are already trusted using the total trust metric defined below. Otherwise, it must not be displayed or relayed.

## Bootstrapping the web-of-trust

It is hard to establish trust targeting a new node on the network with no web-of-trust connections to it. This issue is addressed in the Global Trust section.
However, it is easier to allow new users entering the network to trust individuals who have established some trust through the web-of-trust. Bootstrapping trust
is widespread practice in the literature [Clarke].

This bootstrap can be achieved by including a hard-coded set of OpenBazaar node key fingerprints that are known to be good in the distribution. At the beginning,
these can be the OpenBazaar developers. It is crucial that the number of nodes included is wide so that no individual can influence the bootstrapped trust.
Advanced users are advised to further diminish the weights of the direct edges to the bootstrap-trusted nodes and to include higher-weighted edges to people
they physically trust.

The special bootstrapping nodes must be configured to always respond to trust queries, regardless of whether they trust the query initiator.

This practice in particularly useful to guard against illicit uses of the network, which have been experienced in similar, centralized but anonymous solutions [Barratt].
By ensuring the bootstrap-trusted nodes highly rate only non-illicit traders, it is expected that the network will promote legitimate uses of trade. While
black market goods can still be traded, the user will be required to opt-in for such behavior by manually introducing trust to nodes who highly rate trusted
black market vendors.

## Graph separator attack
The web-of-trust security strongly depends on the size of graph separators. Let us examine the trust as seen from a node `A` to a node `B`. Let `G'` be the
graph induced from the web-of-trust graph `G` as follows: Take all the acyclic paths from `A` to `B` in `G` whose every non-final edge is positive.
These contain nodes and edges. Remove all nodes and edges that are not included in any such path to construct graph `G'`. Then `G'` is the induced trust graph
from `A` to `B`. An `(A, B)` separator is a set of nodes of `G'` which, if removed from the graph, make the nodes `A` and `B` disconnected.

We define an entity "controlling" a set of graph nodes as being able to arbitrarily manipulate the reported `t` and `w` functions when the controlled nodes
are inquired about their trust beliefs.

We will prove the following theorem for any separator. The smallest separator, mentioned below, is simply easier to manipulate by a malicious party, as they
are required to control a smaller set of nodes.

**Theorem**: A malicious entity controlling the smallest `(A, B)` separator on the induced graph `G'` will be able to change a negative projected trust to a positive
projected trust towards the target as seen on the original graph `G`.

**Proof**: Let `S` be any `(A, B)` separator on `G'`.

<img src="http://s12.postimg.org/qfnix9hil/web_of_trust_separator.png" width="800px"/>

Since the trust from `A` to `B` was originally negative, this means that `A` and `B` are connected on the induced graph `G'`. As the projected trust is negative,
this means that there are direct negative edges in `G'` from some intermediate parties `B1, B2, ..., Bn` to `B`; these edges cannot be indirect, as indirect edges are
not traversed for trust discovery.

We will show that the trust through any of `Bi` can be manipulated to be positive. Indeed, take some arbitrary `Bi`. Then there will exist some paths from `A`
to `B` with `Ci` as their penultimate node. Take some arbitrary path `P_i,j` from `A` to `B` through `Bi`. We will show that this path can be manipulated
to produce positive trust. Since `S` separates `A` and `B`, then there must exist some element `s` in `S` that is also in `P_i,j`. Since `s` is controlled
by the malicious entity, they can modify their claimed direct trust towards `B` and set it to `1`. They can also completely ignore any indirect trust, including `Bi`'s opinion:

```
w(s, B) = 1
```

Through this mechanism, every path can be manipulated through the control of `S`. Therefore, all paths ending in a negative edge can be eliminated. Since `A` and
`B` were originally connected, they will remain connected through this trust manipulation. Finally, at least one path ending in a positive edge will exist.
Therefore, since `t(A, B)` will be a sum of positive terms, `A`'s projected trust towards `B` will be bounded from below as follows:

```
t(A, B) >= α t(A, s) / |N(s)|
```

But `t(A, s)` must be necessarily positive. Therefore, `t(A, B)` must also be positive on the induced graph. However, projected trust on `G` is only based on
results on the `(A, B)` induced graph `G'`, and the value of `t(A, B)` will necessarily be the same as seen on `G`. QED.

We have shown that a determined attacker can manipulate trust if they control some separator on the network. Therefore, it is crucial to avoid hub nodes in the
network, and especially the existence of trust through only non-disjoint paths. As the web-of-trust develops, it is important to form trust relationships that
connect nodes from regions with long distance.

This result is expected; a separator of size 1 is essentially an Achilles' heel for the system. Such single-points-of-failure necessarily centralize the
web-of-trust architecture and completely undermine the decentralized design.

## Topology detection through queries

As one of the web-of-trust goals is to disallow malicious agents to learn the global network topology, it is crucial that the default node configuration is
to not respond to trust queries initiated by nodes they do not trust. If this mechanism is not employed, a malicious entity can query all known network nodes
and eventually deduce the global network topology easily.

The exception to this is bootstrapping nodes, which, due to necessity, must be configured
to answer all trust queries. Some ε-positive trust can be used as the minimum threshold of trust below which the canonical client does not respond to queries.
To ensure queries are authenticated, imagine a query from `A` to `C` about whether `B` is trustworthy. The query must be signed with `A`'s OpenBazaar private key to ensure topological information is not revealed to unauthorized parties asking for it. The query must be encrypted with `C`'s OpenBazaar public key to ensure that nobody else can read it, even if the inquirer is authorised. Finally, the response must be signed with `C`'s private key, to ensure that trust is not manipulated as it travels the network, and encrypted with `A`'s public key, again to ensure topological confidentiality.

In this sense, most trust must necessarily be mutual. However, the topology of the graph still remains directed, as the trust weights can be different in
either direction.

## Association with other identity systems

It is worthy to attempt an association of the web-of-trust network with other identity management systems. However, given the highlighted differences in the
previous section, such an association would compromise some of the security assumptions of the model. It is therefore mandatory that interconnection with
other networks is an opt-in option for users who wish to forfeit some of our security goals.

An interconnection with the GPG web-of-trust may be achieved by allowing OpenBazaar nodes to be associated with GPG keys. A particular OpenBazaar node can
have a one-to-one association with a GPG identity through the following technical mechanism: The GPG identity can provide additive trust to the existing
trust of the system. To indicate that a GPG key is associated with an OpenBazaar identity and that the GPG key owner wishes to transfer the GPG trust to an
OpenBazaar node, the GPG key owner cryptographically signs a binding contract which contains the OpenBazaar GUID of the target node, and potentially a
time frame for which the signature is valid. The GPG-signed contract can then be signed with the OpenBazaar cryptographic key to indicate that the OpenBazaar
node operator authorizes GPG trust to be used for their node. The double signed contract can then be included in the metadata associated with the OpenBazaar node and distributed
through the OpenBazaar distributed hash table. Each client can inter-process communicate with the GPG software instance installed on the same platform to obtain
access to existing keys and signatures.

Nevertheless, it is advised not to include such an implementation in the canonical client, as traditional GPG
webs-of-trust are identity-verifying, not trust-verifying, as explored in the section above. Furthermore, the GPG web-of-trust does not offer any
assurances on pseudonymity. While it is possible to exchange GPG signatures anonymously, the GPG web-of-trust is typically based on global topological knowledge
of the GPG graph and is distributed through public keyservers. If a user opts-in to interconnect with the GPG web-of-trust, they are forfeiting these
benefits of the OpenBazaar network.

An interconnection with the Bitcoin OTC web-of-trust is also possible. Existing trust relationships can be imported to the OpenBazaar client manually through
a file, or automatically downloaded from the Bitcoin OTC IRC bot dynamically upon request, as the Bitcoin OTC website is an insecure distribution channel and
does not offer HTTPS. In the dynamic downloading case, the threat model is reduced to trusting the TLS IRC PKI, which is known to be attackable by powerful
third parties [DigiNotar].

This web-of-trust has the benefit of being a true-trust web-of-trust, and has a history of support by the Bitcoin community. A double signature is again required
to interconnect two identities. The GPG key associated with the Bitcoin OTC network is used to cryptographically sign a binding contract similar to the one described
above, and the rest of the procedure is identical to GPG identity binding.

In this case, an Achilles' hell is introduced to the software, as the user is required to trust the Bitcoin OTC web-of-trust operator and the distribution
operator, both of which identities can
possibly be compromised by a malicious third party. The situation can be improved if the Bitcoin OTC operator begins GPG signing the trust network, or by
requiring the Bitcoin OTC trust edges to include GPG signatures by the users involved. However, the topology of the network is again public, forfeiting
pseudonymity requirements. Therefore, an implementation is again not advised for the canonical OpenBazaar client at this time.

If the user is not concerned with single-points-of-failure and centralization, the web-of-trust can be temporarily bootstrapped by binding identities to
existing social networking services which include edges between identities as "friendships" or "follows". For example, the Twitter and Facebook networks
can be used. Such bindings can be weighted with a low score in addition to existing scores as described in the Total Trust section below [6].

Further research is required to determine how such interconnections will impact the security of the network.

## Global trust

In addition to the projected trust system provided by the web-of-trust, it is desired to provide some global trust in the network. This serves to
allow the network to function with nodes that need to receive trust, but are not associates with other users of the network, or wish to remain pseudonymous
even to their friends. In addition, this allows to bootstrap the network for someone who wishes to use it without explicitly trusting any entities.

Global trust mimics the trust given in real-world transactions towards vendors that have invested money in their business, something that can be physically
verified. When a buyer visits a physical shop to purchase some item, they trust that the shop will still be there the next day in case their item is faulty;
they do not expect the shop to disappear overnight. The reason for this expectation is that it would clearly be unprofitable for the vendor to open
and close shops every day, as it costs money to establish a store, and the money needed to establish a store is more than the money a vendor could gain
by selling a faulty product.

Similarly, hotels ask for the passport of their residents in order to be able to legally hold them accountable to limit financial risk. While it is possible
to create counterfeit passports every other day, it is economically irrational to do so, as building a new identity is more costly than a couple of hotel nights.

In these situations, rational agents are economically incentivised not to cheat on transactions through physical verification of proof that it would be
costly to forfeit their identity – either to create a counterfeit passport or to shut down a physical store overnight. However, in a pseudonymous digital
network, such mechanisms need to be established artificially. We start by exploring some approaches to the problem that do not meet our goal: Proof-of-donation
and proof-to-miner. Subsequently, we introduce two mechanisms that solve the problem, proof-of-burn and proof-of-timelock, which are combined to form
the global trust score.

In all schemes, the person wishing to create trust for a pseudonymous node pays a particular amount of money, which can be provably associated with the node
in question. The differentiation comes from whom the payment is addressed to.

## Proof-of-donation
In a proof-of-donation (also called  "proof-of-charity" in the community) scheme, the pseudonym owner pays any desired amount to some organization, which is hopefully used for philanthropic or other non-profit
purposes. The addresses of organizations that are allowed to receive donations would be hard-coded in the canonical OpenBazaar client and payments towards them
would have been verified by direct bitcoin blockchain inspection by each client. A proof-of-donation first seems desirable, as money is transferred to organizations
for good. One possible scenario could include funding the OpenBazaar project itself through this scheme.

The technical way to achieve proof-of-donation is to simply make a regular bitcoin transaction with a donation target as its output. The transaction must also include the
GUID of the target OpenBazaar identity that the donation is used for.

Nevertheless, a proof-of-donation scheme is inadequate for our purposes, as it introduces an Achilles' heel. In particular, if a malicious agent is able to access the private
cryptographic keys of one of the donation targets, they are able to game the system and manipulate trust arbitrarily. Compromising the private cryptographic keys
can be achieved through various ways by powerful agents; for example, a secret warrant can be issued by a government ordering that the private keys are handed
to the court.

This attack would work as follows: The 
malicious agent first generates a new OpenBazaar identity. Subsequently, they donate a small amount of bitcoin to the donation target organization they have
compromised, including their OpenBazaar node as their target identity in the proof-of-donation, thereby gaining a certain amount of trust. They then use the
private keys they control to give the money back to themselves, potentially through a certain number of intermediaries to avoid trackability. Finally, they
repeat the process an arbitrary amount of times to gain any amount of trust desired, thereby gaming the system.

## Proof-to-miner
In a proof-to-miner scheme, the payment to create trust for an identity is paid to the miner that first confirms the bitcoin transaction which is the proof.
This scheme initially seems desirable, as there is no single entity which can be compromised, and it incentivizes the network to mine more, thereby making bitcoin
more secure and, in turn, OpenBazaar more secure.

Technically, proof-to-miner can be achieved by including an OP_TRUE in the output script of the transaction. While anyone is, in principle, able to spend the
output of the given transaction, a miner is incentivized to only include their own spending in their confirmation. Alternatively, a 0-output bitcoin transaction
can be made, so that all the inputs are given to the next miner as fees. Again it is important to include the GUID of the OpenBazaar identity in the transaction.

Unfortunately, it is again possible to game this system. This attack would work as follows: The malicious agent first generates a new OpenBazaar identity. Subsequently,
they make a proof-to-miner bitcoin transaction with any amount they desire, but they keep the transaction secret. They then perform regular bitcoin mining as usual,
but include their secret proof-to-miner transaction in their block confirmation. Including an additional transaction does not increase the cost of mining; therefore
this approach can be employed by existing rational miners. If they succeed in generating a block, they publish the secret transaction and they gain identity trust
in the OpenBazaar network, and can use the money again in the same scheme to increase their trust arbitrarily. If they do not succeed in generating a block, they 
keep the transaction secret and double-spend the money in a future transaction in the same scheme, until they are able to generate a block.

## Proof-of-burn
Proof-of-burn schemata have been in use by the cryptocurrency community in various settings [CounterParty]. In proof-of-burn, the payment to create trust for an
identity is paid in a way that remains unspendable. Because it is unspendable, the system cannot be easily gamed as in the previous approaches.

Technically, proof-of-burn makes a regular bitcoin transaction including an OP_FALSE in the output script of the transaction. Again, the GUID of the OpenBazaar
identity is included in the transaction to enable blockchain validation.

Proof-of-burn makes Sybil attacks infeasible, as it requires the attacker to create multiple high trust entities in the network, which is costly. In essence,
this is equivalent to bitcoin's proof-of-work scheme and leverages the existing blockchain for the proof.

Global trust based on proof-of-burn is based on how much money was burned to establish a particular identity. We use `g(x)` to denote the global trust
derived from the fact that an amount `x` has been spent to establish the trust of the identity. We notice that `x` is the sum of all the amounts that
has been provably burned for this particular identity. In addition, we notice that when a particular transaction output is used to establish trust
towards some identity, this output is necessarily only associated with one identity. Verification of this proof can be done by the canonical OpenBazaar
client through direct bitcoin blockchain inspection. `x(B)` is a function of the person whose proof-of-burn is to be determined, `B`. For simplicity,
we will for now denote it as `x`.

To determine the numerical trust for the global trust associated with a particular identity, we work as follows. First, we calculate `x` as the sum of verified
proof-of-burn amounts, in bitcoin, associated with the target identity.

Next, we use the following function to evaluate the trust towards the identity:

```
g(x) = 1 - (1/2)^(x/c)
```

Where:
* `x` denotes the amount spent for the proof-of-burn
* `g` denotes the global trust associated with the identity
* `c` is the *base trust cost* of the system

The *base trust cost* is a hard-coded value in the canonical client which is the amount of money required to establish basic trust in the system. The
value can be determined based on the current exchange rate of bitcoin, and can be updated in the future depending on the network's needs. As the value
of bitcoin is expected to rise, it is expected that the value for `c` will drop. This has the additional side benefit that historically older accounts accumulate
more trust as time goes by, as long as the price of bitcoin rises.

To clarify the rationale of the above equation, note its following values:
* `g(0) = 0`. A pseudonymous identity that has not provably burned coins has no global trust.
* `g(c) = 1/2`. A pseudonymous identity that has spent the base trust cost easily establishes a 50% global trust.
* `lim g(x) = 1`, as `x` approaches infinity. Notice that it takes exponentially more money to approach 100% global trust.

We recommend that the base trust cost is a very small affordable amount for any human user. This will make the cost to enter the network small, but still
avoid Sybil attacks. Such schemes have long been used in the literature as proof-of-work to avoid denial of service attacks [Back]. Proof-of-burning has the
same benefits as proof-of-working, as it delegates the proof-of-work to the bitcoin blockchain.

## Proof-of-timelock
While proof-of-burn is equivalent to proof-of-work [CounterParty], we propose an additional mechanism that can be used separately or in combination
with proof-of-burn. In proof-of-timelock, the proof-of-stake ability of a blockchain is leveraged to produce a system that eliminates Sybil attacks
without having to resort to the destruction of money or, equivalently, CPU power.

In proof-of-timelock, the individual interested in establishing trust towards a pseudonymous identity provably locks a specific amount of money in
a transaction that gives the money back to them. This transaction has the property that it remains unexecuted for a specific predefined amount of time.
However, the fact that the transaction is going to take place in the future, the exact amount, and the amount of time of the lock are publicly
verifiable.

While proof-of-burn allows identities to be created in a way that is costly to recreate, proof-of-timelock ensures it is impossible that an enormous amount of identities
associated with one real-world individual can co-exist at a specific moment in time. Proof-of-timelock is a weaker insurance than proof-of-burn;
proof-of-burn can be thought as proof-of-timelock, but for an infinite amount of time.

We predict that people will feel considerably more comfortable ensuring their identities through proof-of-timelock rather than proof of burn.
The psychological burden associated with money destruction may not be an easy one to overcome.

Unfortunately, it is currently impossible to create a technical mechanism for proof-of-timelock on the bitcoin blockchain. Bitcoin supports
the `nLockTime` value at the protocol level. However, this mechanism is not currently honoured by running nodes [nLockTime] and the transaction
will not be broadcast in a way that is verifiable.

A Turing-complete blockchain such as Ethereum [Wood] allows an implementation of this mechanism. Nevertheless, we are reluctant in using this
scheme, as Turing-complete blockchains are yet to be proven feasible in practice and may pose problems in terms of scalability, performance,
and fees.

As such, we recommend proof-of-timelock as an alternative mechanism, but further research is needed to conclude whether it is feasible as
an underlying mechanism for a decentralized anonymous market.

## Total trust
Based on the projected and global trust metrics presented above, we propose the following measure as the total trust towards a network node:

```
s(A, B) = (1/2) * t(A, B) + (1/2) * g(x(B))
```

The projected and global trusts are added together to produce the total trust as seen from `A` to `B`. The weights used here are 50% for each,
but it is advised to tweak these weights based on empirical evidence during development. For advanced users, the weights can be customizable.

The total trust can then be displayed in the user interface of the node of user `A` when she is viewing the profile of user `B`. Additional
interface elements that are possible to include can be the exact amount of money spent in the proof-of-burn scheme, as well as the direct
links yielding the cumulative projected trust for the particular target through induction.

## Conclusion
We have introduced a new mechanism to allow for fully pseudonymous webs-of-trust. The web-of-trust is developed in a way that allows conveying
true trust and not simple identity verification. Furthermore, anonymity is preserved through only partial topological disclosure. The notion of
graph distance is maintained through an attenuation factor. The web-of-trust
is designed to be used in a commercial setting, where trust is an indispensable tool for trade.

The web-of-trust
is bootstrapped through trust to a seed set of nodes, which requires the user to explicitly opt-in if they wish to trade illicitly.

Introduction to the trust system is
obtained through global trust, which is weighted along with projected trust. Global trust is achieved through a proof-of-burn mechanism, and an
alternative proof-of-timelock mechanism is explored. Together, these mechanisms allow a calculation of total trust between nodes.

In parallel with our proposals, we illustrated security concerns on mechanisms that are not
appropriate for such an implementation, such as proof-of-donation and proof-to-miner, and we developed an attack on the web-of-trust through
graph separator control.

Overall, this pseudonymous trust system can be used in a commercial setting such as OpenBazaar. It is strengthened when supported by Ricardian contracts
to create binding agreements between parties through the security of the Bitcoin blockchain and should not be used alone.

## Notes
1. It may be meaningful to distinguish trustworthiness of a pseudonymous individual in different roles; for example, a person who is a trustworthy
   merchant may not be a trustworthy judge. Hence, trust to buy from a person may be different from trust to mediate. However, for now, we are assuming
   that this trust is the same under our projection mechanism.

2. GPG distinguishes between trusting the identity binding between a real-world individual and a key and the trust directly given to an individual
   as far as they are concerned about *signing* other keys. In a similar setting as blurring the trust between different roles, we consider these to be the same.
   In the OpenBazaar web-of-trust, trust is an intuitive concept and there need to be no formal rules followed when trust is given to others. The every-day
   statement "I trust this person" corresponds to actually giving trust to an individual. This is in contrast to the GPG web-of-trust in which signing keys
   requires a certain procedure of identity verification with which individuals may not be familiar with, and hence this differentiation is in order.

3. The use of the word "pseudonymous" as a qualifier of the web-of-trust is mistaken. The web-of-trust itself is not pseudonymous, nor are the edges,
   in the sense that there is no pseudonym associated with the web-of-trust or the edges themselves. The web-of-trust and edges are "pseudonymious"; that is, related
   to the concept of pseudonymity. However, the word pseudonymous is more understood in the literature, and we are opting for its use in this context,
   while understanding this subtle distinction.

4. We do not distinguish between uncertainty of trust and certainty in neutral trust as other authors [Jøsang]. It may be helpful to employ such distinction
   in future versions of the web-of-trust.

5. This algorithm is a draft. Please leave your comment on potential attacks and vulnerabilities it may have. It seems too simplistic to be able to work in
   the real world and may need considerable tweaks.

6. The author strongly advises against such interconnections. The threat model of the OpenBazaar network is completely forfeited if such trust relationships
   are used. Centralized, non-anonymous services for trade such as eBay are widespread and can be used in OpenBazaar's stead if these assurances are of no
   concern to the user.

7. This simple transitivity scheme is flawed and it must be reworked. Currently, trust is impossible to calculate if cycles exist in the network graph. As
   the topology is only partially known, it is not trivial to detect cycles. Furthermore, basic cycle detection mechanisms used in routing protocols may
   easily compromise the anonymity of the network by revealing non-local topological information. The formulae to deduce trust must be reworked to take
   this important issue into consideration. It may be possible to avoid cycle detection and employ a mechanism which converges to the actual trust with good
   probability if some randomness factor is used to decide responding to queries whose answer is not known.

## References
* P.R. Zimmermann. The Ofﬁcial PGP User’s Guide. MIT Press, 1995
* Patrick Feisthammel, 7 Oct 2004, http://www.rubin.ch/pgp/weboftrust.en.html
* OpenBazaar: http://openbazaar.org/
* Satoshi Nakamoto, Bitcoin: A Peer-to-Peer Electronic Cash System, 2008
* Sanchez Washington, 23 June 2014, https://github.com/OpenBazaar/OpenBazaar/wiki/Contracts-and-Listings
* I. Clarke, O. Sandberg, B. Wiley, and T.W. Hong. Freenet: A distributed anonymous information storage and retrieval system. In Proc. Int. Work- shop on Design Issues in Anonymity and Unobservability, volume 2009 of LNCS, pages 46–66, 2001.
* Freenet WoT: https://wiki.freenetproject.org/Web_of_Trust
* OTC: http://wiki.bitcoin-otc.com/wiki/OTC_Rating_System
* GPG identity: http://lists.gnupg.org/pipermail/gnupg-users/2013-March/046364.html
* Gilson, David (2013-06-18). "What are Namecoins and .bit domains?". CoinDesk, http://www.coindesk.com/what-are-namecoins-and-bit-domains/
* Namecoin ID: https://wiki.namecoin.info/?title=Identity
* A. Narayanan, V. Shmatikov, De-anonymizing Social Networks, IEEE Security and Privacy 2009.
* J. Douceur. The Sybil Attack. In Proc. of the IPTPS ’02 Workshop, Mar. 2002.
* A. Jøsang. An Algebra for Assessing Trust in Certification Chains. Proceedings of the Network and Distributed Systems Security Symposium, 1999.
* CounterParty, Why proof-of-burn: https://www.counterparty.co/why-proof-of-burn/
* A. Back, Hashcash - A Denial of Service Counter-Measure, Aug. 2002.
* nTimeLock: https://bitcointalk.org/index.php?topic=321550.0
* G. Wood. Ethereum: A Secure Decentralised Generalised Transaction Ledger.
* J. R. Prins, DigiNotar Certificate Authority breach, Sep. 2011.
* M. J. Barratt, Silk Road: eBay for drugs. Addiction, Volume 107, Issue 3, page 683, Mar. 2012.
