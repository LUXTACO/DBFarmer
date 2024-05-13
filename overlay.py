import sys
import time
import logging
import tkinter as tk
from typing import Callable, Any

logger = logging.getLogger(__name__)

def report_callback_exception(exc_type, val, tb):
    if issubclass(exc_type, GracefulExit):
        sys.exit(0)

    logger.error('Exception occured, exiting:', exc_info=(exc_type, val, tb))
    sys.exit(1)
    
class GracefulExit(Exception):
    "Allows callbacks to gracefully exit without logging error"

OVERLAY_FONT = ('Verdana', '12')

class Overlay:
    
    """
    * Overlay Class
        DESCRIPTION: This class is used to create a tkinter window that will overlay the game window.
        
        Methods:
        > __init__: Initializes the overlay window.
            >> input >> close_callback: Callable[[Any], None], initial_data: dict, initial_delay: int, get_new_data_callback: Callable[[], tuple[int, str]]
            >> output >> None: Returns None cuz its a init func.
            
        Syntax:
        % initial_data & callback_data %: Dict[str]
            % example % -> {"loop": content, "stuck": content}
    """
    
    def __init__(self, initial_data: dict, initial_delay: int, get_new_data_callback: Callable[[], tuple[int, str]]):
        
        self.initial_data = initial_data
        self.log_file = initial_data["log_file"]
        self.initial_delay = initial_delay
        self.last_line = None
        self.get_new_data_callback = get_new_data_callback
        
        self.root = tk.Tk()
        self.root.report_callback_exception = report_callback_exception
        
        # Setup Close and Hide Label
        self.close_label = tk.Label(self.root, text=" X |", font=OVERLAY_FONT
                                    , fg="#cb36b7", bg="#121212")
        
        self.close_label.bind("<Button-1>", lambda x: self.close_window())
        self.close_label.grid(row=0, column=0)
        
        self.hide_label = tk.Label(self.root, text="— |", font=OVERLAY_FONT
                                   , fg="#cb36b7", bg="#121212")
        
        self.hide_label.bind("<Button-1>", lambda x: self.hide_window())
        self.hide_label.grid(row=0, column=1)
        
        self.title_label = tk.Label(self.root, text="DBFarmer Overlay | By: Takkeshi | https://github.com/LUXTACO", font=OVERLAY_FONT
                                    , fg="#cb36b7", bg="#121212", width=58)
        self.title_label.grid(row=0, column=2)
        
        # Setup data stuff
        self.loop_text = tk.StringVar()
        self.loop_label = tk.Label(
            self.root,
            textvariable=self.loop_text,
            font=OVERLAY_FONT,
            fg="#cb36b7",
            bg="#1a1a1a"
        )
        self.loop_label.grid(row=1, column=0, columnspan=3, sticky='w')
        
        self.stuck_text = tk.StringVar()
        self.stuck_label = tk.Label(
            self.root,
            textvariable=self.stuck_text,
            font=OVERLAY_FONT,
            fg="#cb36b7",
            bg="#1a1a1a"
        )
        self.stuck_label.grid(row=2, column=0, columnspan=3, sticky='w')
        
        self.console_textbox = tk.Text(
            self.root, 
            font=OVERLAY_FONT, 
            fg="#cb36b7", 
            bg="#1a1a1a", 
            borderwidth=2,
            height=12, 
            width=65
        )
        self.console_textbox.grid(row=3, column=0, columnspan=500, sticky='w')
        
        
        # Define Window Geometry
        self.root.overrideredirect(True)
        self.root.geometry("+5+5")
        self.root.lift()
        self.root.wm_attributes("-topmost", True)
        self.root.configure(bg="#1a1a1a")
        
    def update_data(self) -> None:
        
        wait_time, update_dict = self.get_new_data_callback()
        
        if update_dict["loop"] != None:
            self.loop_text.set(update_dict["loop"])
        if update_dict["stuck"] != None:
            self.stuck_text.set(update_dict["stuck"])
            
        with open(self.log_file, "r") as file:
            self.console_textbox.delete("1.0", tk.END)
            self.console_textbox.insert(tk.END, file.read())
            self.console_textbox.see(tk.END)
        
        self.root.after(wait_time, self.update_data)
    
    def run(self) -> None:
        
        self.loop_text.set(self.initial_data["loop"])
        self.stuck_text.set(self.initial_data["stuck"])
        
        with open(self.log_file, "r") as file:
            self.console_textbox.delete("1.0", tk.END)
            self.console_textbox.insert(tk.END, file.read())
            self.console_textbox.see(tk.END)
        
        self.root.after(self.initial_delay, self.update_data)
        self.root.mainloop()

    def hide_window(self) -> None:
        self.root.withdraw()
        time.sleep(10)
        self.root.deiconify()
        
    def close_window(self) -> None:
        self.root.destroy()

if __name__ == "__main__": #? Testing the Overlay Class [passed]
    
    import random
    
    def update():
        return 500, {"loop": f"Loops {random.randint(1, 100)}", "crono": f"Current cronos {random.randint(1, 100)}", "stuck": f"Stuck: {random.randint(1, 100)}"}
    
    def close(ignore):
        exit()
    
    def minimize(ignore):
        print("Mini")
    
    Overlay(close, {"loop": "Getting lmao", "crono": "meta a nigger", "stuck": "Stuck: 2"}, 500, lambda: update()).run()