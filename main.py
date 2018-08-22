from multiprocessing import Queue

import strategy_manager

command_queue = Queue()

thread_manager_obj = strategy_manager.strategy_manager(command_queue)
thread_manager_obj.run()

