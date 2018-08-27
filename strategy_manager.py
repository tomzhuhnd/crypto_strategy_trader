# Import multi-threading packages
from multiprocessing import Queue
from threading import Thread, Event

# Import time packages for waiting
import time

# Import Project packages
import front_end_manager
import connection_manager


# Master thread for controlling all processes
class strategy_manager(Thread):

    # Initialization function
    def __init__(self, in_q):

        # Class identifier
        self.__name = 'strategy_manager'

        print(self.__name + ' thread - initializing ... ', end='')

        # Dictionary for thread statuses
        self.thread_status = {}

        # Thread pointers
        self.thread_gui_pointer = None
        self.thread_bfx_ws_pointer = None

        # Thread to queues
        self.to_gui_queue = Queue()

        # Thread from queues
        self.from_gui_queue = Queue()
        self.from_bfx_ws_queue = Queue()

        # Thread events
        self.gui_command_flag = Event()

        # Class queues
        self.in_q = in_q
        self.status_q = Queue()

        # Class events
        self.stopped = Event()

        # Initializaiton of variables complete | Initialize thread instance
        print('Done.')
        super(strategy_manager, self).__init__()

    def run(self):

        # Update status for main thread
        self.thread_status[self.__name] = True
        self.status_q.put((self.__name, True))

        # Starting thread
        print(self.__name + ' thread - started.')

        # gui_manager thread | Initialize and start
        try:
            # Initialize gui manager thread instance
            self.thread_gui_pointer = front_end_manager.gui_manager(
                self.to_gui_queue,
                self.from_gui_queue,
                self.status_q,
                self.gui_command_flag
            )
        except Exception as e:
            print('Initialization of GUI thread has failed!')
            print('\tException message: ' + str(e))
            print('Exiting.')
            return
        # Start thread
        self.thread_gui_pointer.start()

        # bfx_ws thread | Initialize and start
        try:
            # Initialize BFX_WS manager thread instance
            self.thread_bfx_ws_pointer = connection_manager.bfx_websocket(
                self.from_bfx_ws_queue
            )
        except Exception as e:
            print('Initialization of bfx_ws has failed!')
            print('\tException message: ' +str(e))
            print('Exiting.')
            return
        # Start thread
        self.thread_bfx_ws_pointer.start()

        # All threads are started | Start the main loop
        print(self.__name + ' thread - All initialization procedures complete. Starting main loop.')

        # Main loop
        while not self.stopped.is_set():

            # Handle GUI commands as they come in
            if self.gui_command_flag.is_set():
                if not self.from_gui_queue.empty():
                    src_name, tgt_name, tgt_command, tgt_payload = self.from_gui_queue.get(timeout=0.1)
                    print(src_name, tgt_name, tgt_command, tgt_payload)
                    # Reset flag
                    self.gui_command_flag.clear()
                    # TODO: Add proper command handler for incoming gui queue

        # Stopped function was called, close all threads and exit
        print(self.__name + ' thread - Stopping program. Shutting down sub-thread processes.')
        self.thread_gui_pointer.stop()
        # Wait 1 second for all threads to stop, then close main thread
        time.sleep(1)
        return

    def stop(self, src_name, tgt_name):

        print('Stop program called by: ' + src_name)
        self.stopped.set()
        return

    def error_exit(self):
        print('Forced exit due to error')
        self.stopped.set()
        super(strategy_manager, self).join(timeout=1)