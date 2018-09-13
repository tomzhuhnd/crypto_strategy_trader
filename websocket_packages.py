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
        self._isActive = False

        # Internal class events
        self._connected = Event()
        self._disconnected = Event()
        self._pause = Event()

        # Establish as new independent thread
        Thread.__init__(self)
        self.daemon = True
        print('done.')

    def run(self):
        print(self.__name + ' thread - starting.')
        self._connect()

    def _connect(self):
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

        while not self._disconnected.is_set():
            self.ws.keep_running = True
            self.ws.run_forever()

    def stop(self):

        # Disconnect event
        self._disconnected.set()
        try:
            # Check ws connection, close if its open
            if self.ws:
                self.ws.close()
            self._isActive = False
            # Give thread a second to process close operation
            self.join(timeout=1)
            return True
        except Exception as e:
            print(self.__name + ' thread - Error on stop! Error code: ' + str(e))
            return False


    def _bfx_auth_open(self, ws):

        nonce = str(int(time.time() * 1000000))
        auth_payload = 'AUTH' + nonce
        signature = hmac.new(self.__skey, auth_payload.encode(), hashlib.sha384).hexdigest()
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
            self._connected.set()
        except websocket.WebSocketConnectionClosedException:
            print(self.__name + ' thread - Exception! Payload failed to send, websocket connection is closed!')
        except Exception as e:
            print(self.__name + ' thread - Exception! Exception type: ' + str(e))

    def _on_close(self, ws):
        self._connected.clear()
        self._disconnected.clear()
        print(self.__name + ' thread - Websocket connection has been closed.')

    def _on_error(self, ws, error):
        print(error)
        # Todo: Create an actual error handlers

    def _on_message(self, ws, message):

        # Decode incoming json message
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print(self.__name + ' thread - Bad JSON Message received! Msg: ' + str(message))
            return
        except Exception as e:
            print(message)
            print(self.__name + ' thread - Exception! Exception type: ' + str(e))
            return

        # Handle the data based on data type
        print(data)