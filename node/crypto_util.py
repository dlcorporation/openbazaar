import pyelliptic as ec
import json
import arithmetic


def pubkey_to_pyelliptic(pubkey):
    # Strip 04
    pubkey = pubkey[2:]

    # Split it in half
    pub_x = pubkey[0:len(pubkey) / 2]
    pub_y = pubkey[len(pubkey) / 2:]

    # Add pyelliptic content
    print "02ca0020" + pub_x + "0020" + pub_y
    return "02ca0020" + pub_x + "0020" + pub_y


# UNUSED IN THE PROJECT
def load_crypto_details(store_file):
    with open(store_file) as f:
        data = json.loads(f.read())
        f.close()
    assert "nickname" in data
    assert "secret" in data
    assert "pubkey" in data
    assert len(data["secret"]) == 2 * 32
    assert len(data["pubkey"]) == 2 * 33

    return data["nickname"], data["secret"].decode("hex"), \
        data["pubkey"].decode("hex")


def makePrivCryptor(privkey):
    privkey_bin = '\x02\xca\x00 ' + arithmetic.changebase(privkey,
                                                          16, 256, minlen=32)
    pubkey = arithmetic.changebase(arithmetic.privtopub(privkey),
                                   16, 256, minlen=65)[1:]
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
