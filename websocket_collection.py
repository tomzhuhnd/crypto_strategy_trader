import time

# Import libraries for web response handling
import hmac, hashlib, time, json

# Websocket External library
import websocket

# Import Multi-threading modules
from multiprocessing import Queue
from threading import Thread, Event, Timer
from collections import OrderedDict

class openBFXWebSocket(Thread):

    def __init__(self, socket_name):

        # Global Variables
        self.__API_Key  = API_Key
        self.__API_SKEY = API_SKey

        self.__isActive = True
        self.__url = 'wss://api.bitfinex.com/ws/'
        self.__reconnectTimer = 5
        self.__socketName = socket_name
        self.__terminal_print = True

        # Info Msgs from BFX
        self.info_message = {
            20051: 'Reconnect request',
            20060: 'Pause request',
            20061: 'Re-subscribe request'
        }
        # Error Msgs from BFX
        self.errors = {
            10000 : 'Unknown event',
            10001 : 'Generic error',
            10008 : 'Concurrency error',
            10020 : 'Request parameters error',
            10050 : 'Configuration setup failed',
            10100 : 'Failed authentication',
            10111 : 'Error in authentication request payload',
            10112 : 'Error in authentication request signature',
            10113 : 'Error in authentication request encryption',
            10114 : 'Error in authentication request nonce',
            10200 : 'Error in un-authentication request',
            10300 : 'Subscription failed (generic)',
            10301 : 'Already subscribed',
            10302 : 'Unknown channel',
            10400 : 'Subscription failed (generic)',
            10401 : 'Not subscribed',
            11000 : 'Not ready, try again later',
            20000 : 'User is invalid!',
            20051 : 'Websocket server stopping',
            20060 : 'Websocket server re-syncing',
            20061 : 'Websocket server re-sync complete'

        }

        # Initialize Control Variables
        self.q = Queue()
        self.chl_subs = OrderedDict()
        self.connected = Event()
        self.disconnect_call = Event()
        self.pause = Event()

        # Establish self as a new thread
        Thread.__init__(self)
        self.daemon = True

        print(socket_name + ' - websocket successfully initialized !')

    def _connect(self):
        # Start websocket objet
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.__url,
                                         on_message=self._onMessage,
                                         on_error=self._onError,
                                         on_close=self._onClose,
                                         on_open=self._bfxAuthenticatedOpen)
        self.ws.run_forever()

        while not self.disconnect_call.is_set():
            print(self.__socketName + ' Webocket has disconnected! Attempting to reconnect again in %s seconds.' %
                  self.__reconnectTimer)
            self.state = 'unavailable'
            time.sleep(self.__reconnectTimer)

            self.ws.keep_running = True
            self.ws.run_forever()
            # self._reconnect_channels

    def run(self):
        self._connect()

    def stop(self):
        # Disconnect Call Event Set
        self.disconnect_call.set()
        self.unauthenticate()


    def _bfxAuthenticatedOpen(self, ws):
        print('\tWS -> ' + self.__socketName + ' WS establishing authenticated channel subscription ... ', end = '')
        self.connected.set()
        nonce = str(int(time.time() * 1000000))
        auth_payload = 'AUTH' + nonce

        signature = hmac.new(
            self.__API_SKEY,
            auth_payload.encode(),
            hashlib.sha384
        ).hexdigest()

        payload = {
            'apiKey': self.__API_Key,
            'event': 'auth',
            'authPayload': auth_payload,
            'authNonce': nonce,
            'authSig': signature
        }
        try:
            self.ws.send(json.dumps(payload))
        except websocket.WebSocketConnectionClosedException:
            print('ERROR - Payload not sent due to connection not open')


    def _onMessage(self, ws, message):
        # Try to parse the incoming json object
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print('\t Bad JSON Message')
            return

        # On successful json parse, determine if its a system message or system data
        if isinstance(data, dict):
            if self.__terminal_print: print('\tWS -> Raw Message: ' + message)
            res = self._msg_handler(data)
        else:
            # Handle hearbeat
            if data[1] == 'hb':
                print('HEARTBEAT - TODO')
            # Data from server
            else:
                if self.__terminal_print: print('\tWS -> Raw Data: ' + message)
                self.q.put((data[0], data[1:]))


    def _msg_handler(self, jsonDt):
        print('TODO')


    def _onError(self, ws, error):
        print(error)
        # Todo: Set up reconnect and error handling here

    def _onClose(self, ws):
        if self.__terminal_print: print(self.__socketName + ' websocket closing ')
        self.connected.clear()

    def unauthenticate(self):
        payload = {
            'event': 'unauth'
        }
        try:
            self.ws.send(json.dumps(payload))
        except websocket.WebSocketConnectionClosedException:
            print('ERROR - Payload not sent due to connection not open')
