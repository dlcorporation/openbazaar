import obelisk
import logging
import pybitcointools

# from twisted.internet import reactor


_log = logging.getLogger('trust')

TESTNET = False
# OBELISK_SERVER_TESTNET = "tcp://obelisk-testnet2.airbitz.co:9091"
# OBELISK_SERVER_MAINNET = "tcp://obelisk.bysh.me:9091"


# def build_output_info_list(unspent_rows):
#     unspent_infos = []
#     for row in unspent_rows:
#         assert len(row) == 4
#         outpoint = obelisk.OutPoint()
#         outpoint.hash = row[0]
#         outpoint.index = row[1]
#         value = row[3]
#         unspent_infos.append(
#             obelisk.OutputInfo(outpoint, value))
#     return unspent_infos


def burnaddr_from_guid(guid_hex):
    _log.debug("burnaddr_from_guid: %s" % guid_hex)

    if TESTNET:
        guid_hex = '6f' + guid_hex
    else:
        guid_hex = '00' + guid_hex

    _log.debug("GUID address on bitcoin net: %s" % guid_hex)

    guid = guid_hex.decode('hex')

    _log.debug("Decoded GUID address on bitcoin net")

    # perturbate GUID
    # to ensure unspendability through
    # near-collision resistance of SHA256
    # by flipping the last non-checksum bit of the address

    guid = guid[:-1] + chr(ord(guid[-1]) ^ 1)

    _log.debug("Perturbated bitcoin proof-of-burn address")

    return obelisk.bitcoin.EncodeBase58Check(guid)


def get_global(guid, callback):
    get_unspent(burnaddr_from_guid(guid), callback)


def get_unspent(addr, callback):
    _log.debug('get_unspent call')
    # def history_fetched(ec, history):
    #     _log.debug('History fetched')
    #     if ec is not None:
    #         _log.debug('Error fetching history: ', ec)
    #         return
    #     unspent_rows = [row[:4] for row in history if row[4] is None]
    #     unspent = build_output_info_list(unspent_rows)
    #     unspent = obelisk.select_outputs(unspent, 10000)

    #     if unspent is None:
    #         callback(0)
    #         return

    #     points = unspent.points

    #     if len(points) != 1:
    #         callback(0)
    #         return

    #     point = points[0]
    #     value = point.value

    #     callback(value)

    # if TESTNET:
    #     obelisk_addr = OBELISK_SERVER_TESTNET
    # else:
    #     obelisk_addr = OBELISK_SERVER_MAINNET

    # _log.debug('unspent query to obelisk server at %s' % obelisk_addr)

    # client = obelisk.ObeliskOfLightClient(obelisk_addr)

    # _log.debug('Obelisk client instantiated')

    # def get_history():
    #     _log.debug("get_history called from thread")
    #     client.fetch_history(addr, history_fetched)

    # reactor.callFromThread(get_history)

    history = pybitcointools.history(addr)
    total = 0

    for tx in history:
        total += tx['value']

    callback(total)
