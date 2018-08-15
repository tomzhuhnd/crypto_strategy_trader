# Import multi-threading packages
# Import GUI related packages
import tkinter  as tk
from multiprocessing import Queue
from threading import Thread, Event


class gui_manager(Thread):

    # Initialization function
    def __init__(self, in_q, status_q):

        # Print to terminal for initialization alert
        print(self.__type + ' : ' + self.__name + ' - initializing ... ', end='')

        # Class identifiers
        self.__name = 'gui'
        self.__type = 'gui'

        # Class queues
        self._inbound_q  = in_q
        self._outbound_q = Queue()
        self._status_q   = status_q

        # Class event flags
        self._stopped = Event()

        # Class command handlers
        self._command_handlers = {
            'raw_print' : self.raw_print
        }

        # Successful initialization, print to terminal
        print('Done.')

        # Initialization of variables complete | Initialize thread instance
        super(gui_manager, self).__init__()

    # Startup of thread mainloop
    def run(self):

        # Generate tkinter master window
        self.gui_root = tk.Tk()

        # Call recursive run_function to constantly update tkinter gui
        self.gui_root.after(1, self.run_gui)
        self.gui_root.mainloop()

    # Main run loop for tkinter gui
    def run_gui(self):

        # Check if stopped has been set
        if not self._stopped.is_set():
            # Check for queued commands
            try:
                src_type, src_name, tgt_type, tgt_name, tgt_command, tgt_payload = self._inbound_q.get(timeout=0.1)
                # Call appropriate command handler
                self._command_handlers[tgt_command](
                    src_type, src_name, tgt_type, tgt_name, tgt_payload
                )
            except:
                print(self.__type + " : " + self.name + " - No event handler!")
            # Run tkinter gui update commands

            # Recall main run loop
            self.gui_root.after(1, self.run_gui)

        # Stopped flag on | Turn off gui front end
        else:
            try:
                # Exit out of tkinter GUI interface, close out all variables to none, join thread
                self.gui_root.destory()
                super(gui_manager, self).join(timeout=1)
                return True
            except:
                return False

    # Function to stop the gui
    def stop(self):
        # Set stop event
        self._stopped.set()

    # Function to print directly to terminal
    def raw_print(self, source_type, source_name, target_type, target_name, target_payload):

        # Check to see if there is a string that needs to be added to end of terminal print
        if target_payload[1] is None:
            print(target_payload[0])
        else:
            print(target_payload[0], end=target_payload[1])