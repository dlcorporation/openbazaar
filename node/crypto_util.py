import pyelliptic as ec
from pybitcointools import main as arithmetic


def pubkey_to_pyelliptic(pubkey):
    # Strip 04
    pubkey = pubkey[2:]

    # Split it in half
    pub_x = pubkey[0:len(pubkey) / 2]
    pub_y = pubkey[len(pubkey) / 2:]

    # Add pyelliptic content
    print "02ca0020" + pub_x + "0020" + pub_y
    return "02ca0020" + pub_x + "0020" + pub_y


def makePrivCryptor(privkey_hex):
    privkey_bin = '\x02\xca\x00 ' + arithmetic.changebase(privkey_hex,
                                                          16, 256, minlen=32)
    pubkey_hex = arithmetic.privkey_to_pubkey(privkey_hex)
    pubkey_bin = arithmetic.changebase(pubkey_hex, 16, 256, minlen=65)[1:]
    pubkey_bin = '\x02\xca\x00 ' + pubkey[:32] + '\x00 ' + pubkey[32:]
    cryptor = ec.ECC(curve='secp256k1', privkey=privkey_bin, pubkey=pubkey_bin)
    return cryptor


def makePubCryptor(pubkey):
    pubkey_bin = hexToPubkey(pubkey)
    return ec.ECC(curve='secp256k1', pubkey=pubkey_bin)


def hexToPubkey(pubkey):
    pubkey_raw = arithmetic.changebase(pubkey[2:], 16, 256, minlen=64)
    pubkey_bin = '\x02\xca\x00 ' + pubkey_raw[:32] + '\x00 ' + pubkey_raw[32:]
    return pubkey_bin
