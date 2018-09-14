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

        # Channel mappings
        self._channel_ids = {}

        # Event handlers
        self._event_handlers = {
            'info': self.__handle_event_info,
            'auth': self.__handle_event_auth
        }

        # Data handlers
        self._data_handlers = {
            'account': {
                'ps': self.__handle_data_account_ps,
                'ws': self.__handle_data_account_ws,
                'hb': self.__handle_data_account_hb
            }
        }

        # Websocket specific variables
        self.ws_version = None
        self.ws_userid  = None
        self.account_balances = {'exchange': {}, 'margin': {}, 'funding': {}}
        self.account_orders = {}

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
        # self.ws.run_forever(ping_interval=60, ping_timeout=65)

        while not self._disconnected.is_set():
            print('test')
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

        # ===================================== Connection functions ===================================== #

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
        self._disconnected.set()
        self.ws.close()
        print(self.__name + ' thread - Websocket connection has been closed.')

    def _on_error(self, ws, error):
        print(error)
        # Todo: Create an actual error handlers

    def _on_message(self, ws, message):

        # print('Raw print: ' + str(message))

        # Decode incoming json message
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print(self.__name + ' thread - Exception! Bad JSON Message received! Msg: ' + str(message))
            return
        except Exception as e:
            print(message)
            print(self.__name + ' thread - Exception! Exception type: ' + str(e))
            return

        if isinstance(data, dict):                                  # Message is a dictionary | Event type

            if data['event'] in self._event_handlers:
                self._event_handlers[data['event']](data)
            else:
                print(self.__name + ' thread - Missing event handler for: "' + data['event'] + '". ', end='')
                print('Event Contents: ' + str(data))
            pass            # Todo: Pass off to event handler
        else:                                                       # Message is a list       | Data type

            channel_name = self._channel_ids[data[0]][0]

            if data[0] in self._channel_ids:
                if channel_name in self._data_handlers:
                    data_type = data[1]
                    if data[1] in self._data_handlers[channel_name]:
                        self._data_handlers[channel_name][data_type](data)
                    else:
                        print(self.__name + ' thread - Warning! Received a data message with no data type handler for "', end='')
                        print(data_type + '". Raw data: ' + str(data))
                else:
                    print(self.__name + ' thread - Warning! Received a data message with no channel handler for "', end='')
                    print(channel_name + '". Raw data: ' + str(data))

            else:
                print(self.__name + ' thread - Warning! Received an unmapped channel data message. Raw data: ' + str(data))

    # ===================================== Event handlers ===================================== #

    def __handle_event_info(self, data):

        if 'version' in data:
            self.ws_version = data['version']
        if 'platform' in data:
            if 'status' in data['platform']:
                if data['platform']['status'] == 1:
                    print(self.__name + ' thread - BFX Websocket platform is currently active!')
                    # Todo: have an actual handler for when the platform goes down
                else:
                    print(self.__name + ' thread - BFX Webscoket platform is currently offline!')
                    # Todo: have an actual handler for when the platform goes down

    def __handle_event_auth(self, data):

        if 'status' in data and data['status'] == 'OK':             # Authenticated channel subscription successful
            self._channel_ids['account'] = data['chanId']
            self._channel_ids[data['chanId']] = ('account', 0)
            print(self.__name + ' thread - Authenticated account channel created. ChanId: ' +
                  str(self._channel_ids['account']))
        else:
            print(self.__name + ' thread - BFX Websocket failed to establish authenticated channel subscription!')
            # Todo: Add handlers that will try to re-authenticate when the initial auth. fails

    # ===================================== Data handlers ===================================== #

    def __handle_data_account_ps(self, data):
        # Todo: Add handler for position snapshot
        print(self.__name + ' thread - Position Snapshot received {currently ignored}. Contents: ' + str(data))


    def __handle_data_account_ws(self, data):

        # Wallet balances snapshot
        account_balances = data[2]
        for balance in account_balances:
            if balance[0] == 'exchange':
                self.account_balances['exchange'][balance[1]] = balance[2]
            elif balance[0] == 'trading':
                self.account_balances['margin'][balance[1]] = balance[2]
            elif balance[0] == 'deposit':
                self.account_balances['funding'][balance[1]] = balance[2]
            else:
                print(self.__name + ' thread - Invalid account type received! Balance Snapshot: ' + str(balance))

    def __handle_data_account_os(self):

        # Order statuses snapshot
        print(self.__name + ' thread - Orders snapshot received! {currently ignored}')
        # TODO: Add proper order status handling

    def __handle_data_account_hb(self, data):
        # TODO: Add proper heartbeat, ping/pong handler. Need a seperate thread for message monitoring
        if False:
            print(self.__name + ' thread - Heartbeat {currently ignored}.')
