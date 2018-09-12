# Import default libraries
import time
import json, requests
import hmac, hashlib

# Import connectivity libraries
import websocket

# Import multi-threading libraries
from multiprocessing import Queue
from threading import Thread, Event, Timer

from api_keys import *


# URLs
bfx_url = 'wss://api.bitfinex.com/ws/'

# BFX Websocket class
class bfx_websocket(Thread):

    def __init__(self):

        # Class name
        self.__name = 'bfx_ws'
        print(self.__name + ' thread - initializing ... ', end='')

        # Internal class variables
        self.__key = bfx_api_pkey
        self.__skey = bfx_api_skey

        # Internal status variables
        self.isActive = False

        # Internal class events
        self._connected = Event()
        self._disconnect_call = Event()
        self._pause = Event()

        # Establish as new independent thread
        Thread.__init__(self)
        self.daemon = True
        print('done.')

    def _bfx_auth_open(self, ws):

        nonce = str(int(time.time() * 1000000))
        auth_payload = 'AUTH' + nonce
        signature = hmac.new(self.__skey, auth_payload.encode(), hashlib.sha384).hexdigest
        payload = {
            'apiKey': self.__key,
            'event': 'auth',
            'authPayload': auth_payload,
            'authNonce': nonce,
            'authSig': signature
        }