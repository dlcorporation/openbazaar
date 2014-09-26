<img src="https://blog.openbazaar.org/wp-content/uploads/2014/07/logo.png" width="500px"/>

# Risk and Insurance in *OpenBazaar*

## 1.0 Introduction

Insurance is a valuable service that is often misinterpreted, over-regulated, and out of reach for many people. On *OpenBazaar*, insurance is contextualized as a service that can be offered by anyone or group, leveraging: 

1. The clarity of terms and conditions set out in a Ricardian contract
2. An open marketplace for competing insurance policies and service providers
3. The transparency that crypto-currencies provide via the blockchain

Ultimately, the market will decide the most appropriate insurance service and contract models for *OpenBazaar*. In this article, we propose some potential implementations as a primer for future development. 

## 2.0 Insurance Services 

Insurance services fundamentally offer: 

1. A pool of funds to offset a cost that exceeds the capacity of the client to pay within a timely manner
2. A pool of funds to compensate another party that has been wronged by actions of the client, which addresses their capacity to pay within a reasonable time frame
3. A dispute resolution organization that represents the interests of the client

These services are of course provided through the lens of *risk assessment* to dictate the price of: 

1. The insurance premium (regular cost of the policy)
2. The excess (fee paid when insurance is triggered). 

Traditional business models of insurance mirror a fractional reserve system in that funds are predominantly reinvested on the statistical reality that it is unlikely for all or even most policies to be triggered at once. Whether this model survives the blockchain era is unknown. The transparency that the blockchain provides may alter consumer preferences for how insurance funds are managed; *proof of solvency* may be an inescapable market-imposed regulation. If so, insurance providers will need to prove that the proportion of funds kept in reserve and those reinvested are at the levels that the policy claims. Alternatively,  conservative insurance providers may keep 100% reserves and seek to raise profits only by fees incorporated into the premium and excess. 

Whatever business model an insurance provider adopts, the terms and conditions of their policy will be listed within a Ricardian contract in *OpenBazaar*, with digital signatures as the unmistakable evidence of agreement.

While the various fields necessary for a comprehensive contract are difficult to predict, the *seed contract* may contain the following core data fields:

```JSON
{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Insurance",
        "Sub-category,": "Car-Insurnace",
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
	"Insurance": {
		"PolicyNonce": "abc123",
		"Term": "12 months",
		"Type": "Car",
		"PolicyValue": "20 BTC",
		"Reserve": "20 percent",
		"Coverage": {
		  "Fire": "True",
		  "Water": "True",
		  "Flood": "False",
		  "AccidentalCrash": {
		    "IFCauseClient": "False",
		    "IFCauseNotClient": "True"
		    	},
			}
		"Client": {
			"Payments": "0.1 BTC"
			"PaymentFreq": "Monthly"
			"Excess": "0.25 BTC"
			},
		}
}
```

When a client takes out an *insurance contract* with a provider, a multisignature transaction is created in combination with the notary's pubkey. The client's insurance funds are paid to the multisignature transaction according to the payment schedule specified within the *insurance contract*. Under the client and/or notary's supervision, the insurance provider cannot extract funds beyond the reserve amount stated in the contract. For large insurance policies, a notary pool can be used for redundancy's sake and to minimize risk for client and insurance provider. Before an *insurance contract* is signed by the client and insurance provider, the latter can provide evidence that they have sufficient funds to payout the full value of the policy (e.g. 20 BTC in the case of the *insurance contract* above).

In the event that the client makes an insurance claim, the client can provide the relevant detail and evidence of the claim to the insurance provider. For a successful claim, the insurer can transfer the required amount directly to the client. If the insurance provider rejects the claim, the client may flag a dispute.

## 3.0 Transaction Insurance on *OpenBazaar*

It is possible for users to take out insurance for trades made over *OpenBazaar*. The purpose of the insurance in this context is to guard against the scenario where a user is subject to a loss of funds and/or goods that **cannot** be recovered. This loss is not necessarily due to fraudulent activity, but also covers the accidental loss of funds/goods in transit (i.e. including acts of God).

For example, Alice sells a cat to Bob on *OpenBazaar*:
1. During transit, the cat escapes and an empty cage is delivered to Bob. Bob refuses to sign a multisignature transaction releasing funds to Alice based on the a perceived violation of the contract. 
2. Alice and Bob flag a dispute and engage an arbiter to weigh up the case in order to determine who should receive the funds. 
3. During the dispute resolution process, Alice provides sufficient evidence that the cat was delivered alive and well to the courier. Likewise, Bob is able to provide evidence that the cage was delivered empty to him by the courier.

If the courier in this example *did not* have a presence on *OpenBazaar* (i.e. outside of its jurisdiction), the arbiter may have no choice but to rule in favor of Bob (according to their arbitration policy). The arbiter instructs the notary (the third signature of the 2-of-3 multisignature escrow address between Alice and Bob) to create and sign a transaction releasing the funds back to Bob.

In this case, Alice was not at fault but ended up suffering the consequences of an uncommon accident, which is an ideal scenario for insurance to cover. If Alice had taken *merchant insurance* for her trade with Bob, she could make a claim to cover the value of the lost good in the failed trade. The insurance provider may launch their own investigation before deciding to award Alice the insurance funds.

If the courier in this example *did* have a presence on *OpenBazaar*, Alice's insurance provider may contact the courier directly or the courier's insurance provider. In the latter case, compensation to Alice can be paid out of the courier's insurance policy funds (most likely after arbitration between both insurance providers).

## 4.0 Conclusion

This article is a primer for future participants of *OpenBazaar* to devise peer-to-peer merchant insurance policies to mitigate against losses in non-malicious failed trades. The Ricardian contract system used by *OpenBazaar* permits insurance contracts to be formed between peers on the network.
