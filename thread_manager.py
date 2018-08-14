# Import multi-threading packages
from multiprocessing    import Queue
from threading          import Thread, Event
from queue              import Empty

class thread_manager(Thread):

    # Initialization class
    def __init__(self, in_q):

        # Class identifiers
        self.__name = 'thread_manager'

        # Create new thread
        super(thread_manager, self).__init__()

        # Master dictionary for storing thread statuses
        self._thread_status = {}

        # Class specific queues
        self._thread_master_in_q = in_q
        self._thread_status_q = Queue()

        # Class events
        self._stopped = Event()

    def run(self):

        # Update status for main thread
        self._thread_status_q.put((self.__name, True))

