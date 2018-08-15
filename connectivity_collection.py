# Import connectivity packages

# Import all api keys

# Import multi-threading packages
from multiprocessing    import Queue
from threading          import Thread


class bfx_websocket(Thread):

    # Initialize class
    def __init__(self, in_q):

        # Class identifiers
        self.__name = "bfx_ws"
        self.__type = "websocket"

        # Class queues
        self._outbound_q = Queue()
        self._inbound_q  = in_q

        # Class event flags

        # Initialization of variables complete | Initialize thread instance
        Thread.__init__(self)
        self.daemon = True

        # Print to terminal that thread has been initialized
        self._outbound_q.put((
            self.__type,
            self.__name,
            'gui',
            'gui',
            'raw_print',
            (self.__type + " : " + self.__name + " - successfully initialized.", None)
        ))
