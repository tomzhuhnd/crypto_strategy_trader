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
url_bfx = 'wss://api.bitfinex.com/ws/'

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
        self.connected = Event()
        self.disconnected = Event()
        self._pause = Event()

        # Establish as new independent thread
        Thread.__init__(self)
        self.daemon = True
        print('done.')

    def connect(self):
        # Start the websocket object
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            url_bfx,
            on_open=self._bfx_auth_open,
            on_close=self._on_close,
            on_error=self._on_error,
            on_message=self._on_message
        )
        # Run loop
        self.ws.run_forever()

        while not self.disconnected.is_set():
            self.ws.keep_running = True
            self.ws.run_forever()

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

        # Send payload to establish authenticated connection to account
        print(self.__name + ' thread - Establishing authenticated connection to account.')
        try:
            self.ws.send(json.dumps(payload))
        except websocket.WebSocketConnectionClosedException:
            print(self.__name + ' thread - Exception! Payload failed to send, websocket connection is closed!')
        except Exception as e:
            print(self.__name + ' thread - Exception! Exception type: ' + str(e))

    def _on_close(self, ws):
        self.connected.clear()
        self.disconnected.clear()
        print(self.__name + ' thread - Websocket connection has been closed.')

    def _on_error(self, ws, error):
        print(error)
        # Todo: Create an actual error handlers

    def _on_message(self, ws, message):
        pass