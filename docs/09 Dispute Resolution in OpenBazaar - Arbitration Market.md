# Dispute Resolution in *OpenBazaar*

<img src="http://s29.postimg.org/82z3qgz87/Open_Bazaar_Banner.png" width="800px"/>

## 1.0 Introduction
Multisignature escrow addresses are the key to managing risk for trades between peers on *OpenBazaar*. These addresses mathematically ensure that a single agent is incapable of stealing funds from an address using their private key alone. Furthermore, multisignature addresses can be designed to accommodate several parties within a voting pool as [previously discussed](https://github.com/OpenBazaar/OpenBazaar/blob/master/docs/06%20Voting%20Pools%20in%20OpenBazaar.md). 

In a typical 2-of-3 multisignature transaction in *OpenBazaar*, the first two signers are the buyer and seller. The third signature is a 'trusted' third party who has the power to sign a transaction in combination with the buyer or seller in the event of an accident, key theft, or dispute. The third party signer, a notary, in *OpenBazaar* also acts as the third signer of Ricardian contracts for the sale of goods and services, to leverage the many strengths of [triple-entry accounting](http://iang.org/papers/triple_entry.html) particularly for settling **disputes**.

Dispute resolution is a fundamental component to success of *OpenBazaar*. As the goal of *OpenBazaar* is to create a decentralised and censorship-resistant marketplace, State-mediated dispute resolution is out of the question. Thus, our model should follow non-State services, also known as alternative dispute resolution (ADR). 

Many forms of ADR exist in the *legacy* marketplace. ADR aims to avoid final adjudication by the State in order to reduce overall costs, save time, and potentially prevent an adversarial outcome between the contending parties after the dispute has been resolved. Rather, *OpenBazaar* aims to create a marketplace for ADR, alongside goods and services, to settle disputes between peers. 

## 2.0 Dispute Resolution

### 2.1 Notaries
Thus far the proposals for various market implementations within *OpenBazaar* (and other decentralised marketplace proposals) have assumed that a third party in a transaction (i.e. the third signer in a 2-of-3 multisignature escrow address) performs two roles:

1. **Notarising** contracts and transactions 
2. **Arbitrating** disputes between two or more in parties

The **notary** aspect of their service includes digitally signing contracts and transactions in the event of a dispute between the buyer and seller. The arbitration aspect of their role is to decide who the winning side is in a dispute between the buyer and seller. However, this overlapping notary-arbiter model is prone to several weaknesses:

- There is a conflict of interest between the arbiter and disputing parties
- There is a practical burden on a single agent to perform all of these tasks simultaneously for potentially dozens/hundreds of transactions/trades
- There is a slight disincentive for the buyer and seller to carefully choose a suitable arbiter prior to a dispute arising 

A possible solution is to divide these services, to be provided by separate agents: 

1. A notary, to focus exclusively on signing Ricardian contracts and creating/signing multisignature transactions
2. An arbiter, dispute resolution as an independent and exclusive service on *OpenBazaar*

Pamela Morgan expands on this concept:

> The ideal third party will be professional, knowledgeable about the technology and security protocols, and independent of business operations. Why are these characteristics important? Professionalism is important because the third party will be your backup to access funds in the event a signer becomes unavailable. 

> The third party should be reliable, available upon short notice, communicative, and responsive. The third party must be knowledgeable in the technology, have a thorough understanding of how to use multi-signature accounts, and best practices for security – such as offline key generation and storage. 

> They should understand principles of conflict of interest and be able to maintain a distance from operations, so that they will not be subject to coercion or other undue influence. A disinterested third party also provides investors, employees, and the community with an increased level of protection thereby justifying an increased confidence in operations as evidence of good corporate governance.

*Source:* [Multisignature accounts for corporate governance](http://empoweredlaw.wordpress.com/2014/05/25/multi-signature-accounts-for-corporate-governance/)

#### 2.1.1 Responsibilities
A notary's responsibilities include:

1. Digitally signing the Ricardian contract between two or more parties
	- The notary serves as a witness to the contract and independent auditor as per triple-entry accounting
	- The notary offers the final bitcoin pubkey for the creation of the multisignature escrow address
2. Releasing funds from a multisignature escrow address as a result of:
  1. A late-signing buyer (*lazy transactions*)
  2. A dispute between the buyer and seller, releasing funds according to the arbiter's judgement
3. Selecting a tie-breaking arbiter for an arbiter pool
4. 'Hand-holding' new users in using *OpenBazaar* for the first time

Given the role that notaries will play in exchanges in *OpenBazaar*, _their services would need to be available essentially 24/7_. Of the responsibilities listed above, the first can be entirely _automated_ and capped according to the notary's preference. The second responsibility requires the attention of the notary in order to sign the transactions. After successfully receiving the good, the buyer may be delayed in signing a transaction to release funds from the multisignature escrow address to the seller. In this case, the notary is involved to release these funds. In the event of a dispute, the notary prepares a transaction according to the arbiter's judgement for signing in combination with the 'winning' party. Of course, the notary doesn't need to fulfill this role if both the buyer and seller perform this function themselves. If a dispute arises where an arbitration pool is requested from the buyer and seller, the notary can be called upon to choose a tie-breaking arbiter according to their preference prior to the *hearing* of the dispute. Finally, the notary can offer to supervise new users through a transaction, explaining each step of the process and troubleshooting potential issues.

#### 2.1.2 Fees
While the market will ultimately determine the fee structure, we assume that automated services such as contract signing (role #1 above) would be offered freely, subsidised by other services requiring the notary's directly involvement. As for the appropriate value of the fee, we expect it to be equal to or lesser than a typical bitcoin transaction fee. This fee can either be paid as a refundable deposit from both parties, or deducted from the price of the good being sold.

#### 2.1.3 Advantages and Challenges
There are several advantages to using a dedicated notary service for 3rd party contract and transaction signing. Firstly, and perhaps most importantly, there is an effective separation between the power to release funds from a multisignature escrow address, and dispute resolution between two parties. As a result, notary and arbitration services can be independently assessed and rated for their efficiency. 

Secondly, there is a market created for notary services for the timely fulfilment of their obligations in a trade, especially triple-signing Ricardian contracts. In the event of a dispute, the final cost in fees and time is slightly higher than in a role where notary and arbitration services overlap within a single agent. However, the increase in dispute costs may incentivise greater care in arranging exchanges within *OpenBazaar* to specifically avoid these fees.

#### 2.1.4 Practical Implementation into *OpenBazaar*
How will the separation of notary and arbitration services into separate agents affect the end-user experience and overall mechanics of a transactions? Firstly, similar to the original model, the end-user begins their *OpenBazaar* experience by selecting preferred notary service providers for all future transactions. In selecting a notary, a user should prefer services that are automated with 24 hour response time when 'human interaction' is required.

Ideally, the client will select a notary service provider that is present on both the buyer and seller's 'preferred list', or an overlapping notary up to X degrees of freedom from the buyer and seller's Web of trust. For example, the buyer has a friend who shares a preference for a notary with the seller's friend of a friend (2 degrees of freedom). Failing this, the client can either randomly select a notary agent based on their reputation metrics. 

Finally, while it is the recommendation of this author for users to separate notaries from arbiters, the client will not impose this model. As the notary/arbitration market is a specialised service for *OpenBazaar*, users will be able to browse through various users offering notary and/or arbitration services. Ultimately the market will pick an approach that seems to be the most efficient.

#### 2.1.5 Notary Inclusion into Contracts
We predict that there will be two ways notaries will be included into the contract formation process. The first way is **offline**, which requires the contract to be digitally signed and passed along to the next party after inclusion of new information (demonstrated below):

<img src="http://s28.postimg.org/6bwve4a25/Slide1.jpg" width="800px"/>

This process is somewhat tedious, but necessary to establish the proper authentication chain to avoid possible attacks/disputes. Alternatively, **online** contract formation requires all parties to be online simulatneously to rapidly establish the terms of the contract and attach their digital signatures only once:

<img src="http://s3.postimg.org/hvs6c2boj/Slide2.jpg" width="800px"/>

It is important to note that the client isn't required to create these contracts, which can be made externally and imported into the client to streamline the digital signing and notary/arbitration process.

### 2.2 Negotiation
For dispute resolution between peers on *OpenBazaar*, the two major forms of ADR to be implemented are:

1. **Negotiation:** where both parties directly arrive at a resolution of a dispute.
2. **Arbitration:** where a third party is invited to resolve a dispute

*Negotiation* is a preferable approach to dispute resolution as it does not involve intervention by a third party, not even the notary of the transaction. Negotiation between the buyer and seller seeks to resolve the conflict by discourse between the parties. The transfer of bitcoins from the multisignature address can be accomplished by both parties after a successful negotiation.

Negotiation on *OpenBazaar* can take place over any communication platform inside or outside of the client software. The client currently supports encrypted communication from node to node, and also integrates BitMessage. For real-time negotiation, platforms such as CryptoCat may be an easy to use messaging platform that supports off-the-record encryption. In addition, the DarkWallet client also supports private communication channels. 

The details and outcome of a negotiation do not need to be written down or formalised in any way. Every effort should be made by both parties to resolve disputes between themselves to preserve favorable reputations and avoid arbitration fees. However, not every dispute can be resolved peer to peer negotiation; an outside party is required to arbitrate.

### 2.3 Arbitration
*Arbitration* involves an independent party, made up of a single or multiple agents, reviewing the details of a dispute and deciding where the fair allocation of property titles should be awarded to. As explored previously, the arbitrating agent shouldn't be the third signer in a multisignature escrow address. Rather, the third signer (a notary) should be a neutral party that can be contractually subject to the outcome of the arbiter's decision.

#### 2.3.1 Arbiter Selection
In the event of a dispute between a buyer and seller, if negotiation has failed to resolve the dispute, an arbiter must be employed. To begin the process, both parties inform the notary that a dispute has arisen. The notary's primary role in the event of a dispute is to create and sign a transaction according to the judgement of the arbiter(s). However, this function can be performed by the disputing parties in order to avoid notary fees. 

There are three possible ways for an appropriate arbiter to be selected:

1. Client matching
  - As with notaries, the client attempts to select an arbiter automatically based upon the 'preferred arbiter' list from both parties.
  - An extention of this concept is to the use the web of trust to find overlapping preferred arbiters from the buyer/seller's trusted and/or positively rates peers
2. Consensus selection
  - The buyer and seller agree upon an arbiter based on their examination of the arbitration market
  - In the event that the buyer or seller is *inactive* in making a decision within a reasonable amount of time (which may need to be stated in the contract), the notary and the other *active* party can select an arbiter.
  - If the buyer and seller cannot agree on a single arbiter that they both prefer, they can form an arbitration pool make up of the buyer, seller, and notary's preferred arbiter.
3. Notary-Arbiter servicing
  - Here, the notary and the arbiter are the same agent. As this agent is selected before the exchange takes place, the notary-arbiter simple proceeds to judge the dispute immediately.
  - While this is the most efficient approach in terms of time, there are drawbacks to this approach we are explained above. However, users will not be restricted from excercising this option.

#### 2.3.2 Arbitration Contracts

As arbitration is fundamentally a service, a service contract can be drawn up between all interested parties that will need to include:

1. Arbiter's details
	- GUID
	- Bitcoin pubkey
	- PGP key
	- Fee
2. Dispute details
	- Nonce of the contract in dispute
	- Hash of the contract
	- Estimate arbitration time
3. Dispute claims from both parties
4. Decision conditions (applicable only to multiple arbiters, indicating if a majority or consensus decision is required) 

Formatted correctly, the arbitration contract may look something like this:

```JSON
{
        "arbiter": {
            "arbiter_GUID": "drwasho_abc123",
            "arbiter_BTCuncompressedpubkey": "04d09c05c84a73344ee3b03d03fdf4a6bff2b1c4e15ffeb7403b91b0815be8b03ee50ade6b28d27aabc7c56cf679f74acec3d8e760595f5878caec12edd32938ea",
            "arbiter_pgp": [
				"mQENBFMKYTUBCADD6kIAjBlJ2Q0NEd97aia0BSBibO1C2lVemWig5cNATeob1McWoEo3QznZ",
			    "f9LaRsuo+ryyqEeXx4p9m9FG/TDeeZvOaiSo2Pg5MtgAdxwJK3ZQ+6b6DjrfYRZplD4qVsQd",
			    "/GhxDr733NBdTpfvE8rYrAttNeU8P9vZpJuU+ESSRNb8Sbgfrym2i7xeMP6/xnyfTunXti7x",
			    "sJzFkGIoF1dc+HntP2b9oSy1y0P5n0FdGt7IaEEtN1AZwAfFJ0obSlXiVdWdPwyambAzj93V",
			    "XD//KxXyxAHjqFD+sdqDzqxBTZ/MC/YCMU1UQ5hvWsx7FRqubLhyMB1p1ycvdnX6nqdTABEB",
			    "AAG0KFNhbSBQYXR0ZXJzb24gPHNhbUBzYW11ZWxycGF0dGVyc29uLmNvbT6JATkEEwECACMF",
			    "AlMKYTUCGwMHCwkIBwMCAQYVCAIJCgsEFgIDAQIeAQIXgAAKCRCI0UoG/7KgjtsoCACaiEO1",
			    "0u22dGDSuBLvFV2UIhyh2Cj9+KEGe7qHlohwbFHqwT+/6B7P5CmBggqL0abMqEqkUCOxk7g4",
			    "rBdCSMeqGe+7VdsXVnNAlEYGd6AqQxfcIPV/r/E0qCUQcJbBxjO8rr7il2o4b98AeU8GB6qU",
			    "8YFblsCv0KlFRYhDngHVfRMpvsTm9NMcm99P6n/UVn2mrhk50EqJMHB7T+b4n0fWQj5M9340",
			    "lmVWnn1i1w3+yDC0v4yLS9UuSuL3UsnC6CP7XPA2z5iVqoTH+i0WguGgGgyUpPIQexGm/IKx",
			    "b5Bb/rRsKpcXtdIT7Vr5US4XtCBe9zWvSWyEAz3llYA/OGx+uQENBFMKYTUBCACToWiWhjWI",
			    "aJM1pD0TXTk/IbNWZPhJpfAiYy3EsYwckvAY1Q6yOSWydakimpr+93oBpJpY9y6Aj8GDBNyv",
			    "eaAomK2jYV0cqxhOzAH2UgSLptFQawxwR/8+rLz5KDZQGT8SNNDwV7FtFT4ubzeH+ILugnJp",
			    "Jo83IjoU5Vg3g1d75Tc38KLd8VbwZ52QcxNaoxoEHQoF8Q+2rRNPwRRr5NX71jQPA6Pxuzpd",
			    "mTogQ5gIA3Zr4cDrxAAPCZAo/bDJF3jhd9lpZXFudlyCwbRNF3qfG9L0S7ES+zIfXFWmryQb",
			    "CUg4pcRfbaN9OY6GWzjOLOzXzEehd7sNbNCKEP3tWqbjABEBAAGJAR8EGAECAAkFAlMKYTUC",
			    "GwwACgkQiNFKBv+yoI4kHQgAiz6mQz0GeOfB60ILe1R/9fkYtejFTTb5P8H/w19S2WM+gFyb",
			    "R4BTg0OSN0YhcmzIzgy1zF1/J+noxEVUS5zbGLytVgLFECyOinFZUc0A/b0nuermvKFuF7GJ",
			    "QcV3Gz1HCNrfaWK7LW5hGTdQZtaFtEmla6Wk+v1MHWWW2K9Ez0KXCqrK5b0Oji2MUh8LRh2p",
			    "mmciki/R0pXXMYMJpeb9IPwOlbIqm8xT4Z93rPYyOwmgii1Dy3Gop/Ofq4yU7GGxjjALR+JM",
			    "yebij7AblNTCSgWXm/QV+ejZH0bR91FbtjdVKoFo6qrL04zuRbBFm2wHv+CYNKwRR2PPcCB/",
			    "dQaGpQ==",
			    "=IB1U"
            ],
            "arbiter_fee": "0.01 BTC"
        },
        "arbitration": {
            "contract_nonce": "01",
            "contract_hash": "f22fee51c64dd36afb158769d6dacf95a982777997f96f5e9a25b97da64d9457",
            "contract_arbitration_time": "7 days"
        },
        "buyer_claim": [
        	"The seller never sent me the turtles!"
        ],
        "seller+claim": [
        	"The buyer hasn't paid for the wee turtles even though I sent them."
        ]
}
```

The digital signatures of the buyer, seller, and notary are appended to the contract and sent to the arbiter for their approval. If the arbiter agrees to hear the case, he/she appends their details and digital signature to the contract, sending back to the interested parties. The case can now be considered open, with the format and presentation of the evidence to be arranged between them.

#### 2.3.3 Arbitration Market and Precedents
The **arbitration market** is a dedicated marketplace featured in the client listing agents offering notary and/or arbitration services in *OpenBazaar*. These agents will list the duties they perform, the estimated response-time for their services, and fees. In addition to these, arbitration service providers can also display a list **precedents** that they themselves have established or other arbiters have published in order to give an expectation of service *process* and *quality*.

**Precedents**, the legal standards formed due the application of consistent rulings on similar cases, will become a key performance predictor and indicator of an arbiter's capacity to fairly administer justice on *OpenBazaar*. It is difficult to predict how precents will be formatted, but some considerations are most likely:

1. Consent
  - Both parties must consent to their case being published as a precedent for the arbiter
2. Anonymisation of disputing parties
  - All traces of the identities (pseudonyms, bitcoin addresses etc) of the disputing parties is **removed**
3. Dispute cateogrisation
  - What type of dispute is *claimed* (i.e. failure to deliver physical good, failure to perform service etc)
4. Process
  - The objective of a precedent is to demonstrate to potential clients the process they can expect from the arbiter (i.e. what evidence needs to be provided, timeframes, what the outcomes are if a party fails to demonstrate necessary evidence, what consitutes as evidence)
  - Process for strictly anonymous transactions will be important for certain types of sensitive transactions
5. Resolution
  - If the arbiter rules in favor of the buyer or seller (a specific claim), what was the outcome of the resolution in terms of payment
6. Fees
  - What were the fees for resolving this type of dispute? 
  - If the dispute took extra time than expected, what was charged?

Arbiters may offer their services *pro-bono* in order to build up a case history of precedents to market themselves for future employment. Alternatively, new arbiters may cite *precedents* from other well-known and highly rated arbiters to indicate a pattern arbitration for similar cases. Ultimately, throught the use of precedents and an arbitration market, a polycentric merchant law is expected to arise in *OpenBazaar*.

#### 2.3.4 Appeals
A later innovation of market arbitration can be the formation of an appeals process to resolving disputes. Prior to the initial round of arbitration, both parties can agree to establish a 3-tier appeal process. Each arbitration tier may consist of arbiters of increasing quality and/or quantity, and therefore price. In the outcome of a first-tier arbitration decision that leaves the losing party dissatisfied, the losing party may appeal to the second-tier arbiter. The contract and dispute records are all forwarded to the second-tier arbiter who first determines whether the case should be heard. Consideration of the case may attract a fee, which could be paid by the appealer. If the case is heard, a second round of arbitration begins; if not, the standing judgement of the first arbiter remains and the notary prepare and signs a transaction accordingly.

## 3.0 Conclusion
*OpenBazaar* is not merely a censorship-resistant market platform for the sale of goods and services using bitcoin. *OpenBazaar* requires an arbitration mechanism to ensure that exchanges between parties are conducted with minimal risk. Unlike legacy marketplaces, the arbitration mechanism is not in the monopolistic control of a nation State, corporation, or single entity. Rather, an open marketplace for arbitration will be created to faciliate a polycentric merchant law to accomodate the requirements and preferences of each individual.
