# Import multi-threading packages
from multiprocessing import Queue
from threading import Thread, Event

# Import time packages for waiting
import time

# Import Project packages
import front_end_manager


# Master thread for controlling all processes
class strategy_manager(Thread):

    # Initialization function
    def __init__(self, in_q):

        # Class identifier
        self.__name = 'strategy_manager'

        # Dictionary for thread statuses
        self.thread_status = {}

        # Thread pointers
        self.thread_pointers = {}

        # Thread queues
        self.thread_queues = {}

        # Class queues
        self.in_q = in_q
        self.status_q = Queue()

        # Class events
        self._stopped = Event()

        # Initializaiton of variables complete | Initialize thread instance
        print(self.__name + ' - successfully initialized.')
        super(strategy_manager, self).__init__()

    def run(self):

        # Update status for main thread
        self.thread_status[self.__name] = True
        self.status_q.put((self.__name, True))

        # Starting thread
        print(self.__name + ' - started.')

        # gui_manager thread | Initialize and start
        try:
            # Create queues for gui manager
            self.thread_queues['gui'] = {}
            self.thread_queues['gui']['to'] = Queue()
            self.thread_queues['gui']['from'] = None

            # Initialize gui manager thread instance
            self.thread_pointers['gui'] = front_end_manager.gui_manager(
                self.thread_queues['gui']['to'],
                self.status_q
            )
            self.thread_queues['gui']['from'] = self.thread_pointers['gui'].outbound_q

        except Exception as e:
            print('Initialization of GUI thread has failed!')
            print('\tException during initialization of gui_thread: ' + str(e))
            print('Exiting.')
            return
        # Start thread
        self.thread_pointers['gui'].start()

        print('All initialization procedures complete, shutting down')
        time.sleep(3)

        # Stop function calls
        self.thread_pointers['gui'].stop()
        # Wait 3 seconds for all threads to stop, then close main thread
        time.sleep(3)
        return

    def stop(self, src_name, tgt_name):

        print('Stop program called by: ' + src_name)
        self._stopped.set()
        return

    def error_exit(self):
        print('Forced exit due to error')
        self._stopped.set()
        super(strategy_manager, self).join(timeout=1)