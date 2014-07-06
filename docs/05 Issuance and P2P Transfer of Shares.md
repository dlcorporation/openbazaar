# The Issuance and P2P Transfer of Shares in *OpenBazaar*

by ```drwasho``` and ```Delain Markos```

<img style="float:center" src="https://camo.githubusercontent.com/140995019bcc360028133b09df336bb36e7f9381/687474703a2f2f692e696d6775722e636f6d2f577750555847532e706e67" width="600px" />

## Introduction

```Decentralised money necessarily requires decentralised markets.```

*OpenBazaar* has begun to create the peer-to-peer (P2P) infrastructure to enable individuals to trade any good or service pseudonymously using bitcoin. The focus thus far has been on the sale and transfer of physical goods and services. However, decentralised markets are required for **all** asset classes, including shares. 

However, there are several security considerations that must be factored into with peer-to-peer sales of share contracts. What is to stop an issuer or any bearer selling the same share contract to multiple individuals, essentially *double-spending* the share? Currently, there are several platforms to enable users to issue shares to avoid the *double-spend* problem. One solution is to employ the use of a central issuer or mediator, who validates all peer-to-peer (P2P) transfers to prevent double-spends. Alternatively, blockchain technology can be used minimise the risk of *double-spends* in the absence of a trusted third party. The latter can be accomplished by using the Bitcoin blockchain (i.e. colored coins, Mastercoin or Counterparty protocols), leveraging the existing and growing security of the network. Another option is for a user to create their own blockchain with each *coin* representing a token of the asset. 

While these approaches may be technically sound, there are some key disadvantages. A central issuer/mediator that validates transactions between peers introduces a centralisation and security risk, which only grows as the share price moves in a direction contrary to the interest of the issuer. In the case of a central mediator(s) (e.g. an exchange server), while the use of Ricardian contracts would prevent any fraudulent manipulation of the share contracts, the mediators themselves are central points of failure for secure asset transfers.  

Using the Bitcoin blockchain for asset issuance and P2P transfers consumes additional resources that are paid for by other members of the network. Moreover, transaction times between peers are limited to the existing contraints within the Bitcoin network. Creating a custom blockchain is a significant risk if there is a failure to gain a critical mass of honest nodes, contributing sufficient hashing power to security the network. It is also unclear how successful projects such as *Ethereum* will be addressing these issues and managing their own network security. 

A preferable solution to this problem is to leverage the existing network and contractual infrastructure of *OpenBazaar* without relying on a trusted third party or a blockchain. While we do not presume to forsee what approach users may use, or force users to follow any one model, in this article we propose a scheme called **one-time key revocation asset transfer** (OTK-RAT).

#### Objectives

1. Allow the transfer shares without using a blockchain and creating a new coin
2. Allow the transfer shares without requiring the issuer or a trusted-third party to keep track and verify transfers
3. Preserve the privacy of users in the transfer of shares

## One-Time Key Revokation Asset Transfer (OTK-RAT)

### Part 1: Issuance of Shares

Shares will be represented as individual Ricardian contracts, or 'asset contracts'. An issuer will include the following information as fields within the contract:

1. Issuer ID (nym ID)
2. Asset contract class (in this case 'shares')
3. Share nonce (unique identifier for the share)
4. Share entitlement (message outlining what the bearer is entitled to from the company)
5. Issuer Public PGP key
6. Issuer digitial signature of (1)-(5)

One of the most important pieces of data within the share contract is the share nonce. The share nonce is a unique identifier for each share, which can be verified by cross-referencing against a list of all shares issued (**share listing**) and their corresponding nonces in the initial public offering. The share listing will be digitally signed by the issuer and other arbiters.

For example, Acme Inc. conducts an IPO issuing 5 shares. Acme draws up the following **share listing**:

**Share Listing Hash:** ``` 1e0b3a555c10104322b3a01bcd822444be53fb23 ```
```xml
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

<?xml version="1.0"?>

<!-- Contract Properties -->
<contract_type> Financial Asset </contract_type>
<finasset_type> Share Listing </finasset_type>

<!-- Share Issuer -->
<issuer_name> ACME Inc. </issuer_name>
<issuer_nym> 61768db8d1a38f1c16d3e6eea812ef423c739068 </issuer_nym>

<!-- Share Nonces -->
<share01> 356a192b7913b04c54574d18c28d46e6395428ab </share01>
<share02> da4b9237bacccdf19c0760cab7aec4a8359010b0 </share02>
<share03> 77de68daecd823babbb58edb1c8e14d7106e83bb </share03>
<share04> 1b6453892473a467d07372d45eb05abc2031647a </share04>
<share05> ac3478d69a3c81fa62e60f5c3696165a4e5e6ac4 </share05>

<!-- Share Entitlement -->
<share_entitlement> The bearer of this share is entitled to an 
single stake of equity in ACME Incorporated, and one voting 
right. </share_entitlement>

<!-- Issuer PGP Key -->
<PGP_Public_Key>
- -----BEGIN PGP PUBLIC KEY BLOCK-----
Version: Mailvelope v0.8.2
Comment: Email security by Mailvelope - http://www.mailvelope.com

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
=dDLn
- -----END PGP PUBLIC KEY BLOCK-----
</PGP_Public_Key>

<!-- Issuer Digital Signature -->
-----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47

iQKBBAEBAgBrBQJTlB+GZBxEciBXYXNoaW5ndG9uIFlhbWFuZHUgU2FuY2hleiAo
MjAxNCBLZXlwYWlyIGZvciBuZXcgZW1haWwgYWRkcmVzcykgPHdhc2hpbmd0b24u
c2FuY2hlekBvdXRsb29rLmNvbT4ACgkQ4HjIrr/yMs+fqA/9FQHla0tEL8oFANVW
QLmNUGxQkTHvoPWPIYQpNCdWnbV03XC77RTI0YoxO6f0UXM624TwiWYSMviRLa4m
lpn+drZGiVwb2aESailexFwXzYYNyPr8nnR5QJIHmqhMl7VTB7H54GYFG2+ggK6r
yeH9HUUYziPAoga6ORyx3eYaOFYcOB34Ga5X8IuJCJ1b/Jf90ObcwRWlfrmlf/W6
nFHhqGPPgw4FWQ1CamVx5B1DFT/N29yBjIvAqhJPjKTexFAM4anvbV5WzXpN03io
WYaAo1tRFypM+msvOcGJs2t6Dn0HVFcE4sSQxHQN2uHPxOBkdyQXESVNRIOwCX76
zAzqgLSSoyZJgaEmf3cXxo294FlkdPVMBTiLomy+CxGPEZis2snst7vCo0ohIu6L
HQ1081Z4LIVxCrG+OOBSFZMnnuMF5BT9n19FkLk3eOlARrl8YWmJMudOoqtHtbpr
yT1Zq1BNOgMmY1+m9uPocATs87QnjAmgUCK1QA1FwlRJqUZ9P8ZBlncHwRCqaGLl
D+nkeEXKJ5mDgQnEIbGC5FnMHgmonUf5GlsYQIin0wRhz2FsRAgpq5nR1i9LZHit
yv0rBd0QSnN72rPQAf5D6FStOQSoWTTWQDZsI5krmjgrv12saFPO0vw2lE1UzE+P
Jfw+bo6TPKy6BVYO1GdAoSzYRUU=
=IxtT
-----END PGP SIGNATURE-----
```

### Part 2: Genesis Shareholders

The share contract is created with its sale to the first buyer (Alice), the *genesis shareholder*. As with other Ricardian contracts, Alice makes a bid offer by including the following fields within the contract:

1. Alice's details (nym ID, public PGP key)
2. Price for the share
3. Alice's digital signature of the final contract

After receiving Alice's bid, Acme Inc. accepts the bid by digitally signing the contract and sending it to a mutually agreed upon arbiter for triple-signing and the creation of the multsig address. Alice's funds in the multisig address are released once Acme Inc. updates the public share listing to indicate that the *share nonce* has been sold. 

![0](http://s1.postimg.org/5rga9d7nz/Images.png)

### Part 3: One-Time Key Revocation Asset Transfers

The risk of a double-spend primarily exists in P2P transfers beyond the *genesis shareholder*. If Alice wants to sell the share contract to Bob and Jack at the same time, two legitimate chains of ownership will be created for the same share nonce. This isn't a problem for physical goods and services, as failure to delivery the good or perform the service will prevent any funds from being released for the multisignature address. Buyers of share contracts require a means of validating that the share contract *cannot* be sold to any other party without using a trusted third party or deanonymising public ledger.

This can be achieved through the creation of *one-time keypairs* by both the buyer (Bob) and seller (Alice). Alice firstly advertises the share contract for sale, which includes her nym details and the issuer's digital signature of transfer to Alice, verifying that she is *genesis shareholder*. The share contract attracts the attention of Bob. Transferring the asset firstly requires the Bob to create a bid contract for the share, which must include the following data:

1. Share nonce
	- Optional: include a hash of Alice's 'for sale' share contract, but the nonce should suffice if the issuer's digital signature is valid
2. Bob's details (nym ID, public PGP key)
3. Price for the share
4. Bob's *one-time* **public** *key* (full signature block and corresponding hash)
5. Bob's digital signatures using their public key and the *one-time* **public** *key*

For example:

**Bid Contract Hash:** ``` 4f43692c12a41079fb9b3dc58e7d367b453cc650 ```
```xml
<?xml version="1.0"?>

<!-- Contract Properties -->
<contract_type> Financial Asset </contract_type>
<finasset_type> Share Contract </finasset_type>

<!-- Share Contract -->
<issuer_name> ACME Inc. </issuer_name>
<issuer_nym> 61768db8d1a38f1c16d3e6eea812ef423c739068 </issuer_nym>
<share_nonce> 356a192b7913b04c54574d18c28d46e6395428ab </share01>

<!-- Buyer Details -->
<buyer_nym> 4f43692c12a41079fb9b3dc58e7d367b453cc650 </buyer_nym>

<!-- Buyer PGP Key -->
<PGP_Public_Key>
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: Mailvelope v0.8.2
Comment: Email security by Mailvelope - http://www.mailvelope.com

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
=dDLn
- -----END PGP PUBLIC KEY BLOCK-----
</PGP_Public_Key>

<!-- Buyer One-time key  -->
<PGP_Public_Key>
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: BCPG v1.47

mQINBFODLW8BD/9rmoBRBASaZuNpPBG+Gj7/aJcE7aQ4Sti7lKaERFD7/rHdWHm+
o+FnyQvxpkOuuU6G4q739tP5ZqHx/bn9rhpAKKa+o7es70jlpenHyge40QyIU1/9
jXzwlMsXkq9XfbOhqtgiBRpeZ83/ZjUsf5/wQXhrGWvG4rnKj5khYNq8PHzqJO21
cDcD7LJy6yPuOgrBfb4MMa3+9lauIZ5Ye2kXR4m1OuWrig0M7SwgFZwo3GbmcWe5
KCK60nHW0AZh47B/yC18s/uR3t2bGrkQwL6AgTiOd2hX/K2l1ccgIPnWo1s/5fMc
7HiGpPkioOYhWgDm+2bimh56D2Tq7ikZQSDZIhw42pOQCevN/efak7vc2vaaaKqG
reF8EwQ5vahF9bS6aNzXzdG1t6PYVAIupdWzCt0vrZr1ynBaIEEBJlFuI3vEyp+X
85BVqV9B7gWbcE6vLeUPUB/Nu4NEdg5V4Np+URFQvW9NKfN04kGfuEViVe0sfgSE
c86h+eJ3gWTI8NdhJZdRkzKzlB7QFzMfL0TzxKSkOSu47eWx64e4xsyvkAVirkDb
5VRzoeOOpJ/5ZOE1Cv8XJWEUZd/WAyp60LT2Ga8mCqhUrPAkcQKsPhccEn23mxIH
8Pt3xWfnDFqtma7Tu2fBCM4UKpd/dAjTVnZNNjSuBb+4SGBuGiUkA3yvdwARAQAB
tB1MaW9uZWwgRGVudCA8bGlvbmVsQGRlbnQuY29tPokCMgQQAQgAJgUCU4Mt1gYL
CQgHAwIJEKnOFXGYSKNNBBUIAgoDFgIBAhsDAh4BAAAzQQ/9GArtJ4cNqPqM//NJ
CsQHCy35mKOpErbEkia/U10wlISDYV0S3fJJ+ktE/RSF1ZU+2JMf3Hl4q7hYPsFx
PvfayjRL48WBXI/V31zLvZUuH4reut4QLM4e6eAugS3lT+p8jU7mS7audZfUW65/
VL3ZXJs8QhW52LqffkhAJLQauXBy0gE7+ndbGRVxrquINt2sTZFLBaDOpLr84Aiq
+UYunRUOmM7lpMnuErTkTe670Pxsu+8Ta8r+bedXhNIbYcMTgoJLOBLXIdL3G7ix
5y5ebw0eQXTfX6QfW//er9NOi0lWVtplrYFoQ98kS19/uEta4P7rkMqZGBpPc7Zt
r3zdeNwmbU3oVOv88ecizuvv3rwMDN5juUZ/KP0vQePA7LEdpGLdTpBMmwd5t6XA
rso0pDZl4J6YxVZ5HoIYlw2a648VgF0nli11zzix/YKtMSRVOwubuo0YGP/cRJy9
qVawNU79wTHtnva86orGuQ5d9H/F7S2+f93u87nG5TNnI5ORXWzAHkJ3VU6SDzAL
s3K9PbzTSu4biSsMFSll2cZjZw2INsH9+gNOCWzwS7vROVxuZFQolyuWmBfBwVq5
U+S8gmRJELkblR+jXetY5e8T2Cv23KefBj6LBv1HpiUMD6KX4cASS94tMdLlJqa7
8Yl7A35froh30Tq3wfm1KSX7SuS5Ag0EU4Mt2AEQAIQzWvnLqtZP9nhWGcGqRwoZ
P0RJHmnbCpVmmVaoj2I/36k7PcuYs1xbc9Qt0gBpCQiskIjmCKVEcs+Dfj960qRx
zrVfUQ/O09MrI2eMekhYnC+jlBNXc22CgH1ESodZDCZf2iA9qjAjd8swLotJ2v0M
w6GLmuLmejo2M3kV/jnQJW5ePHd/Wyw45yA1TJv75UhHZ4mo3/MYPBZnSt624JBt
/+T4++XaG1kMDf5Ku63SEwhkz/nGpyW4BYTa56Pd/zKVxoxW5SfGfgREw8aw09ja
Apkfz9fyGAXcptFWCAvDDfxSCKiMNFBGzuXmgsB3GmEhaOpA9YwCy5TFPWvJ2U+w
Z8DNM2JMGgwEL+AfHPa9zSH7fXppF95zpJRMpS0oLM3Rk7OxH+jF5xj+tzNJlBEU
drfIw3J6ZZD0wFSZUx4/5Wqa7nCDl/FnrYPXevZXL6eaSsY5umeTNveLLLz1SYq+
GtRqBgON7fOZbKNxw2udAYpufNX4HXvf/Y/FBf1zrUtxf035a+MmAtSjKbf6yUI0
BcwNLVBtyMQ6npL0942hH1T37szIL3TT2RZRifSs8u22oZVOxRaEyZrRdYrtQpz5
47rQMJ76a4mplmBGjdMv/ksvicVh1SJ7f+YhtGkUcDWC0CUYxnY/jAEL34muSZad
G4CAKk7w3jJwryMbE6Y5ABEBAAGJAh8EGAEIABMFAlODLh8JEKnOFXGYSKNNAhsM
AACzog//R4yBYDXurrsyFpPS2ndCwm/F0yxIVMYx5n/qWxrt+1Yv8sc9PVSLnTil
qoVjJIokq6UkpATcmZOxSthCXYX1BjmQdjnlz6YGZHWKYkT2BPOJTHvcchSKnx2v
n+DIlVIyJjvo6T4zeUVl99XJwWN7kNJ+NrlcLzqzksNFW8S6pndkBjn5bC/CzZKg
h/KHX7L7ibc3jICgI4MZZLjapf+Y4mDmzPoSLrQBHMzAAShj3Li6IEdz0C6KrfGW
zVcCHHfpOhWY+A0y4ztOKEEWUlrlTPPgxuEbbspee5caBb6mVsvADwn2/wJ2LSYU
a0jBSXnQy5Az94xbfbJtLqEn7uWsJ9HE0kXOLk89BCSguYog86ptmUXG4uDT5S9z
lScR5XC3EJOKpvYUNchZS1ydMoerb3VLtVY6pQUqRvSu9+HrouHpp2h2+6B83Eh7
gTy7BSqc7TIhSsfNIt5nJLCLzWiGst9CS6XuuLzf9JAH85m9ZH8AuKfAW2fICX8K
yiBicH/seGHqdJ7buEidG3WbA3vvGePma2cXDTfBRcddUwvoLTmCxOMt8IPEwuUq
0tnSoJaCHMMN+csbgCTLb+CMvVjzGbgI8Z3LlKCe1siBh6iDvad7/pIEZm7T7OOC
FFN8mcvExvCZU6mpCGRg7JmXuI5gzq+O3A+x2virikGYG7NjK8w=
=nT6N
-----END PGP PUBLIC KEY BLOCK-----
</PGP_Public_Key>

<!-- Digital Signature -->
-----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47

iQKBBAEBAgBrBQJTlE94ZBxEciBXYXNoaW5ndG9uIFlhbWFuZHUgU2FuY2hleiAo
MjAxNCBLZXlwYWlyIGZvciBuZXcgZW1haWwgYWRkcmVzcykgPHdhc2hpbmd0b24u
c2FuY2hlekBvdXRsb29rLmNvbT4ACgkQ4HjIrr/yMs/TVBAAtakTp5faT46fr5W+
aM7ibQfTL71NFDDdYRnIKsbC160+Nt4dVfGJzd5dY7XWZo8nh4XDkW7SqaLtblqH
4nnwGlPWz12g9eN459ryfggdKAOyputliGiYo8GNU5r94SFtoEAuDHfZp2ZanorW
NwgY6ybRITzDX7+mhMzo7mDzstId9ffDvHxZx/VmTaUgYhQw0kLh0ABaqT6nco3+
w1Q1ZDojqCnrS3z40/50pKR+mOYsFjM5QMTszjItfS2S3kz5nGYSj2coLP0c+fHB
SwhqgO6KPnCyjJ2wu87rcDOE960cY7rShLCwgNP6a0lM1z8zNkdpDFGg/UpV2/0j
JmOciFiSLuom/szuUujyHFVgwt9OumZFYCI+zMDQo6hmH6zbt4jchx5H4r6OwGyA
koIYVwQU25PuUiblefHOUjdQ8skatBcF2/dOXFNV9P2/ZpDb/EvGjHcy6DQf5MDc
SXOsbGj255lYI2OwQPmMq5yudRiLaLq1ZLiG26G+z8OUuE12kB8+m0OYQ+QwOvAC
YpW8Bjnvi+S8aE/NGGHbGpn/+MV636+q7JP+LHD0kGrfe377/CT+bzquv/0OLHAQ
yXdjq3/WFmdXb464Wc+bp4Yia87CQ1/VyR0KIq2sLhRK/27XB/4v6SCbpuuVmwho
OsHgYDeyitDMoQch0s+vJzs3Y9s=
=FQZY
-----END PGP SIGNATURE-----

<!-- One-time key Digital Signature -->
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.0.22 (MingW32)

iQIcBAABAgAGBQJTlE/AAAoJEKnOFXGYSKNN4UgP/ipyr7OqukWW6wcbfNbDzdYm
rShPs6mYBnKgkXoI6eqz7hRxp+sZubypE/K+zfYfZtu3ozHmQvAAz5cmG5ccXTaB
ldjx4fxEb+c0KX3pWhhyr6tjBNTyWoDtQQwJk5Umah7HsgID63NwW4o3/i2ocXae
eMS1cbsTqfHuiEPCHAtoEDQkytkl6el4a8zbp4qF5KrdMnYCpCPSud9tBYHrflOx
eLA36XYOQHp0bhX7KT2S+jKtXoOBxB2tFGkb4Gh7AcEIrn/U/NpTsuNVgLWuV1OJ
4tnqCNv+vUMQbrmUEskFPpl/p03YFuO2b+w7ZpT1dILy1PjEpDnDl4kMy0kAOXd7
/h0o/0mFwMxZ5DXiDuAQpBjUE0vpfnrp9i4vealM4IM4PxM4wFhwSk2/bGOmcUDf
7eL7Y+Wn9G+OKIKQiUVTukc2tOqfQQF5iIXVpRWWRvYerUrouTlHP4UA7sUvVqRP
tEQwTeUK0cYQNc4bc8bTlHhRPGoMglP65ICJ8Ws3s8Z/wu4Tjwmt6oOekrDoCaJ4
vFjMlYTN0F7mHSeu2FdqfRDxMJlfSG4Ryy7DLbfhGkZjNtqx+2ex+tXLJp33lmyC
bF1swI1Cj1n2SrseaePIOt7jjuGZ5ehcfWRQThIHyPfNxqYdglRlomtUsrz0T74J
llG/ZYhE/8phvmXh98Ts
=Doze
-----END PGP SIGNATURE-----
```

Alice receives the bid for the share and decides to accept the contract. In order to do so, Alice digitally signs the contract using her *one-time* **private** *key* and forwards it to the Bob and the mutually selected arbiter of choice for triple-signing and the creation of a multisig address. Once Bob has transferred funds to the multisig address, Alice must publicly **revoke** her *one-time keypair*, preventing her from transferring the share contract to any other individual after a sale to Bob. The revocation message will contain the following information and format:

1. The share nonce
2. Alice's *one-time* **public** *key*
3. The hash of Bob's *one-time* **public** *key*
4. The hash of the arbiter's public key
5. The hash of triple-signed contract

The revocation message is digitally signed with Alice's *one time* **private** *key*. The *one time keypair* is only considered **revoked** once it has been published to a distributed ledger of *one time key* revocations. The following is an example of a revocation message:

```xml
<?xml version="1.0"?>

<share_nonce> 356a192b7913b04c54574d18c28d46e6395428ab </share_nonce>
<seller_1tpubkey>
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.22 (MingW32)

mQENBFOUVtMBCADQrxbfRgyk+9QSqutapr/qfCzcaEetwrIg+eGRo4PhyrwbxQAl
G8iBO2ehQunecTVKVL23JqHk0JssOhTMZgDdurBp4IR5N3mXp9WwbGig4llmjRmr
fIS8LzvH0fxGM6YaARj8vRv5O8SyEGBwBUx6YZxOg/6McXLvWMpIai0k5l34qgD/
LJoD6xN3kvruuD7ezgLiPlKSzctVzJ2zWwGdBqxEyQdXAyWN/s+2GduA3I5X3znA
eagqXIEh9ML6csssoLizXlto4KBvOWL7RhGsEjMqFtey3vNX3YiOzwvQ1Gmo+CXy
TuIb7vAYGyIx+NCrN44hSOiQSR1HLjRCbKPtABEBAAG0LkR1ZGUgRHVkZSAoVGhp
cyBpcyBmb3IgYSBkdWRlKSA8ZHVkZUBkdWRlLmNvbT6JATkEEwECACMFAlOUVtMC
Gw8HCwkIBwMCAQYVCAIJCgsEFgIDAQIeAQIXgAAKCRAlH0rab4VOaHKXCAC91hx3
YG/QFYcgUAACviNrfFb98buC1gCRwz9k8nEk5/3K8VMOePgMTfKH5y/at1lzWRHR
cNIjuHV4ZTtv49d7WkJGoq0ir0EImAECWEakKv6RnlGqNp85O+SQh6gVjP4diK41
ypAYm01ZKkRUVFUWQD3dWv3t0m/eDDR0pYLPKeXp6Y7kNJYwrniWkPSBLW13Ei5x
EKlq8HFUXzXFnVNwBs2xmHsfOkDMQ6f4tzm30QYSl429+xi2yyuT4OW7c8Z7lf1R
fV+Cr27iRcAzKcpEIx7fRpRDPSk5NUezbdcyovb+qMPjKt9IP2ffbOjDiGg6zxnP
kjCDTRboSuog4Ljj
=6x5D
-----END PGP PUBLIC KEY BLOCK-----
</seller_1tpubkey>
<buyer_1tpubkey> 8a2da05455775e8987cbfac5a0ca54f3f728e274 </buyer_1tpubkey>
<arbiter_pubkey> 6a839aaeac978584b12ae1868e3d0010d1d53b11 </arbiter_pubkey>
<triplesig_contract> 2e3c0feeabaeb595f91f6dcc1639939ea012c490 </triplesig_contract>

<!-- Digitial Signature -->
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.0.22 (MingW32)

iQEcBAABAgAGBQJTlFcpAAoJECUfStpvhU5oEHoH+wehggEUsUqXkRP6L8m7XOj3
MvXEBEoXnD8e7UXC414iCu3bvOwD8qP4Bd1PuLcUbDOBDWSaOgy2a0rHQCZyJa9J
COxEViFvVU/zKaUcsWqI4+9HNweGIpZh5LgP1fI6nVLNKgoQ5kiQzdqQkgs9Ntqq
amxnjGyG0282HaGWMjvJbHAQwbTj5PExAPSItfYURZfuk2kJOekX4w7Cj2EFufIV
57fnOQqbhwUMkexQGEXQ1+/rXC0vv5Cq5bACi1DBc+IXVffjipLh2NAHIngYm8ng
N4cLuFCAfT7zrm8sQhI70OLhpsXcXQ1O3jg8Ysr7xhL0I/e4OaxXzPzwyd2Nivs=
=MSdE
-----END PGP SIGNATURE-----
```

After Bob and arbiter can confirm that the revocation message has been generated and published to the distributed ledger of *one-time key* revocations, the funds are released from the multisig address. The triple signed contract serves as a proof of ownership transfer from Alice to Bob.

The final measure to prevent Alice, or subsequently Bob, double-spending the share contract is for the *share nonce* to be hashed after every transfer (share nonce throttling). Within the triple-signed contract, root *share nonce*, previous and current hashes of the *nonce* can be included as fields. Any attempts to sell the same *share nonce* or use the same *one-time keys* twice can easily be detected by cross-referencing against the distributed ledger of *one-time key* revocations.

The new owner of a share contract can also to request the issuer to digitally resign the contract as an additional means of validating the share contract. Although the issuer's digital signature should only be relied upon as a secondary means of verifying the validity of the share contract. 

![0](http://s22.postimg.org/yjatvqbsh/Images_2.png)

### Part 4: Distributed Ledger of One-Time Key Revocations

The distributed ledger of *one-time key* revocations is not like the blockchain as individuals do not need to host the entire revocation ledger. Users (buyers, sellers, arbiters) can also host a revocation ledger for transactions that they have participated in, which they have an incentive to host to prevent potential disputes and attempts at double-spends. The share issuer, shareholders, arbiters, or altruistic users may decide to host a copy of the revocation ledger for the company's share alone. There is particular incentive for share issuers and arbiters to host revocation ledgers for their shares, in order to preserve the integrity of their shares being traded within *OpenBazaar*. The number of copies of a revocation ledger is irrelevant provided that at least a single copy of a valid digital signature exists of a revocation message.

## Conclusion

In this article we propose a system called 'one-time key revocation asset transfer' (OTK-RAT) as a means of P2P transfers of share contracts within *OpenBazaar*, without resorting to a trusted third party or blockchain. While the market will decide the preferred process of transferring shares between peers on *OpenBazaar*, OTK-RAT is yet another means for users to consider.
