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
        self.isActive = True

        # Internal class events
        self._connected = Event()
        self._disconnect_call = Event()
        self._pause = Event()

        # Establish as new independent thread
        Thread.__init__(self)
        self.daemon = True
        print('done.')

