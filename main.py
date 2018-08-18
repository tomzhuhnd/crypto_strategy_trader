from multiprocessing import Queue

import thread_manager

command_queue = Queue()

thread_manager_obj = thread_manager.thread_manager(command_queue)
thread_manager_obj.run()

