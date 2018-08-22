# Import GUI related packages
import tkinter  as tk

# Import multi-threading packages
from multiprocessing import Queue
from threading import Thread, Event


class gui_manager(Thread):

    # Initialization function
    def __init__(self, in_q, status_q):

        # Class identifiers
        self.__name = 'gui'

        # Print to terminal for initialization alert
        print(self.__name + ' thread - Initializing ... ', end='')

        # Class queues
        self.inbound_q = in_q
        self.outbound_q = Queue()
        self.status_q = status_q

        # Class event flags
        self._stopped = Event()

        # Class command handlers
        self._command_handlers = {

        }

        # Successful initialization, print to terminal
        print('Done.')

        # Initialization of variables complete | Initialize thread instance
        super(gui_manager, self).__init__()

    # Startup of thread mainloop
    def run(self):

        print(self.__name + ' thread - Starting.')

        # Generate tkinter master window
        self.gui_root = tk.Tk()

        # Call recursive run_function to constantly update tkinter gui
        self.gui_root.after(1, self.run_gui)
        self.gui_root.mainloop()

    # Main run loop for tkinter gui
    def run_gui(self):

        # Check if stopped has been set
        if not self._stopped.is_set():
            # Check if anything is in the queue
            if not self.inbound_q.empty():
                # Error handler wrapper just in case
                try:
                    src_name, tgt_name, tgt_command, tgt_payload = self.inbound_q.get(timeout=0.1)
                    if tgt_command in self._command_handlers:
                        # Call appropriate command handler
                        self._command_handlers[tgt_command](
                            src_name, tgt_name, tgt_payload
                        )
                    else:
                        print(self.__name + ' - No event handler for ' + tgt_command + '!')
                except Exception as e:
                    print(self.__name + ' exception error! Exception: ' + str(e))
            # Run tkinter gui update commands

            # Recall main run loop
            self.gui_root.after(1, self.run_gui)

        # Stopped flag on | Turn off gui front end
        else:
            # Exit out of tkinter GUI interface, close out all variables to none, join thread
            self.gui_root.destroy()
            self.gui_root.quit()
            return

    # Function to set the stopped event flag
    def stop(self):
        # Set stop event
        self._stopped.set()
        return
