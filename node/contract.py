#!/usr/bin/env python

import json
import logging

class OBContract(object):


    def __init__(self, transport):

        self._transport = transport
        self._dht = transport.getDHT()
        self._market_id = transport.getMarketID()

        self._log = logging.getLogger('[%s] %s' % (self._market_id, self.__class__.__name__))
        self._log.info("Loading Market %s" % self._market_id)

        self.current_version = "0.1-alpha"
        self.contract_body = ""
        self.state = "seed"

    def raw_to_contract(self, raw_contract):
        self._log.info(raw_contract)
        self.contract_body = raw_contract

