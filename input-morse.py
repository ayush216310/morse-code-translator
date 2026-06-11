import tkinter as tk
import time

# --- Configuration ---
LONG_PRESS_THRESHOLD = 0.3
ENTER_EXIT_THRESHOLD = 1.0

# --- Variables ---
space_press_time = 0.0
space_is_pressed = False
space_timer = None

enter_press_time = 0.0
enter_is_pressed = False
enter_timer = None

# NEW: The variable that will hold our entire message
final_morse_string = ""


# --- Spacebar Logic (Dots and Dashes) ---
def on_space_press(event):
    global space_press_time, space_is_pressed, space_timer

    if space_timer is not None:
        root.after_cancel(space_timer)
        space_timer = None

    if not space_is_pressed:
        space_press_time = time.time()
        space_is_pressed = True
        status_label.config(bg="lightgray", text="HOLDING...")


def on_space_release(event):
    global space_timer
    space_timer = root.after(50, execute_space_release)


def execute_space_release():
    global space_is_pressed, space_timer, final_morse_string
    space_is_pressed = False
    space_timer = None

    duration = time.time() - space_press_time

    if duration >= LONG_PRESS_THRESHOLD:
        symbol = "-"
    else:
        symbol = "."

    print(symbol + " ", end="", flush=True)

    # NEW: Add the symbol to our master string
    final_morse_string += symbol + " "

    status_label.config(bg="SystemButtonFace", text="PRESS SPACEBAR")


# --- Keyboard Logic (Words and Lines) ---
def on_shift_press(event):
    global final_morse_string
    print(" / ", end="", flush=True)

    # NEW: Add the space to our master string
    final_morse_string += " / "


def on_enter_press(event):
    global enter_press_time, enter_is_pressed, enter_timer

    if enter_timer is not None:
        root.after_cancel(enter_timer)
        enter_timer = None

    if not enter_is_pressed:
        enter_press_time = time.time()
        enter_is_pressed = True


def on_enter_release(event):
    global enter_timer
    enter_timer = root.after(50, execute_enter_release)


def execute_enter_release():
    global enter_is_pressed, enter_timer, final_morse_string
    enter_is_pressed = False
    enter_timer = None

    duration = time.time() - enter_press_time

    if duration >= ENTER_EXIT_THRESHOLD:
        print("\n\n[Done entering Morse code. Closing program...]")
        root.destroy()
    else:
        print("\n", end="", flush=True)
        # NEW: Add the new line to our master string
        final_morse_string += "\n"


# --- Main Wrapper Function ---
def start_telegraph():
    global root, status_label, final_morse_string

    # Clear the string in case we run the function multiple times
    final_morse_string = ""

    root = tk.Tk()
    root.title("Telegraph Key")
    root.geometry("250x100")
    root.eval('tk::PlaceWindow . center')

    status_label = tk.Label(root, text="PRESS SPACEBAR", font=("Arial", 14), height=3, width=20, relief=tk.RIDGE)
    status_label.pack(pady=10)

    root.bind("<KeyPress-space>", on_space_press)
    root.bind("<KeyRelease-space>", on_space_release)
    root.bind("<Shift_L>", on_shift_press)
    root.bind("<Shift_R>", on_shift_press)
    root.bind("<KeyPress-Return>", on_enter_press)
    root.bind("<KeyRelease-Return>", on_enter_release)

    print("--- MORSE CODE TERMINAL ---")
    print("Spacebar   : '.' (Tap) or '-' (Hold)")
    print("Shift Key  : New Word (' / ')")
    print("Enter Key  : New Line")
    print("Hold Enter : Finish and Exit")
    print("---------------------------\n")

    # This pauses the script until the user holds Enter and root.destroy() runs
    root.mainloop()

    # NEW: Once the window closes, return the collected string!
    return final_morse_string.strip()


# --- How to test it ---
if __name__ == "__main__":
    my_captured_morse = start_telegraph()

    print("\n--- RESULTS ---")
    print("The final string saved in your Python code is:")
    print(repr(my_captured_morse))  # Using repr() so you can clearly see the spaces and \n