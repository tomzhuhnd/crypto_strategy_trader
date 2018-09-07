# Import generic packages
import time

# Import multi-threading libraries
from multiprocessing    import Queue
from threading          import Thread, Event

import front_end_manager

class program_master(Thread):

    def __init__(self):

        # Class name
        self.__name = 'manager'
        print(self.__name + ' thread - initializing ... ', end='')

        # Class internal variables
        self.__sleep_timer = 1

        # Class internal events
        self.stopped = Event()

        # Thread pointers
        self._gui_thread = None

        # Thread statuses
        self.thread_status = {}

        # Incoming Queues
        self._inbound_gui_q = Queue()

        # Outgoing Queues
        self._outbound_gui_q = Queue()

        # Data grid variables


        # Class command handlers
        self.command_handlers = {

        }

        # Initialization complete. Instantiate thread
        super(program_master, self).__init__()
        print('done.')

    def run(self):

        # Update status in thread status
        self.thread_status['master'] = True         # Todo: add handler to push status to gui
        print(self.__name + ' thread - started! Initializing child threads ... ')

        self._gui_thread = front_end_manager.gui_manager(
            self._inbound_gui_q,
            self._outbound_gui_q
        )
        self._gui_thread.start()
        self.thread_status['gui'] = True

        # Main Loop
        while not self.stopped.is_set():

            time.sleep(self.__sleep_timer)

        if self.stopped.is_set():

            self._gui_thread.stop()
