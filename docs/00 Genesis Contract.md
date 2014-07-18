# *OpenBazaar* Genesis Contract

<img src="http://s29.postimg.org/82z3qgz87/Open_Bazaar_Banner.png" width="800px"/>

The following article contains *OpenBazaar's* first ever Ricardian contract for the sale of a good between Sam Patterson and Brian Hoffman, arbitrated by Dr Washington Sanchez. In short, the signing process follows these steps:

1. Creation of the *seed contract* by the **seller**
  - The **seller** creates a contract to sell a good
2. Creation of a *bid offer* for the contract by the **buyer**
  - The **buyer** appends their details to the *seed contract* and digitally signs it
  - The signed contract is called the *bid offer* and is sent back to the **seller**
3. *Double-signing* of the *bid offer* by the seller.
  - The **seller** digitally signs the *bid offer* to accept the contract
  - Consensus to the terms of the exchange is now achieved by both **buyer** and **seller**
4. *Triple-signing* of the completed contract by the arbiter and creation of the multisignature escrow Bitcoin address
  - The *double-signed* contract is sent to the pre-selected **arbiter**
  - The **arbiter** appends the multisignature escrow address (2-of-3: **buyer**, **seller**, **arbiter**)
  - The **arbiter** digitally signs the contract, which is sent to all parties, awaiting transfer of funds from the **buyer** to the multisig escrow address
5. *Receipt* of a completed trade is issued by one of the parties

This process would be used if one or more of the parties are not online at one time to create the finished contract from scratch, requiring the contract to be sent back and forth between the parties in order to establish authenticated consensus for the terms of the exchange. Ideally, if all the parties are online at one time, the contract can be written in its entirety, appending the detached digital signatures of each party.

## Case Study: Sam wants to sell a USB stick to Brian

### 1. *Seed Contract*

Sam creates the *seed contract*.

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1
 
{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Physical good",
        "Sub-category,": "Ask price: negotiable",
        "Nonce": "01",
        "Expiration": "2014-06-29 12:00:00"
    },
    "Seller": {
        "NymID": "Samuel Patterson",
        "NodeID": "SamPatt",
        "BTCuncompressedpubkey": "044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01565b838e06af0b",
        "PGPpublicKey": [
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
        ]
    },
    "Physical Good Contract": {
        "ItemName": "1 USB Drive - 256MB",
        "Currency": "Bitcoin",
        "Price": "0.0026",
        "Description": [
            "Stores crap."
        ],
        "Delivery": {
            "Country": "USA",
            "Region": "All States",
            "EstimatedDelivery": "13 days after triple-signing",
            "PostagePrice": "Included in the item price"
        }
    }
}
-----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47
 
iQFGBAEBAgAwBQJTqLUmKRxTYW0gUGF0dGVyc29uIDxzYW1Ac2FtdWVscnBhdHRl
cnNvbi5jb20+AAoJEIjRSgb/sqCO6BAH/1D5jDN6Ue9IQnXXqJVH8jRi0wOkkVkr
/WyYuUjMxd3vfAmU+aaWyVpMIRuXo/DSzxBmI2HzxRh6s/fJCrufKGzKLfxT+asB
14JHzpFKOgVcbvLRoFdspF20tEgsM1a82iCyAjZptGMb4QON0ibvSAKELXlbvMDJ
NnZ4vHS9TK/7y4nkqTPY6V6jSdpD2aCog9ktGY1Si2DsuZhs1J3kVlzBY4zYKQG8
rNTWCkx5MfAKXK96OcSjs9SZBOOC7iNQQJMg4Nx3O/waALe5hqE1z5U5SSAJRjtT
sBPhClPME2wQm96lYTAgbWal1Tm4Ly4AvhWUHTBjsakpSBKeYBTxTnU=
=UO2C
-----END PGP SIGNATURE-----
```

### 2. *Bid Offer*

Brian creates a *bid offer* from the *seed contract*.

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

- -----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Physical good",
        "Sub-category,": "Ask price: negotiable",
        "Nonce": "01",
        "Expiration": "2014-06-29 12:00:00"
    },
    "Seller": {
        "NymID": "Samuel Patterson",
        "NodeID": "SamPatt",
        "BTCuncompressedpubkey": "044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01565b838e06af0b",
        "PGPpublicKey": [
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
        ]
    },
    "Physical Good Contract": {
        "ItemName": "1 USB Drive - 256MB",
        "Currency": "Bitcoin",
        "Price": "0.0026",
        "Description": [
            "Stores crap."
        ],
        "Delivery": {
            "Country": "USA",
            "Region": "All States",
            "EstimatedDelivery": "13 days after triple-signing",
            "PostagePrice": "Included in the item price"
        }
    }
}
- -----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47

iQFGBAEBAgAwBQJTqLUmKRxTYW0gUGF0dGVyc29uIDxzYW1Ac2FtdWVscnBhdHRl
cnNvbi5jb20+AAoJEIjRSgb/sqCO6BAH/1D5jDN6Ue9IQnXXqJVH8jRi0wOkkVkr
/WyYuUjMxd3vfAmU+aaWyVpMIRuXo/DSzxBmI2HzxRh6s/fJCrufKGzKLfxT+asB
14JHzpFKOgVcbvLRoFdspF20tEgsM1a82iCyAjZptGMb4QON0ibvSAKELXlbvMDJ
NnZ4vHS9TK/7y4nkqTPY6V6jSdpD2aCog9ktGY1Si2DsuZhs1J3kVlzBY4zYKQG8
rNTWCkx5MfAKXK96OcSjs9SZBOOC7iNQQJMg4Nx3O/waALe5hqE1z5U5SSAJRjtT
sBPhClPME2wQm96lYTAgbWal1Tm4Ly4AvhWUHTBjsakpSBKeYBTxTnU=
=UO2C
- -----END PGP SIGNATURE-----
    "Buyer": {
        "NymID": "Brian Hoffman",
        "NodeID": "brianhoffman",
        "BTCuncompressedpubkey": "047c18cb94c75934de10c067b0085ff18f933e0a8fc06707dbec6ade33ec5ab9e451e73cf53b9eead130e87d1e4145b4a62a87661d2f68508f8dcf5c539a67b71c",
        "PGPpublicKey": [
            "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",
            "Z0oLprd+yduIIH0=",
            "=dGBY"
        ]
    },
    "Arbiter": {
        "NymID": "Dr Washington Sanchez",
        "NodeID": "drwasho",
        "BTCuncompressedpubkey": "04d09c05c84a73344ee3b03d03fdf4a6bff2b1c4e15ffeb7403b91b0815be8b03ee50ade6b28d27aabc7c56cf679f74acec3d8e760595f5878caec12edd32938ea",
        "DisputeFee": "10 percent of item price",
        "PGPpublicKey": [
            "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",
            "=G1fD"
        ]
    }
}
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1
Comment: GPGTools - https://gpgtools.org

iQEcBAEBCgAGBQJTqtfbAAoJEN/utaJDj6F8pU4IAKYLfVcDFsL2Faq5K4GJ4yRT
lsjd2Zb0uJKNehYs4OABtN3CWeRWbg+9CgxccPnlN1F6rsubWRHvAU50S2QBJgqp
MbfIeMiUxdbhXNCBKLURuZ7wjphRTyOjzxTgJBapy8m0a1jHp4uqqAb5ASNe5Ov3
9VKYo/vy86txzLfFnETZSvEvJjjJ6RzppZGz5wScBIsCZLyFTaN6g0B54WBAfia/
fdKpDMWvNOd0nxCqCIQzASrdKwGw1Sjpm37syuzRDHNnsdmtDKDkcEXStxA8diys
UN3fXcKUSbAT35qUjAqvn1ee1p465QtDBvpJLtZKCHMBN/gdYL1WEgg4MCsQCsY=
=x4o/
-----END PGP SIGNATURE-----
```

### 3. *Double-Signed Contract*

Sam digitally signs Brian's *bid offer* to accept his offer.


```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

- -----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

- - -----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Physical good",
        "Sub-category,": "Ask price: negotiable",
        "Nonce": "01",
        "Expiration": "2014-06-29 12:00:00"
    },
    "Seller": {
        "NymID": "Samuel Patterson",
        "NodeID": "SamPatt",
        "BTCuncompressedpubkey": "044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01565b838e06af0b",
        "PGPpublicKey": [
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
        ]
    },
    "Physical Good Contract": {
        "ItemName": "1 USB Drive - 256MB",
        "Currency": "Bitcoin",
        "Price": "0.0026",
        "Description": [
            "Stores crap."
        ],
        "Delivery": {
            "Country": "USA",
            "Region": "All States",
            "EstimatedDelivery": "13 days after triple-signing",
            "PostagePrice": "Included in the item price"
        }
    }
}
- - -----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47

iQFGBAEBAgAwBQJTqLUmKRxTYW0gUGF0dGVyc29uIDxzYW1Ac2FtdWVscnBhdHRl
cnNvbi5jb20+AAoJEIjRSgb/sqCO6BAH/1D5jDN6Ue9IQnXXqJVH8jRi0wOkkVkr
/WyYuUjMxd3vfAmU+aaWyVpMIRuXo/DSzxBmI2HzxRh6s/fJCrufKGzKLfxT+asB
14JHzpFKOgVcbvLRoFdspF20tEgsM1a82iCyAjZptGMb4QON0ibvSAKELXlbvMDJ
NnZ4vHS9TK/7y4nkqTPY6V6jSdpD2aCog9ktGY1Si2DsuZhs1J3kVlzBY4zYKQG8
rNTWCkx5MfAKXK96OcSjs9SZBOOC7iNQQJMg4Nx3O/waALe5hqE1z5U5SSAJRjtT
sBPhClPME2wQm96lYTAgbWal1Tm4Ly4AvhWUHTBjsakpSBKeYBTxTnU=
=UO2C
- - -----END PGP SIGNATURE-----
    "Buyer": {
        "NymID": "Brian Hoffman",
        "NodeID": "brianhoffman",
        "BTCuncompressedpubkey": "047c18cb94c75934de10c067b0085ff18f933e0a8fc06707dbec6ade33ec5ab9e451e73cf53b9eead130e87d1e4145b4a62a87661d2f68508f8dcf5c539a67b71c",
        "PGPpublicKey": [
            "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",
            "Z0oLprd+yduIIH0=",
            "=dGBY"
        ]
    },
    "Arbiter": {
        "NymID": "Dr Washington Sanchez",
        "NodeID": "drwasho",
        "BTCuncompressedpubkey": "04d09c05c84a73344ee3b03d03fdf4a6bff2b1c4e15ffeb7403b91b0815be8b03ee50ade6b28d27aabc7c56cf679f74acec3d8e760595f5878caec12edd32938ea",
        "DisputeFee": "10 percent of item price",
        "PGPpublicKey": [
            "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",
            "=G1fD"
        ]
    }
}
- -----BEGIN PGP SIGNATURE-----
Version: GnuPG v1
Comment: GPGTools - https://gpgtools.org

iQEcBAEBCgAGBQJTqtfbAAoJEN/utaJDj6F8pU4IAKYLfVcDFsL2Faq5K4GJ4yRT
lsjd2Zb0uJKNehYs4OABtN3CWeRWbg+9CgxccPnlN1F6rsubWRHvAU50S2QBJgqp
MbfIeMiUxdbhXNCBKLURuZ7wjphRTyOjzxTgJBapy8m0a1jHp4uqqAb5ASNe5Ov3
9VKYo/vy86txzLfFnETZSvEvJjjJ6RzppZGz5wScBIsCZLyFTaN6g0B54WBAfia/
fdKpDMWvNOd0nxCqCIQzASrdKwGw1Sjpm37syuzRDHNnsdmtDKDkcEXStxA8diys
UN3fXcKUSbAT35qUjAqvn1ee1p465QtDBvpJLtZKCHMBN/gdYL1WEgg4MCsQCsY=
=x4o/
- -----END PGP SIGNATURE-----
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.11 (GNU/Linux)

iQEcBAEBAgAGBQJTq04eAAoJEIjRSgb/sqCOZlkH/jt+L184Q4GtNmvKSG3esu37
AdEez8wE6a8iwUdlVkaG3bUhSPwvgPv8H9obXhCeDPA4mYDMoRrf3VO1n3ucxf7T
736/d9W6wA3nDjA6kbeGwDDYBfb3tDO0PNANc7roConHDz0Dm3ibcfgqM8baSMbM
kePeP7tXxO/TP0/NFHbZk2Xiv+xAMODPHGPSI3Gs+tGTy+JbxcUmNZrs+bt26X0d
FBbldmdD6k4SbxVDMR0MwISmhXeFRZ4MAy+k9o0ODE3d3+QcMWnVTZ6zdd7TD8L3
YbIH4rcahN09gVwlfvfzG1Kw56KAxRVTse5A/em0djOTBTKrZbtxniY7v1fIf7o=
=hFVq
-----END PGP SIGNATURE-----
```

### 4. *Triple-Signed Contract*

Washington (the arbiter) appends to the double-signed contract the multisignature escrow address and redemption script, and finally digitally signs the *double-signed* contract.

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

- -----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

- - -----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

- - - -----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Physical good",
        "Sub-category,": "Ask price: negotiable",
        "Nonce": "01",
        "Expiration": "2014-06-29 12:00:00"
    },
    "Seller": {
        "NymID": "Samuel Patterson",
        "NodeID": "SamPatt",
        "BTCuncompressedpubkey": "044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01565b838e06af0b",
        "PGPpublicKey": [
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
        ]
    },
    "Physical Good Contract": {
        "ItemName": "1 USB Drive - 256MB",
        "Currency": "Bitcoin",
        "Price": "0.0026",
        "Description": [
            "Stores crap."
        ],
        "Delivery": {
            "Country": "USA",
            "Region": "All States",
            "EstimatedDelivery": "13 days after triple-signing",
            "PostagePrice": "Included in the item price"
        }
    }
}
- - - -----BEGIN PGP SIGNATURE-----
Version: BCPG v1.47

iQFGBAEBAgAwBQJTqLUmKRxTYW0gUGF0dGVyc29uIDxzYW1Ac2FtdWVscnBhdHRl
cnNvbi5jb20+AAoJEIjRSgb/sqCO6BAH/1D5jDN6Ue9IQnXXqJVH8jRi0wOkkVkr
/WyYuUjMxd3vfAmU+aaWyVpMIRuXo/DSzxBmI2HzxRh6s/fJCrufKGzKLfxT+asB
14JHzpFKOgVcbvLRoFdspF20tEgsM1a82iCyAjZptGMb4QON0ibvSAKELXlbvMDJ
NnZ4vHS9TK/7y4nkqTPY6V6jSdpD2aCog9ktGY1Si2DsuZhs1J3kVlzBY4zYKQG8
rNTWCkx5MfAKXK96OcSjs9SZBOOC7iNQQJMg4Nx3O/waALe5hqE1z5U5SSAJRjtT
sBPhClPME2wQm96lYTAgbWal1Tm4Ly4AvhWUHTBjsakpSBKeYBTxTnU=
=UO2C
- - - -----END PGP SIGNATURE-----
    "Buyer": {
        "NymID": "Brian Hoffman",
        "NodeID": "brianhoffman",
        "BTCuncompressedpubkey": "047c18cb94c75934de10c067b0085ff18f933e0a8fc06707dbec6ade33ec5ab9e451e73cf53b9eead130e87d1e4145b4a62a87661d2f68508f8dcf5c539a67b71c",
        "PGPpublicKey": [
            "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",
            "Z0oLprd+yduIIH0=",
            "=dGBY"
        ]
    },
    "Arbiter": {
        "NymID": "Dr Washington Sanchez",
        "NodeID": "drwasho",
        "BTCuncompressedpubkey": "04d09c05c84a73344ee3b03d03fdf4a6bff2b1c4e15ffeb7403b91b0815be8b03ee50ade6b28d27aabc7c56cf679f74acec3d8e760595f5878caec12edd32938ea",
        "DisputeFee": "10 percent of item price",
        "PGPpublicKey": [
            "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",
            "=G1fD"
        ]
    }
}
- - -----BEGIN PGP SIGNATURE-----
Version: GnuPG v1
Comment: GPGTools - https://gpgtools.org

iQEcBAEBCgAGBQJTqtfbAAoJEN/utaJDj6F8pU4IAKYLfVcDFsL2Faq5K4GJ4yRT
lsjd2Zb0uJKNehYs4OABtN3CWeRWbg+9CgxccPnlN1F6rsubWRHvAU50S2QBJgqp
MbfIeMiUxdbhXNCBKLURuZ7wjphRTyOjzxTgJBapy8m0a1jHp4uqqAb5ASNe5Ov3
9VKYo/vy86txzLfFnETZSvEvJjjJ6RzppZGz5wScBIsCZLyFTaN6g0B54WBAfia/
fdKpDMWvNOd0nxCqCIQzASrdKwGw1Sjpm37syuzRDHNnsdmtDKDkcEXStxA8diys
UN3fXcKUSbAT35qUjAqvn1ee1p465QtDBvpJLtZKCHMBN/gdYL1WEgg4MCsQCsY=
=x4o/
- - -----END PGP SIGNATURE-----
- -----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.11 (GNU/Linux)

iQEcBAEBAgAGBQJTq04eAAoJEIjRSgb/sqCOZlkH/jt+L184Q4GtNmvKSG3esu37
AdEez8wE6a8iwUdlVkaG3bUhSPwvgPv8H9obXhCeDPA4mYDMoRrf3VO1n3ucxf7T
736/d9W6wA3nDjA6kbeGwDDYBfb3tDO0PNANc7roConHDz0Dm3ibcfgqM8baSMbM
kePeP7tXxO/TP0/NFHbZk2Xiv+xAMODPHGPSI3Gs+tGTy+JbxcUmNZrs+bt26X0d
FBbldmdD6k4SbxVDMR0MwISmhXeFRZ4MAy+k9o0ODE3d3+QcMWnVTZ6zdd7TD8L3
YbIH4rcahN09gVwlfvfzG1Kw56KAxRVTse5A/em0djOTBTKrZbtxniY7v1fIf7o=
=hFVq
- -----END PGP SIGNATURE-----
{
    "Escrow": {
        "MultiSigAddr": "35MgRri9sk2d8xB7PF75D2icF9cm4R2ddd",
        "RedemptionScript": [
            "5241044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf",
            "61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01",
            "565b838e06af0b41047c18cb94c75934de10c067b0085ff18f933e0a8fc0",
            "6707dbec6ade33ec5ab9e451e73cf53b9eead130e87d1e4145b4a62a8766",
            "1d2f68508f8dcf5c539a67b71c4104d09c05c84a73344ee3b03d03fdf4a6",
            "bff2b1c4e15ffeb7403b91b0815be8b03ee50ade6b28d27aabc7c56cf679",
            "f74acec3d8e760595f5878caec12edd32938ea53ae"
            ]
        }
}
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.0.22 (MingW32)

iQIcBAEBAgAGBQJTq3EyAAoJEOB4yK6/8jLP5NAQAMYJjyqPIpbtNZNafyOeDJ7v
cQoi1Vj8l8k6jvwu9QAP9zwIYP4ny23SZmd4xVZSumwZsE5RZtU+b9LkXR7MyjXb
4tTS3VnzeXpScheWcWasLWNTzb+Egtohz0BjSBo0GLEmyRYzC4GmPgO6gNYVgEap
X8p+Q6R92/gGZLNarlnRWXqyISOzjhTHHMBEi+T56OrMIHjrs6GJIO7wTeB0yggp
7iXeBC4ePK0l7FgdxrqA+7zDhbcGDQNQ0N922OzvPzCXR5umy7argFIfgtmRmt8s
68fUaSixRdYM0v3Z7XgM9rbnnwJ2o9augQXSugbDjd03FUQf2btqeIY+zNQd+er2
w/qQKCF1lFcBFf6jl02zsY0z1I/K/7z75YcqUX1+zEFqoojxZkMyh+p8DOfwTRaG
sjNhTZ3+w7biMa3UMdbRfMgxcvhCAVdXt5aX4fJF4TRgMMBcy9+DZj8ICeQ+TPHA
OIL2gyBOUlu1ma5q9GSfzlUsl6artbZXlkJSrE28tIuEzL5mi1zZcmfLBWIq/E9b
oVGCYG4zWxPHxciUALVBt4ib2BFOYaHcRl5toTFMv/KE6lHyRHThzFkP02BAiXFP
u+59qYP1XA9v0Z81ww+20OC1YCCwnm5KtBEpOeqgrYRsEM/CbvrZ9aYGBu5LPBIj
1E52Cex76HI7dmsnKJK9
=RCU5
-----END PGP SIGNATURE-----
```

### 5. *Receipt*

Theoretically any party involved in the exchange can issue a receipt for a successful exchange. It can be assumed that if funds are transferred from the multisig escrow address to the seller without the intervention of the arbiter, then it reasonably safe to assume that the goods arrived and the trade can be considered successful, without disputes. Once the funds have been transferred, the buyer can append the transaction details to the contract, make a final digital signature and distribute it to the other parties of the trade.
