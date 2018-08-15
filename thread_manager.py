# Import multi-threading packages
from multiprocessing    import Queue
from threading          import Thread, Event


# Import Project packages

class thread_manager(Thread):

    # Initialization function
    def __init__(self, in_q):

        # Class identifiers
        self.__name = 'thread_manager'
        self.__type = 'thread_manager'

        # Master dictionary for storing thread statuses
        self._thread_status = {}

        # Master dictionary for storing thread
        self._thread_collection = {}

        # Class specific queues
        self._thread_master_in_q = in_q
        self._thread_status_q = Queue()

        # Class events
        self._stopped = Event()

        # Print to terminal that this thread is initialized
        print(self.__type + ' : ' + self.__name + ' - successfully initialized.')

        # Initialization of variables complete | Initialize thread instance
        super(thread_manager, self).__init__()

    def run(self):

        # Update status for main thread
        self._thread_status[self.__name] = True
        self._thread_status_q.put((self.__name, True))

        # Print to terminal that this thread is starting
        print(self.__type + ' : ' + self.__name + ' - started.')

        # Initialize and start gui_thread
        try:
            self._thread_collection
        except:
            print('Initialization of GUI thread has failed! Exiting...')


    def error_exit(self):
        print('Forced exit due to error')
        self._stopped.set()
        super(thread_manager, self).join(timeout=1)