def hello_request(data):
    data['type'] = 'hello_request'
    return data


def hello_response(data):
    data['type'] = 'hello_reply'
    return data


def goodbye(data):
    data['type'] = 'goodbye'
    return data


def ok():
    return {'type': 'ok'}


def shout(data):
    data['type'] = 'shout'
    return data


def proto_welcome():
    return {'type': 'welcome'}


def proto_reputation(pubkey, reviews):
    data = {'type': 'reputation', 'pubkey': pubkey.encode('hex'), 'reviews': reviews}
    return data


def proto_query_reputation(pubkey):
    data = {'type': 'query_reputation', 'pubkey': pubkey.encode('hex')}
    return data


def proto_page(uri, pubkey, guid, text, signature, nickname, PGPPubKey, email, bitmessage, arbiter, arbiter_description):
    data = {'type': 'page', 'uri': uri, 'pubkey': pubkey, 'senderGUID': guid, 'signature': signature.encode('hex'),
            'text': text, 'nickname': nickname, 'PGPPubKey': PGPPubKey, 'email': email, 'bitmessage': bitmessage,
            'arbiter':arbiter,
            'arbiter_description':arbiter_description}
    return data


def query_page(guid):
    data = {'type': 'query_page', 'findGUID': guid}
    return data


def order(id, buyer, seller, state, text, escrows=None, tx=None):
    if not escrows: escrows = []
    data = {'type': 'order', 'id': id, 'buyer': buyer.encode('hex'), 'seller': seller.encode('hex'), 'escrows': escrows}
    # this is who signs
    # this is who the review is about
    # the signature
    # the signature
    if data.get('tex'):
        data['tx'] = tx.encode('hex')
    # some text
    data['text'] = text
    # some text
    data['address'] = ''
    data['state'] = state
    # new -> accepted/rejected -> payed -> sent -> received
    return data

def proto_listing(productTitle, productDescription, productPrice, productQuantity, market_id, productShippingPrice, productImageName, productImageData):
    data = {'productTitle':productTitle,
            'productDescription':productDescription,
            'productPrice':productPrice,
            'productQuantity':productQuantity,
            'market_id':market_id,
            'productShippingPrice':productShippingPrice,
            'productImageName':productImageName,
            'productImageData':productImageData}
    return data

def proto_store(key, value, originalPublisherID, age):
    data = {'type': 'store', 'key': key, 'value': value, 'originalPublisherID': originalPublisherID, 'age': age}
    return data


def negotiate_pubkey(nickname, ident_pubkey):
    data = {'type': 'negotiate_pubkey', 'nickname': nickname, 'ident_pubkey': ident_pubkey.encode("hex")}
    return data


def proto_response_pubkey(nickname, pubkey, signature):
    data = {'type': "proto_response_pubkey", 'nickname': nickname, 'pubkey': pubkey.encode("hex"),
            'signature': signature.encode("hex")}
    return data
