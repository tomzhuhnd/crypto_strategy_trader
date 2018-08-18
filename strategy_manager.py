# Import multi-threading packages
# Import time packages for waiting
import time
from multiprocessing import Queue
from threading import Thread, Event

# Import Project packages
import front_end_manager


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

        # Master dictionary for storing thread queues
        self._thread_queues = {}

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
            # Create queues
            self._thread_queues['gui'] = {}
            self._thread_queues['gui']['gui'] = {}
            self._thread_queues['gui']['gui']['from'] = None
            self._thread_queues['gui']['gui']['to']   = Queue()

            self._thread_collection['gui'] = {}
            self._thread_collection['gui']['gui'] = front_end_manager.gui_manager(
                self._thread_queues['gui']['gui']['to'],
                self._thread_status_q
            )
            self._thread_queues['gui']['gui']['from'] = self._thread_collection['gui']['gui']._outbound_q
        except Exception as e:
            print('Exception with initialization: ' + str(e))
            print('Initialization of GUI thread has failed! Exiting...')
            return
        self._thread_collection['gui']['gui'].start()

        # Testing the raw_print function
        self._thread_queues['gui']['gui']['to'].put((
            self.__type, self.__name, 'gui', 'gui', 'raw_print', ('Raw Print Testing', None)
        ))

        # Test Function
        print('All initialization procedures complete, shutting down')

        time.sleep(3)

        # Stop function calls
        self._thread_collection['gui']['gui'].stop()
        # Wait 3 seconds for all threads to stop, then close main thread
        time.sleep(3)
        return


    def stop(self, src_type, src_name, tgt_type, tgt_name):

        print('Stop program called by: ' + src_type + ' - ' + src_name)
        self._stopped.set()
        return


    def error_exit(self):
        print('Forced exit due to error')
        self._stopped.set()
        super(thread_manager, self).join(timeout=1)