# Import generic packages
import time

# Import multi-threading capacity
from multiprocessing import Queue
from threading import Thread, Event

# Import GUI packages
import tkinter      as tk
import tkinter.font as tkfont
import tkinter.ttk  as ttk


class gui_manager(Thread):

    def __init__(self, outbound_queue, inbound_queue):

        # Class name
        self.__name = 'gui'
        print(self.__name + ' thread - initializing ... ', end='')

        # Class variables

        # Class queues
        self.inbound_q  = inbound_queue
        self.outbound_q = outbound_queue

        # Class events
        self._stopped = Event()

        # Class command handlers
        self.command_handlers = {

        }

        print('done.')
        super(gui_manager, self).__init__()

    def run(self):

        print(self.__name + ' thread - starting.')

        # Generate tkinter master window
        self.gui_root = tk.Tk()

        # Instantiate window classes
        self.main_window = main_window(self.gui_root, self.inbound_q, self.outbound_q)

        self.gui_root.after(0, self.run_gui)

    def run_gui(self):

        # Gui main loop
        if not self._stopped.is_set():
            if not self.inbound_q.empty():
                src_name, tgt_name, cmd_name, payload = self.inbound_q.get()
                if cmd_name not in self.command_handlers:
                    print(self.__name + ' thread - No handler for ' + cmd_name)
                else:
                    self.command_handlers[cmd_name](src_name, tgt_name, cmd_name, payload)
                self.gui_root.update()
                self.gui_root.after(0, self.run_gui)
        else:
            # Todo: set all tkinter varaibles to None on exit
            self.gui_root.destroy()
            self.gui_root.quit()

    def stop(self):
        # Set Stop event
        print(self.__name + ' thread - Shutting down.')
        self._stopped.set()
        time.sleep(1)
        super(gui_manager, self).join(timeout=1)
        return True

class main_window:

    def __init__(self, gui_root, inbound_q, outbound_q):

        # Class internal variables
        self.__name = 'gui'
        self.gui_root = gui_root
        self.gui_root.title('Program')
        self.frame = tk.Frame(self.gui_root)



