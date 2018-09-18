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
        self._loop_timer = 0.5
        self._isActive = False

        # Class internal flags
        self._stop_all = Event()

        # Class incoming data pipes
        self._bfx_data_queue = bfx_data_queue

        # Queue command handlers
        self.queue_command_handlers = {
            'account': {
                'wallet': self.__update_account_wallet
            },
            'funding': {
                'position': self.__update_funding_position
            }
        }

        # Data grids
        self.account_balances = {'exchange': {}, 'margin': {}, 'funding': {}}
        self.funding_positions = {'lend': {}, 'loan': {}}

        # Establish as new independent thread
        super(strategy_manager, self).__init__()
        print('done.')

    def run(self):

        print(self.__name + ' thread - starting.')

        while not self._stop_all.is_set():

            # time.sleep(self._loop_timer)

            if not self._bfx_data_queue.empty():
                # Unload data from the queue
                data = self._bfx_data_queue.get()
                try:
                    self.queue_command_handlers[data[0][0]][data[0][1]](data[1])
                except Exception as e:
                    print(self.__name + ' thread - Warning [Exception - ' + str(e) + ']')

        if self._stop_all.is_set():

            print(self.__name + ' thread - Strategy Manager shutting down, killing all strategies.')
            return

    def stop(self):

        self._stop_all.set()

    # Internal Functions

    def __update_account_wallet(self, data):
        # No need to check if the incoming data is the correct type of account balance, already handled on websocket
        self.account_balances[data[0]][data[1]] = data[2]

    def __update_funding_position(self, update):
        new_update = update
        if new_update['side'] == 1:             # Offer type is a Lend
            self.funding_positions['lend'][new_update.pop('offerId', None)] = new_update
        else:                               # Offer type is a Loan
            pass

        # TODO: Add MySQL integration to handle storage of these updates