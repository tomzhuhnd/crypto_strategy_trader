# Import generic libraries
import time

# Import multi-threading libraries
from multiprocessing import Queue
from threading import Thread, Event, Timer


class strategy_manager(Thread):

    def __init__(self, bfx_data_queue):

        # Class name
        self.__name = 'strategy'
        print(self.__name + ' thread - initializing ... ', end='')

        # Class internal variables
        self._loop_timer = 1
        self._isActive = False

        # Class internal flags
        self._stop_all = Event()

        # Class incoming data pipes
        self._bfx_data_queue = bfx_data_queue

        # Establish as new independent thread
        super(strategy_manager, self).__init__()
        print('done.')

    def run(self):

        print(self.__name + ' thread - starting.')

        while not self._stop_all.is_set():

            time.sleep(self._loop_timer)
            print(time.time())

        if self._stop_all.is_set():

            print(self.__name + ' thread - Strategy Manager shutting down, killing all strategies.')
            return

    def stop(self):

        self._stop_all.set()
