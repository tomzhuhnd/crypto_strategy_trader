# Import all api keys
from api_keys import *

# Import python packages
import websocket, hmac, hashlib, json
import time, datetime

# Import multi-threading packages
from threading import Thread, Event


class bfx_websocket(Thread):

    # Initialize class
    def __init__(self, out_q):

        # Class identifiers
        self.__name = "bfx_ws"

        print(self.__name + ' thread - initializing ... ', end='')

        # Class variables
        self._print_all = True
        self.__url = 'wss://api.bitfinex.com/ws/'

        # Class queues
        self._outbound_q = out_q

        # Class event flags
        self.connected = Event()
        self.disconnected = Event()
        self.pause = Event()

        # Keys
        self.__api_pkey = bfx_api_pkey
        self.__api_skey = bfx_api_skey

        # Initialization of variables complete | Initialize thread instance
        Thread.__init__(self)
        self.daemon = True
        print('Done.')

    # Connect handler
    def connect(self):
        # Start the websocket object
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            self.__url,
            on_open=self._on_bfxAuthOpen,
            on_close=self._on_close,
            on_error=self._on_error,
            on_message=self._on_message
        )
        # Run loop
        self.ws.run_forever()

        while not self.disconnected.is_set():
            self.ws.keep_running = True
            self.ws.run_forever()

    def run(self):
        print(self.__name + ' thread - Starting.')
        self.connect()

    def stop(self):
        # Trip disconnect event
        self.disconnected.set()
        try:
            if self.ws:
                self.ws.close()
            # Give thread time to process close operation
            self.join(timeout=1)
            return True
        except:
            return False

    # ---------------------------------- Websocket specific functions ---------------------------------- #

    # Websocket Authenticated connection handler
    def _on_bfxAuthOpen(self, ws):
        print(self.__name + ' thread - establishing authenticated channel subscription ... ')

        self.connected.set()
        nonce = str(int(time.time() * 1000000))
        auth_payload = 'AUTH' + nonce
        signature = hmac.new(self.__api_skey, auth_payload.encode(), hashlib.sha384).hexdigest()
        payload = {
            'apiKey': self.__api_pkey,
            'event': 'auth',
            'authPayload': auth_payload,
            'authNonce': nonce,
            'authSig': signature
        }
        # Send request to connect with auth payload
        try:
            self.ws.send(json.dumps(payload))
        except websocket.WebSocketConnectionClosedException:
            print(self.__name + ' thread - Exception! Payload not sent due to connection not being open!')
        except Exception as e:
            print(self.__name + ' thread - Exception! Code: ' + str(e))

    # Websocket close handler
    def _on_close(self, ws):
        self.connected.clear()
        print(self.__name + ' thread - Websocket service has been disconnected.')

    # Websocket error handler
    def _on_error(self, ws, error):
        print(error)
        # Todo: create error handler for re-connect

    # Websocket message handler
    def _on_message(self, ws, message):
        # Parse JSON object
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print(self.__name + ' thread - Bad json object from websocket: ' + str(message))
            return
        print(data)

    # -------------------------------------------------------------------------------------------------- #
















