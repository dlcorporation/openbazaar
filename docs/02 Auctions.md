# Auctions on *OpenBazaar*

#### Dependencies

1. [Ricardian Contracts on OpenBazaar](https://github.com/OpenBazaar/OpenBazaar/blob/master/docs/Ricardian-Contracts.md)
2. [P2P Lending on OpenBazaar](https://github.com/OpenBazaar/OpenBazaar/blob/master/docs/P2P-Lending.md)

## Introduction

It is becoming increasingly clear that *OpenBazaar* will become a powerful platform that will support a variety of peer-to-peer market transactions. One of the most fundamental market transaction types is the *auction* of a good by a seller to discover the market price. In this article, we cover one possible way of auctioning a good using *Ricardian contracts*. 

It should be noted that this proposal essentially describes the 'back-end' of implementing Ricardian contracts into auctions on *OpenBazaar*. It is important that the end-user (i.e. your mother, grandfather etc with novice skills) will be unaware of digital signing, hashing etc occuring in the background unless they choose to be, in order to lower the technical barrier of entry for using *OpenBazaar*.

## Auctions

The seller firstly selects an *auction* template contract in *OpenBazaar*. In this type of contract, the product and auction details of the good to be sold are entered into *required* fields within the JSON or XML file. The product auction details would include:

1. The name and description of the item
2. A minium sell price, if any
3. A 'buy now' price, if desired
4. An expiration date for the auction
5. A blank field for a bidder to enter their price

For example, let's imagine Alice wants to sell a yellow pinata on *OpenBazaar*. After digitally signing it, the **auction_contract** looks something like this:

``` Contract hash: 8f9cfa1255e4f4c1a5cc1d21c7dd7ce233aa0c9b ```
```xml
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

<?xml version="1.0"?>

<!-- Seller's NYM -->
<nym_id> Alice-NYM-ID-HASH </nym_id>

<!-- Node Address -->
<node_addr> Westeros </node_addr>

<!-- Bitcoin Pubkey -->
<btc_addr> 03d728ad6757d4784effea04d47baafa216cf474866c2d4dc99b1e8e3eb936e730 </btc_addr>

<!-- Product Details -->
<item_name> Yellow Pinata </item_name>
<item_description> Good condition, never busted. </item_description>
<item_image> https://img0.etsystatic.com/000/0/6342324/il_570xN.326696084.jpg </item_image>
<min_sell> 5 mBTC </min_sell>
<bid_price>  </bid_price>
<buynow_price> 30 mBTC </buynow_price>
<auction_expiration> 2014-06-25 21:00 UTC </auction_expiration>

<!-- Sellers's PGP Key -->
<PGP_Public_Key>
- -----BEGIN PGP PUBLIC KEY BLOCK-----
Version: Mailvelope v0.8.2
Comment: Email security by Mailvelope - http://www.mailvelope.com

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
=dDLn
- -----END PGP PUBLIC KEY BLOCK-----
</PGP_Public_Key>
-----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47

iQKBBAEBAgBrBQJTixgpZBxEciBXYXNoaW5ndG9uIFlhbWFuZHUgU2FuY2hleiAo
MjAxNCBLZXlwYWlyIGZvciBuZXcgZW1haWwgYWRkcmVzcykgPHdhc2hpbmd0b24u
c2FuY2hlekBvdXRsb29rLmNvbT4ACgkQ4HjIrr/yMs/xVhAAu6lUosqqw0TfG61L
XDjGo9U+EPqztU4Rt24QyMj5iNF6/2yNNWofrJLrPJXQJ7ZDhX18ZrAhCh7VGm7x
B86XwyAnlDRbIhZiKuXWlKG6vJAyLI66KrmU4me4+JY95aLQ/o9wgzv1QVV3kBEv
Cy3DJAmpqmHtLQ7EgL/mIANtoGMBs2bkhmudk3Dq4d1DQv+cokj3JfBvDqFLXte9
OfZPJY/mS5nSNUeNpjNwHtlQXQeabKX5IiP3tVRryMM63Sd+ZbJUF6TGCO8Yv6Uv
V1sz6Gdqk+vLvPMvqulzkQ8zSM2UAsBT+ylUjfoB9Gjie8uuVnTkg+3zoI5aqLRU
2cINQgkf0XSjU1kmxSiA/osxO51JKi0/1QV3RvBKBkKDJ/fQFzx/WVBfGhn1oYgg
digXDpUEgOqJ/CamT+XGAWKGpJb8gnE2fEsRIxKe5W1Al1FWiDrqO32+GEdJ40I4
h1pHFJP2ZFXykCs1Vkp4TONJIdGwonJAnQQBTUIf5i1aW1P9Jfobt1wHo4N5pvwv
FNK6M+dWuQtFzvVd6PxR9kPgP5PxpfHdZlJcRTh/GFrOuYPdeoKSqdTz680o7/1w
etGML8rzAKOEJNgewX58yNqvMq2t4VT5nNXu2RnMj5rJvzggZwkwa2i9pzvgtkGk
0eFXeq8J2lxvYVgNJJsSTX8olHA=
=O2ib
-----END PGP SIGNATURE-----
```

<img src="https://img0.etsystatic.com/000/0/6342324/il_570xN.326696084.jpg" width="100px"/>

Bob accesses the contract and chooses to bid on the pinata. To place a bid on the item, he draws up the following digitially signed **bid contract**:

``` Contract hash: 57074779f93235c88a07b7c6de8285c8478cc6a6 ```
```xml
<?xml version="1.0"?>

<!-- Buyer's NYM -->
<nym_id> Bob-NYM-ID-HASH </nym_id>

<!-- Node Address -->
<node_addr> Essos </node_addr>

<!-- Bid details -->
<auction_contract> 8f9cfa1255e4f4c1a5cc1d21c7dd7ce233aa0c9b </auction_contract>
<bid_price> 7 mBTC </bid_price>

<!-- Buyer's PGP Key -->
<PGP_Public_Key>
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: BCPG v1.47

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
=nT6N
-----END PGP PUBLIC KEY BLOCK-----
</PGP_Public_Key>
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.0.22 (MingW32)

iQIcBAABAgAGBQJTixr6AAoJEKnOFXGYSKNNKBcP/j9NtM5KK8/YvXfONAxBEkuB
e4NhcMigMewYM2RJjWIV+AsSQoEOmd4NpWjKzeIqEYeLBKadfY1mqatYXV50Pww0
UwwrmJcs4M0HgCDQlHwMqFPkGVfd8CfBmdDsaWwztyGbmZgzOSRKSJHHQGS3CO6S
fUqYIt+e3sEHWqf1Tj/5rJ5tuYn8awtaSkTAFPsDkpGiHq1Dr61gWD/DOyeQb1si
NMgzstC2GJ+bhq5kpUhqkE56ZRUFvgAM2dLK/NXMDgTozamrUFau532Lg3CRmhP2
0//P6Uos5KXXvcCuw64i15AdwqsKGrZ/RR2filot2Hen2y0JHvtGzqzVrKfwXqXV
cReEThDSn27y/rhqtRzmUwQSjz0IbemOIwQWRzB4T32THa+tQ3M9Enb4Q65N4W8k
AGgCy6v7ggYHvhQ15OGRE3C7gORfsQoL4FohhRAKmMCwBGj5V5a3pHHv3AwAy4Pz
j03emOwKASzyKbpT6QM+yIYqzYB+3OJJr6SDfBWH4r4D8kQYrwBbwMo4HIXbp5D9
qRPVDBvvmDv3p7ar7SqBhzS469rbnn5gIZH8kM2h2WfnBh1JwiDdVEeVdU7vY7CQ
SOL9iJiOUm4fkbPO141oovynn/4AZ1ORTR2Pw/godX5SsplWnuF16px7BXuDiomu
7PbH/QRFV4c5aSOZpwjb
=oB4I
-----END PGP SIGNATURE-----
```

Alice may receive five different bids on the yellow pinata and according to her conditions, the originally contract is updated with the latest bid price. At the end of the expiration date of the contract, Alice digitally signs the final winning **bid contract**, sends it to the arbiter for digitally signing and creating a multisignature bitcoin address for the winning bidder, Bob. 

Due to the architecture of the P2P network setup, Alice may not be available 24/7 during the term of her **auction contract** to update the market on the latest bid price of the item. As a result, she may choose to upload her contract on a 24/7 accessible node (a **negotiator node**) that acts as a contract *server*. If so, the **negotiator node** will create their own contract for the item, digitally sign **bid contracts**, update the ```<item_price>```, and turn over the final **bid contract** to Alice for her digital signature at the end of the contract/auction expiration date. If Alice digitally signs the contract, the contract is sent to an arbiter for sigining and creation of the multisignature bitcoin address for Bob, the winning bidder, to send funds to. As a reward for hosting the contract, the **negotiator node** is rewarded by a fee paid for by Alice (via another multisignature address setup with anoter arbiter). If Alice disapproves of how the contract was negotiated by the **negotiator node** on her behalf, she can simply refuse to sign the contract and raise a dispute to the arbiter for a refund of the fee from the multisignature address.

#### Insurance

For the seller (Alice), she can have confidence that the funds for the item actually exist once Bob has sent the required amount of bitcoins to the multisignature bitcoin address, upon which she will ship the item to Bob's designated address. Similarly for Bob, he can retrieve the funds from the multisignature address if he can prove to the arbiter's satisfaction that he goods either did not arrive, or did not arrive in the condition specified in the contract.

To further promote good behavior, the arbiter may require a **surety bond** from one or both parties. The surety bond is a quantity of bitcoins sent from either the buyer or seller (or both) held in a multisignature bitcoin address that is refundable upon a successful trade. If a dispute arises, and one party is found to be at *malicious* fault, the funds within the surety bond are transferred to the arbiter and opposing party as compensation.

A *non-malicious* versus *malicous* fault may be, for example, a shipping comapany damaging the goods during transport (*non-malicious*) versus the seller knowingly sending a damaged good (*malicious*). The value of the surety bond is negotiable and completely optional. However, it is reasonable to expect that surety bonds will become less necessary between individuals with a high *web of trust* reputation and/or *proof of burn* identity.

## Conclusion

Ricardian contracts have sufficient flexibility to support eBay-style auctions on *OpenBazaar*, leveraging the authenticity and fidelity features that digital chain signing and contract hashing it has to offer. While the P2P network infrastructure and contract distribution protocol is still under development, we propose here a means of using a third party **negotiator node** to host contracts on behalf of a seller, updating price changes in real-time.
