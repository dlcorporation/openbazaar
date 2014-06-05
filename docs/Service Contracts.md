# Service Contracts in *OpenBazaar*

<img style="float:center" src="https://camo.githubusercontent.com/140995019bcc360028133b09df336bb36e7f9381/687474703a2f2f692e696d6775722e636f6d2f577750555847532e706e67" width="600px" />

## Introduction

A service contract in *OpenBazaar* replaces a physical good to be sold with the terms and conditions of a service to be performed by one party. The distinction between a good and service within a [Ricardian contract](https://gist.github.com/drwasho/a5380544c170bdbbbad8) is minimal, as will be described in this article. Morever, the combination of pseudonym (nym) reputation management (*proof of burn* nyms, *web of trust*) and surety bonds can ensure a robust service industry within *OpenBazaar*.

## Service Contracts

The final format of a service contract is of course comparable to that of a physical good. Similar to physical goods, there are several discovery mechanisms for services on *OpenBazaar*.
For the sake of simplicity, we will examine two types of service contracts that can be supported in *OpenBazaar*, following the Ricardian contract model:

1. Invitation to Tender (ITT)
2. Service Listing

### Invitation to Tender (ITT)

> A call for bids, call for tenders, or invitation to tender (ITT) (often called tender for short) is a special procedure for generating competing offers from different bidders looking to obtain an award of business activity in works, supply, or service contracts... Open tenders, open calls for tenders, or advertised tenders are open to all vendors or contractors who can guarantee performance. (Wikipedia)

The first type of contract is an **invitation to tender (ITT)**, whereby a client publishes their list of requirements for a desired good or service. In the context of a service, these details are specified within a Ricardian contract and distributed to potential service providers in the *OpenBazaar* network. Relevant ITT contract details include:

1. Name and category of the service
	- Chosen from a list of pre-determined categories and sub-cateogories
	- This list will be frequently updated to reflect market needs, and include custom categories to support new markets on *OpenBazaar*
2. Price range
	- The price that the buyer is prepared to pay for the service
	- This can be left blank
3. Estimated time of completion
	- The maximum time that a buyer expects the service to be performed
4. Comments and special considerations
	- Any comments or special details that the service provider needs to be aware of

The details of the contract can be further negotiated between the parties before a contract is double-signed (i.e. a contract signed by both the buyer and service provider indicating consensus on the final version of the contract)

For example, if Alice wanted to deliver some cupcakes to a co-worker on the other side of the city, she writes the following Ricardian-contract as an ITT:

**Contract Hash:** ```5a13604e59b03c3b34f830c53919e176aa4cdc59```
```xml
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

<?xml version="1.0"?>

<!-- Contract Properties -->
<contract_type> Service: ITT </contract_type>
<contract_nonce> 12345asdfjkl </contract_nonce>
<contract_exp> YYYY-MM-DD TIME UTC </contract_exp>

<!-- Service Details -->
<service_name> Cupcake delivery </service_name>
<service_category> Courier </service_category>
<service_subcategory> Small item (< 5 kg) </service_subcategory>
<service_price> 0-20 mBTC </service_price>
<service_time> 2014-06-04 07:00-09:00 am </service_time>
<service_comments> Hi, I'd like to deliver the cupcakes to my co-worker before she
 gets into work, which is around 9.30 am. Thanks. </service_comments>

<!-- Category/Sub-category Details -->
<package_name> Cupcakes </package_name>
<package_units> 3 </package_units>
<package_perishable> Yes </package_perishable>
<package_pickupaddr> 1060 W Addison St, Chicago, IL 60613, United States </package_pickupaddr>
<package_dropoffaddr> 900 W Eddy St, Chicago, IL 60613, United States </package_dropoffaddr>

<!-- Client NYM -->
<nym_id> ALICE-NYM-ID-HASH </nym_id>

<!-- Bitcoin Pubkey -->
<btc_addr> 03d728ad6757d4784effea04d47baafa216cf474866c2d4dc99b1e8e3eb936e730 </btc_addr>

<!-- Client PGP Key -->
<PGP_Public_Key>
- -----BEGIN PGP PUBLIC KEY BLOCK-----
Version: BCPG v1.47

mQINBFMZcEIBEADJlq0oVgLfFDdW9WOBguskPdSSeAfHe4s9w8QlmRuO/Zj548gK
fofbM84rtP3rHSOSkeOTsu5GwDt48V/md6gyJ69BTZJkJ6qmxFtGaWVRLP/UD4ma
vW4EAn3PvWY6X7Z8x36U3j2I6vknH1Ufu5Dh5qvQC3WsMliul9ZxlJQZ1/TkQE+q
I/gBPRmsMFZ/xV2VOEjMtM3qOPoemhYFzU39/ra0isk81sXrotySkvWw6zsrx8Nr
kBaw9mxhs0kumF06AfKSrBjyt/FIdbJaWtNrCdxJ+NMfzQUHmq9bzpBI2VpNJzFQ
I4WlO8eRYDS1Z88VxXOjMZchd70JfNNWcXwCUeOA/HUgHO4tWczvb/5/C5pfZRKu
DqfOLntcMEzpPxbhAbXvU+K5TK394SGgu9ioXl3rdrFj1B1EBPH2BfnOdwCiOOr5
ccWVPUHdG34i4D98ARgeqEDxq9/WZwq8FG9rgSszqkmnGQtSZxz8aoW1kU1h1SQu
mqs2ZUrEoLGACkNg16kRq2z7RBLc4MAm3/GW3ygeEFQxK0PMief0X2+l0oVo7a0A
RMLLLx4ckuoX3DIJvBegFPvlp0rO3JihdzNmCqIBTDok7D0k2NiQsm3WDJHAYB+8
G4ruHVPAOzPNxz5krF+u71jcWmZKO4FRAcXCrWTQCku7wLyzOF80sVEDlwARAQAB
tGNEciBXYXNoaW5ndG9uIFlhbWFuZHUgU2FuY2hleiAoMjAxNCBLZXlwYWlyIGZv
ciBuZXcgZW1haWwgYWRkcmVzcykgPHdhc2hpbmd0b24uc2FuY2hlekBvdXRsb29r
LmNvbT6JAjkEEwECACMFAlMZcEICGw8HCwkIBwMCAQYVCAIJCgsEFgIDAQIeAQIX
gAAKCRDgeMiuv/IyzzaGEACiYWINH5utgquhNPIGl8oPXQwi3cdHbLROXk9s8K5j
umxO3qyzrZuag+M39eKrDOgMTteLcCuJV+9sgdmSJHsLuH9o9/PPwaKHsY995C0Y
5ZRsvABRQbHoOJPsdq136gH2Z0kW/RJ2fqQfNrDiqyPJpWTkrnnRZF2XU8OlIAq+
BsyeVqxOiht1vMIz2TX/LanbP6leas7Wah1GRuzhd68+NCyCUQJ4bnBDv6cbGwXR
Vi7kOOvXYoTilCENdbSuYfGWrq7z54DrefjTP3+0Y/YTWwUQr/yvXi915UCDVU+T
6jaqCwtqmezr1VjkMrFQOOrOY7jWmYo4AwQfr4hW9iLdiggr6bPmz0YRfT83a9r9
Z+SmU4zuLWmmJXARiUGBwhXUmyqFQa1yjCVI+50uW8Wx3iDot9qiO7gSB878Zq1s
Ktt3EXolTDGgpVIxZ78do42X02wD8gwGGOdDU3Dzywjy3qcIbVWreuT8tEvCU+Wx
w0TGzeoBLcHezhLEbaAOmE5jAmKPL9EbRQBGS1nV3uwzW24vu9ftNqmseYXC2afW
DCulmUHHAQEfleJA/mKii2mYV7Yxclib81+EzkzJBPijgUJBN9A1PxqliF8ZDXF/
h/jQomASoDBAL8VWo7qwTQlc5CZKZ6xnUZGdUU9lFBmnclw0A6PrMBaZjm1zeKJr
1Q==
=7M1T
- -----END PGP PUBLIC KEY BLOCK-----
</PGP_Public_Key>
-----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47

iQKBBAEBAgBrBQJTj/VAZBxEciBXYXNoaW5ndG9uIFlhbWFuZHUgU2FuY2hleiAo
MjAxNCBLZXlwYWlyIGZvciBuZXcgZW1haWwgYWRkcmVzcykgPHdhc2hpbmd0b24u
c2FuY2hlekBvdXRsb29rLmNvbT4ACgkQ4HjIrr/yMs/QqBAAg0xj9lxbbXYfbLFf
0ut69g0fg82kjVgJQ+kmhIA3gUi59QRgf4gxsoWTUKmIGXNrXbNSAycX9ekOt64L
MOHs/Bx1KOH8ZmSZ0vFBGr/62QqA7OIOV35UvRiSdxA4f3LtKN+aG99QQBioWERz
4mycHzibnKXA2s36iltnAQpXnDG4n6mumlojWXfbb/UqGBRwv30REzJReBl1n2/0
83PofYI1tNyZbYuGiD91OhyBDbrkRsLNnUKzQ+OIIFx7nYtwkZuJZuqfLyKDmmL9
TdnPsU4oXclLlgr2C64YHqj/TETPfHlmBEZniyV59e3XRnSHNN/v7YoOO0oS7Eys
iCx2/+v+r90XIK9onE94gEdWsC4xu5F1qWibdT5L0qznmzAAFOY/oVs9ctQ7RMgw
lqYGAEgTb1KIUtkPVVCVweJ1NW86H7GZXtRuG9sQyM7j7rVErqa4JCE+YLuTnfij
UYni3g0sPrGUNRG9gvVxo9KuwHQQEuRgNAvUeByZ+mRYC7Ky2vgzDWFAleJ4OHFB
N/aZ6vgDBMcmpd/CouPBP0xQh1QYd5Wj7wamMRccvlchub7j0Sq2b9jEBZFjDvls
kfJiiA0Tg71dxZZtqRJaJ341EHBqkWlOt1wQQDBXKWmhtWYcA4JBgg5t7uPoi72A
FizKa/FGaKgJxH9c8MDXggNX07M=
=Yvsl
-----END PGP SIGNATURE-----
```
Alice publishes the unencrypted contract to the *OpenBazaar* network, where service providers can scan for contracts that match the category/sub-category fields that they are interested in.

Bob, owner of 'Raven Drone Courier', is interested in securing the contract. In order for a service provider to place a bid on a contract, they prepare a 'bid contract' that will include:

1. Fee for the service
2. Terms and conditions for providing the service

For example:

**Contract hash:** ```5921a669dcd217e3286711e77911b54865d15702```
```xml
<?xml version="1.0"?>

<!-- Contract Properties -->
<contract_type> Service: ITT </contract_type>
<contract_nonce> 12345asdfjkl </contract_nonce>
<contract_exp> YYYY-MM-DD TIME UTC </contract_exp>

<!-- Service Details -->
<service_name> Cupcake delivery </service_name>
<service_category> Courier </service_category>
<service_subcategory> Small item (< 5 kg) </service_subcategory>
<service_price> 0-20 mBTC </service_price>
<service_time> 2014-06-04 07:00-09:00 am </service_time>
<service_comments> Hi, I'd like to deliver the cupcakes to my co-worker before she
 gets into work, which is around 9.30 am. Thanks. </service_comments>

<!-- Category/Sub-category Details -->
<package_name> Cupcakes </package_name>
<package_units> 3 </package_units>
<package_perishable> Yes </package_perishable>
<package_pickupaddr> 1060 W Addison St, Chicago, IL 60613, United States </package_pickupaddr>
<package_dropoffaddr> 900 W Eddy St, Chicago, IL 60613, United States </package_dropoffaddr>

<!-- Client NYM -->
<nym_id> ALICE-NYM-ID-HASH </nym_id>

<!-- Bitcoin Pubkey -->
<btc_addr> 03d728ad6757d4784effea04d47baafa216cf474866c2d4dc99b1e8e3eb936e730 </btc_addr>

<!-- Client PGP Key -->
<PGP_Public_Key>
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: BCPG v1.47

mQINBFMZcEIBEADJlq0oVgLfFDdW9WOBguskPdSSeAfHe4s9w8QlmRuO/Zj548gK
fofbM84rtP3rHSOSkeOTsu5GwDt48V/md6gyJ69BTZJkJ6qmxFtGaWVRLP/UD4ma
vW4EAn3PvWY6X7Z8x36U3j2I6vknH1Ufu5Dh5qvQC3WsMliul9ZxlJQZ1/TkQE+q
I/gBPRmsMFZ/xV2VOEjMtM3qOPoemhYFzU39/ra0isk81sXrotySkvWw6zsrx8Nr
kBaw9mxhs0kumF06AfKSrBjyt/FIdbJaWtNrCdxJ+NMfzQUHmq9bzpBI2VpNJzFQ
I4WlO8eRYDS1Z88VxXOjMZchd70JfNNWcXwCUeOA/HUgHO4tWczvb/5/C5pfZRKu
DqfOLntcMEzpPxbhAbXvU+K5TK394SGgu9ioXl3rdrFj1B1EBPH2BfnOdwCiOOr5
ccWVPUHdG34i4D98ARgeqEDxq9/WZwq8FG9rgSszqkmnGQtSZxz8aoW1kU1h1SQu
mqs2ZUrEoLGACkNg16kRq2z7RBLc4MAm3/GW3ygeEFQxK0PMief0X2+l0oVo7a0A
RMLLLx4ckuoX3DIJvBegFPvlp0rO3JihdzNmCqIBTDok7D0k2NiQsm3WDJHAYB+8
G4ruHVPAOzPNxz5krF+u71jcWmZKO4FRAcXCrWTQCku7wLyzOF80sVEDlwARAQAB
tGNEciBXYXNoaW5ndG9uIFlhbWFuZHUgU2FuY2hleiAoMjAxNCBLZXlwYWlyIGZv
ciBuZXcgZW1haWwgYWRkcmVzcykgPHdhc2hpbmd0b24uc2FuY2hlekBvdXRsb29r
LmNvbT6JAjkEEwECACMFAlMZcEICGw8HCwkIBwMCAQYVCAIJCgsEFgIDAQIeAQIX
gAAKCRDgeMiuv/IyzzaGEACiYWINH5utgquhNPIGl8oPXQwi3cdHbLROXk9s8K5j
umxO3qyzrZuag+M39eKrDOgMTteLcCuJV+9sgdmSJHsLuH9o9/PPwaKHsY995C0Y
5ZRsvABRQbHoOJPsdq136gH2Z0kW/RJ2fqQfNrDiqyPJpWTkrnnRZF2XU8OlIAq+
BsyeVqxOiht1vMIz2TX/LanbP6leas7Wah1GRuzhd68+NCyCUQJ4bnBDv6cbGwXR
Vi7kOOvXYoTilCENdbSuYfGWrq7z54DrefjTP3+0Y/YTWwUQr/yvXi915UCDVU+T
6jaqCwtqmezr1VjkMrFQOOrOY7jWmYo4AwQfr4hW9iLdiggr6bPmz0YRfT83a9r9
Z+SmU4zuLWmmJXARiUGBwhXUmyqFQa1yjCVI+50uW8Wx3iDot9qiO7gSB878Zq1s
Ktt3EXolTDGgpVIxZ78do42X02wD8gwGGOdDU3Dzywjy3qcIbVWreuT8tEvCU+Wx
w0TGzeoBLcHezhLEbaAOmE5jAmKPL9EbRQBGS1nV3uwzW24vu9ftNqmseYXC2afW
DCulmUHHAQEfleJA/mKii2mYV7Yxclib81+EzkzJBPijgUJBN9A1PxqliF8ZDXF/
h/jQomASoDBAL8VWo7qwTQlc5CZKZ6xnUZGdUU9lFBmnclw0A6PrMBaZjm1zeKJr
1Q==
=7M1T
-----END PGP PUBLIC KEY BLOCK-----
</PGP_Public_Key>
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.0.22 (MingW32)

iQIcBAABAgAGBQJTj/WhAAoJEKnOFXGYSKNNV+oP/0GjFvAhoRCchGWHYzHTf+in
v9q5/Xzx+i393LobNdCi9dsvwHxkQWBNl77xMj0Dm6WmnpAhwXw+9N+FT1iTxvxl
JyoFRrtWEEmpQSeUH+/OuhmJHC2LnRy6rXYY2lvUz1MqKmax2aL9ECGg0iyPAwRb
oKNDgXOrX1yCujD3WjsijgJ3czuVe6KdjFX+v3wNo7LGkDoTQ6q+XtS1eyMiHjTZ
k22xlixBQbYJkvtdz+0PfQr3sBwP6FIoplrQr+zWToYF2Sc6INQ6iHi0eCCByCOp
FA0EYEXR4L7sIoNZtHVCSg7N8+ViIMe8+t4G8NlhIOjuMnY4in7b5xkfVVGG9JTf
AaB26kh2mG9BoaUk9eQnXAjGlxyATmTe91vTxRUNQBwSDJMtXYc9ealpvEVyaCug
X9LkZnvta4OOtgf6x657auF7ASqvotONSQogDfN6b49X5ugeMq7U3Jvj+C1mL4rZ
cRN+Nv72Hmgl4+g4LYFomLrd9m4b0Fx8P8NlDUlHypuZ/jiZ9Hx3R1ZeYLnBKNMf
RVXAYrVYwIZe3kGLlHnqalC9V3jLieNeCMvnDu4eJqgo0kUTDY5LTxENXKnIuXWM
eUbxcZfJPHdmJc/CEY1To8Mjxrozdgcf9/XgC1XIZM9VgVmV8w5gX3GbncxGWVLc
7jmMGfFek2TkyWnzoYwM
=I7cX
-----END PGP SIGNATURE-----
```

The bidding contract can public or private, which is to say it can be broadcast back to Alice from Bob in plaintext or encrypted with Alice's private key.

Alice may receive tens or hundreds of bidding contracts to her ITT and can filter the bidding contracts according to their price, delivery time, nym reputation etc. Once Alice chooses the winning bid contract, and provided she has not finer details to negotiate, she digitally signs contract and sends copies to the bidder and an arbiter to setup the multisignature address. 

#### The *TradeNet* 

A long term outcome of supporting **ITT** contracts within *OpenBazaar* is the potential for it to become a 'TradeNet', as descibed by [Mike Hearn](http://www.slideshare.net/mikehearn/future-of-money-26663148) (slide 25). The original proposal imagined the *TradeNet* to be a market infrastructure for applications, potentially distributed autonomous corporations/businesses, to interface with in order to purchase goods and services according to their programmed goals and profit motives. These applications would issue tenders for goods or services on the *TradeNet*, receive bids and automatically purchase contracts based on algorithmically-determined conditions (factoring in price, proximity, time etc).

A much more attractive alternative is for *OpenBazaar* to potentially faciliate **ITT** contracts for both individuals and distributed consensus/autonomous organisations for peer-to-peer exchanges of goods and services. This is achievable using Ricardian contracts as they are both human and application readable, permitting human-application exchanges without either party known the true identity of each other if so desired.

### Service Listing

The second type of service contract is called a **service listing**, where service providers can advertise their services to potential clients in the hope of receiving a quotation request. Contrary to an *ITT*, where service providers seek out contracts to bid on, a **service listing** will be 'Yellow Pages' of individuals/organisations filtered according to the category/sub-category of services they provide. The **service listing** will be formatted as a Ricardian contract including the following fields:

1. Category and sub-category of service provision
2. Estimated prices
3. Estimated time to complete certain services
4. Availability
5. Comments and special considerations
6. Quotation response time

A potential client can request a quote from the a service provider by drawing up a fresh service contract (according their requirements) that includes a hash of the **service listing**. The inclusion of the hash indicates that the client is requesting a quote based off the specifications advertised by the service provider's **service listing**. From here, the contract is negotiated between both parties as described above prior to double and triple digital signing to initate the contract.

## Good Performance Bonds

A surety bond can be created to cover a failed contract, which either partially or fully remediates the costs of the failed contract for the damaged party. However, as some conditions of the contract can fail without damaging the final outcome of the contract, smaller value surety bonds can be created to incentivise 100% contract fidelity. These smaller surety bonds can be called 'good performance bonds' (GPB). 

For example, GPB may be written to penalise a service provider or supplier for failing to meet a contractually obligated deadline. Another example is a GPB for the client to follow the terms and conditions of the service specified in the contract (i.e. be at a certain place by a certain time).

The GPB can be factored as a deduction for the service provider's fee for the sake of simplicity, which can be carefully monitored by the arbiter. Within the contract, a GPB can be formatted within the following fields (using the example above):

```xml
<!-- Surety/Good Performance Bonds -->
<GPB01_desc> Goods failed to be delivered by courier before 09:00 am </GPB01_desc>
<GPB01_penalty> 7 mBTC </GBP01_penalty>

<GPB02_desc> Failure to sign for delivered goods within 7 minutes of the drone's
 arrival at the specified drop-off address. </GPB02_desc>
<GPB02_penalty> 5 mBTC </GPB02_penalty>

<GPB03_desc> Failure to respond to enquires within 24 hours. </GPB03_desc>
<GPB03_penalty> 2 mBTC/24 hours until contract cancelled </GPB03_penalty>
```

The inclusion of GPBs would occur from the outset of the contract's formation, requiring both parties to digitially sign to indicate their agreement. The arbiter can verify the authenticity and integrity of these terms by both party's digital signatures and contract hashes, as per a normal Ricardian contract.

## Conclusion

In addition to the sale of physical goods, *OpenBazaar* supports a *true* free market for services within a censorship-resistant platform. Service contracts leverage the benefits of Ricardian contracts, used for physical goods and P2P lending, to form a tamper-proof chain of authenticity for contractual consensus between two parties and an arbitrating third party. Finally, the potential for **Invitation to Tender** contracts to form a *TradeNet* effect is an exciting long-term possibility for distributed autonomous corporations/organisations to rapdily obtain goods and services.
