# Import connectivity packages
import websocket

# Import all api keys
from api_keys import *

# Import multi-threading packages
from multiprocessing    import Queue
from threading          import Thread, Event
from queue              import Empty

class bfx_websocket(Thread):

    # Initialize class
    def __init__(self, out_q, in_q):

        # Class identifiers
        self.__name = "bfx_ws"
        self.__type = "websocket"

        # Create new thread
        Thread.__init__(self)
        self.daemon = True