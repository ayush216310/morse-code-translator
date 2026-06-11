import tkinter as tk

def get_choice():
    root = tk.Tk()
    root.title("Choose Convertor")
    root.geometry("450x120")

    root.eval('tk::PlaceWindow . center')
    user_choice = tk.StringVar()

    def set_choice(option):
        user_choice.set(option)
        root.destroy()

    btn1 = tk.Button(root, text="Convert Morse to String", command=lambda: set_choice("Option A"))
    btn1.pack(side=tk.LEFT, expand=True, padx=10, pady=20)

    # Option B Button
    btn2 = tk.Button(root, text="Convert String to Morse", command=lambda: set_choice("Option B"))
    btn2.pack(side=tk.RIGHT, expand=True, padx=10, pady=20)

    # Pauses the script here until the window is closed
    root.mainloop()

    return user_choice.get()

print(get_choice())