# Distributed Currency Exchange on *OpenBazaar*

<img src="http://s29.postimg.org/82z3qgz87/Open_Bazaar_Banner.png" width="800px"/>

## Introduction
*OpenBazaar* allows for the decentralised exchange of types of currencies using the flexible Ricardian contract system. Currency exchanges are not limited trades between crypto-currencies, but can also facilitate exchanges with fiat currencies using reverisble and non-reversible payment systems. 

## Currency Exchanges
Fundamentally, currency exchanges require a matching of buy and sell orders at a certain price for a given volume. Firstly, buy and sell orders will be created and issued as a Ricardian contract, formatted according to a specialised 'currency' template in *OpenBazaar*. Secondly, matching buy and sell orders theoretically will be mediated over *exchange nodes*, which may also function as arbiters for each exchange. Alternative, buy and sell orders may be matched over the *OpenBazaar* distributed hash table. Finally, private exchanges can be made between peers, using *OpenBazaar* to merely faciliate the signing/counter-signing of the contract and finding an arbiter for the trade. After matching buy and sell order, the use of Bitcoin multisignature transactions is the key to managing counterparty risk for an exchange between different crypto-currencies, irrespective of whether Bitcoin is the final currency to be exchanged. 

Currency contract can be further sub-categorised into:

1. Crypto-Crypto currency exchanges
2. Crypto-Fiat currency exchanges
3. Fiat-Fiat currency exchanges

### 1. Crypto-Crypto Currency Exchanges
To create a currency Ricardian contract for a crypto-crypto exchange, a *seed contract* is prepared with the following data fields:

1. Crypto-currency pair (e.g. Litecoin/Bitcoin; LTC/BTC)
2. Exchange rate for the currency pair (e.g. 0.01637)
3. Type (i.e buy, sell)
4. Size (i.e. amount of the currency to buy/sell)
5. Payment address

For example, Alice desires to purchase 5 litecoin for a price of 0.01637 LTC/BTC (0.08185 BTC total). She draws up the following *seed contract* and broadcasts it on *OpenBazaar*:

```JSON
{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Currency",
        "Sub-category,": "Crypto-Crypto",
        "Nonce": "356a192b7913b04c54574d18c28d46e6395427ab",
        "Expiration":"2014-08-29 12:00:00"
        },
    "Seller": {
        "NymID": "61768db8d1a38f1c16d3e6eea812ef423c739068",
        "NodeID": "abc123",
        "BTCuncompressedpubkey":"044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01565b838e06af0b",
        "publicKey": [
            "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",
            "=dDLn"
            ]
        },
    "Currency": {
        "CurrencyPair": "LTC/BTC",
        "ExchangeRate": "0.01637",
        "Type": "Buy",
        "Size": "5",
        "PaymentAddress": "Lbnu1x4UfToiiFGU8MvPrLpj2GSrtUrxFH"
        }
}
```

A prospective buyer only needs to submit a *bid offer* by appending the following data to the *seed contract*:

1. Buyer details
2. Payment address

As with all Ricardian contracts on *OpenBazaar*, digital signatures are required at each step. 

### 2. Crypto-Fiat Currency Exchanges
For a crypto-fiat exchange, the *seed contract* will have the following data fields:

1. Crypto-Fiat currency pair (e.g. Bitcoin/US dollar; BTC/USD)
2. Exchange rate for the currency pair (e.g. 0.00167)
3. Type (i.e buy, sell)
4. Size (i.e. amount of the currency to buy/sell)
5. Payment address/bank details (this data field can be blinded until funds are transferred to the bitcoin multisignature escrow address)

For example, Alice desires to purchase 5 bitcoin for a price of 0.00167 BTC/USD ($3000 USD total). She creates the following *seed contract* and broadcasts it on *OpenBazaar*:

```JSON
{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Currency",
        "Sub-category,": "Crypto-Fiat",
        "Nonce": "356a192b7913b04c54574d18cd8d46e6395427ab",
        "Expiration":"2014-08-29 12:00:00"
        },
    "Seller": {
        "NymID": "61768db8d1a38f1c16d3e6eea812ef423c739068",
        "NodeID": "abc123",
        "BTCuncompressedpubkey":"044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01565b838e06af0b",
        "publicKey": [
            "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",
            "=dDLn"
            ]
        },
    "Currency": {
        "CurrencyPair": "USD/BTC",
        "ExchangeRate": "0.00167",
        "Type": "Buy",
        "Size": "5",
        "PaymentAddress": "1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN"
        }
}
```

On the other side of the trade, the buyer (Bob) submits a *bid offer* by appending the following data to the *seed contract*:

1. Buyer details
2. Bank details (blinded)
  - The bank details can be hashed and included in a single data field
  - Later the source bank details can be revealed to the buyer and arbiter, who can verify the authenticity of the hash

The contract with the buyer's digital signature is sent back to the seller (Alice), which can be signed and forwarded to the arbiter for creation of the multisignature escrow address. Bob transfers 5 BTC to the multisignature address and reveals his bank details to Alice and the arbiter. Bob then awaits for the fiat funds to arrive in his account before signing a release of the funds from the multisig address to Alice.

#### Chargeback Risk

If an irreversible payment processor (e.g. OKPay) is used, then the multisignature bitcoin address is a sufficient means of managing the exchange risk as chargebacks are theoretically impossible. However, if Alice in this case did not use such an non-reverisble payment processor, the trade can still occur with the punative measures to appropriately manage the charageback risk:

1. Probation
  - The purchased bitcoin funds are kept within the multisignature address until the chargeback risk duration has elapsed. This period will be variable, depending on the bank that is used.
2. Surety bond
  - The seller can post a surety bond (refundable security deposit of bitcoin within multisignature address) for the partial or full amount of funds to be exchanged. This allows the seller to access the exchanged bitcoin immediately. While this appears to be a zero-sum game for a single trade, a regular trader may set aside a pool of funds to be re-used as a surety bond after every trade.

### 3. Fiat-Fiat Currency Exchanges
For a fiat-fiat exchange, the *seed contract* will need the following data fields:

1. Fiat-fiat currency pair (e.g. Euro/US dollar; EUR/USD)
2. Exchange rate for the currency pair (e.g. $1.36 EUR/USD)
3. Type (i.e buy, sell)
4. Size (i.e. amount of the currency to buy/sell)
5. Bank details (this data field can be blinded until funds are transferred to the bitcoin multisignature escrow address)

For example, Alice desires to purchase $100 Euro for a price of $1.36 EUR/USD ($136.48 USD total). She creates the following *seed contract* and broadcasts it on *OpenBazaar*:

```JSON
{
    "OpenBazaar Contract": {
        "OBCv": "0.1",
        "Category": "Currency",
        "Sub-category,": "Crypto-Fiat",
        "Nonce": "356a192b7913b04c54574d18cd8d46e6395427ab",
        "Expiration":"2014-08-29 12:00:00"
        },
    "Seller": {
        "NymID": "61768db8d1a38f1c16d3e6eea812ef423c739068",
        "NodeID": "abc123",
        "BTCuncompressedpubkey":"044448c02963b8f5ba1b8f7019a03b57c80b993313c37b464866efbf61c37098440bcdcc88bedf7f1e9c201e294cf3c064d39e372692a0568c01565b838e06af0b",
        "publicKey": [
            "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",
            "=dDLn"
            ]
        },
    "Currency": {
        "CurrencyPair": "EUR/USD",
        "ExchangeRate": "$1.36",
        "Type": "Buy",
        "Size": "100",
        "BankDetails": "8c2226df637baf568e26c042dc376f5d4a1492e8"
        }
}
```

The buyer, Bob, submits a *bid offer* for the *seed contract* by appending:

1. Buyer details
2. Bank details (blinded)

The double-signed contract is sent to the arbiter for the creation of the multisignature escrow address. Both the buyer and seller transfer bitcoin to the address as collateral for their fiat exchange.

As for chargeback risk, it is clearly preferable for both parties to use a non-reversible payment processor. In the absence of this, the bitcoin collateral would not be released until the chargeback risk period as elapsed. 

## Listing and Matching Buy/Sell Orders on *OpenBazaar*

### 1. DHT Listing
Following the [Bitsqaure model](http://Bitsquare.io), the buy and sell orders are listed in the DHT (for a fee, which I'd like to avoid). The client then matches the buy and sell orders and places both parties in contact with each other over the network. Contracts can be found using the inverse keyword search on *OpenBazaar's* DHT, which is a Kademlia-like P2P network.

### 2. DarkPool
This model uses a private means of matching buy and sell orders, which I think also encompasses private P2P exchanges between parties that have already discovered each other. In this case, the transfer is fairly straightforward and would proceed as I described under the crypto-crypto section.

### 3. Exchange Nodes
This introduces the concept of a node or groups of nodes where buyers and sellers submit their orders to (Ricardian contracts as described in the article). The exchange matches the buy and sell orders, and is the arbiter for transactions. It will also have responsibility for broadcasting the price on their exchange. So this takes advantage of the benefits of centralisation, but if the exchange is taken out it doesn't cripple the ability for individuals to make currency exchange.

## Conclusion

*OpenBazaar* can be used as a decentralised currency exchange platform for multiple currency types. These proposals are a primer for the *OpenBazaar* community to develop near trustless systems for the distributed exchange of various currencies using Ricardian contracts.
