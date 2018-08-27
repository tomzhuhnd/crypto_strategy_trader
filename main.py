from multiprocessing import Queue
import time

import strategy_manager

command_queue = Queue()

strategy_manager_obj = strategy_manager.strategy_manager(command_queue)
strategy_manager_obj.start()

while not strategy_manager_obj.stopped.is_set():
    inCmd = input().lower()
    if inCmd in ('stop', 'x'):
        strategy_manager_obj.stop('main', 'strategy_manager')
        time.sleep(1)
        break
    else:
        print('Invalid command!')

    time.sleep(0.5)