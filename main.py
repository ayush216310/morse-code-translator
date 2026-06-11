import tkinter as tk
from tkinter import font as tkfont
import time

# ─── Morse Code Tables ────────────────────────────────────────────────────────

CHAR_TO_MORSE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.',  '(': '-.--.',  ')': '-.--.-',
    '&': '.-...',  ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.',  '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-','@': '.--.-.', ' ': '/',
}

MORSE_TO_CHAR = {v: k for k, v in CHAR_TO_MORSE.items() if k != ' '}

def string_to_morse(text):
    """Convert plain text to morse code.
    Letters separated by spaces, words by ' / ', newlines preserved as newlines.
    """
    result_lines = []
    for line in text.split(chr(10)):
        morse_words = []
        for word in line.split(" "):
            if word == "":
                morse_words.append("")
                continue
            symbols = [CHAR_TO_MORSE[c] for c in word.upper() if c in CHAR_TO_MORSE]
            if symbols:
                morse_words.append(" ".join(symbols))
        result_lines.append(" / ".join(morse_words))
    return chr(10).join(result_lines)

def morse_to_string(morse):
    """Convert morse code to plain text.
    Letters separated by spaces, words by '/ ', newlines preserved.
    """
    decoded_lines = []
    for line in morse.split(chr(10)):
        decoded_words = []
        # Split on '/ ' (word separator written by morse input mode)
        # Also handle ' / ' for string_to_morse generated text
        normalised = line.replace(' / ', '/ ')
        for word in normalised.split('/ '):
            word = word.strip()
            if not word:
                continue
            chars = [MORSE_TO_CHAR.get(sym, '?') for sym in word.split() if sym]
            if chars:
                decoded_words.append(''.join(chars))
        decoded_lines.append(' '.join(decoded_words))
    return chr(10).join(decoded_lines)


# ─── Option Selector Window ───────────────────────────────────────────────────

def show_option_selector():
    """Show a modal option window. Returns 'morse_to_string' or 'string_to_morse'."""
    root = tk.Tk()
    choice = tk.StringVar(value="")
    root.title("Morse Translator")
    root.geometry("480x200")
    root.resizable(False, False)
    root.configure(bg="#1a1a2e")
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    w, h = 480, 200
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    title_font = tkfont.Font(family="Courier", size=13, weight="bold")
    btn_font   = tkfont.Font(family="Courier", size=11)

    tk.Label(
        root, text="— MORSE CODE TRANSLATOR —",
        font=title_font, bg="#1a1a2e", fg="#e0e0e0", pady=22
    ).pack()

    btn_frame = tk.Frame(root, bg="#1a1a2e")
    btn_frame.pack()

    def pick(val):
        choice.set(val)
        root.destroy()

    for label, val in [
        ("  ·-·  Morse → Text  ", "morse_to_string"),
        ("  ·-·  Text → Morse  ", "string_to_morse"),
    ]:
        tk.Button(
            btn_frame, text=label, font=btn_font,
            bg="#16213e", fg="#a0c4ff", activebackground="#0f3460",
            activeforeground="#ffffff", relief=tk.FLAT,
            padx=18, pady=10, cursor="hand2",
            command=lambda v=val: pick(v)
        ).pack(side=tk.LEFT, padx=20)

    root.mainloop()
    return choice.get()


# ─── Main Translator Window ───────────────────────────────────────────────────

LONG_PRESS_THRESHOLD = 0.3   # seconds — tap vs hold for spacebar

class MorseTranslatorApp:
    def __init__(self, mode):
        """
        mode: 'morse_to_string'  — user taps morse in, sees text live
              'string_to_morse'  — user types text, sees morse live
        """
        self.mode = mode

        # Morse-input state
        self.space_press_time = 0.0
        self.space_is_pressed = False
        self.space_timer = None

        self.enter_press_time = 0.0
        self.enter_is_pressed = False
        self.enter_timer = None

        # Buffer holding dots/dashes for the letter currently being typed e.g. [".", "-"]
        # Press Tab to commit the buffer as a letter
        self.current_letter = []

        self._build_window()

    # ── Window Construction ──────────────────────────────────────────────────

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("Morse Translator")
        self.root.geometry("720x500")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 720, 500
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        mono   = tkfont.Font(family="Courier", size=12)
        label_font = tkfont.Font(family="Courier", size=10, weight="bold")
        hint_font  = tkfont.Font(family="Courier", size=9)

        # ── Top status bar ─────────────────────────────────────────────────
        self.status_var = tk.StringVar(value=self._idle_status())
        self.status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            font=label_font, bg="#0f3460", fg="#a0c4ff",
            pady=7, relief=tk.FLAT
        )
        self.status_bar.pack(fill=tk.X)

        # ── Two text boxes ─────────────────────────────────────────────────
        panes = tk.Frame(self.root, bg="#1a1a2e")
        panes.pack(fill=tk.BOTH, expand=True, padx=18, pady=(12, 4))
        panes.columnconfigure(0, weight=1)
        panes.columnconfigure(1, weight=1)
        panes.rowconfigure(1, weight=1)

        # Labels
        morse_lbl_text = "MORSE CODE"
        text_lbl_text  = "PLAIN TEXT"
        if self.mode == "morse_to_string":
            morse_lbl_text += "  ◄ input"
            text_lbl_text  += "  (translated)"
        else:
            morse_lbl_text += "  (translated)"
            text_lbl_text  += "  ◄ input"

        tk.Label(panes, text=morse_lbl_text, font=label_font,
                 bg="#1a1a2e", fg="#7ecbff", anchor="w").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 4))
        tk.Label(panes, text=text_lbl_text, font=label_font,
                 bg="#1a1a2e", fg="#a0ffa0", anchor="w").grid(
            row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 4))

        # Morse box
        morse_bg = "#0d1b2a" if self.mode == "morse_to_string" else "#121212"
        self.morse_box = tk.Text(
            panes, font=mono, bg=morse_bg, fg="#7ecbff",
            insertbackground="#7ecbff", relief=tk.FLAT,
            wrap=tk.WORD, padx=10, pady=10,
            state=tk.NORMAL if self.mode == "morse_to_string" else tk.DISABLED,
            cursor="xterm" if self.mode == "morse_to_string" else "arrow",
        )
        self.morse_box.grid(row=1, column=0, sticky="nsew", padx=(0, 6))

        # Text box
        text_bg = "#0d1b2a" if self.mode == "string_to_morse" else "#121212"
        self.text_box = tk.Text(
            panes, font=mono, bg=text_bg, fg="#a0ffa0",
            insertbackground="#a0ffa0", relief=tk.FLAT,
            wrap=tk.WORD, padx=10, pady=10,
            state=tk.NORMAL if self.mode == "string_to_morse" else tk.DISABLED,
            cursor="xterm" if self.mode == "string_to_morse" else "arrow",
        )
        self.text_box.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

        # Scrollbars
        for box, col in [(self.morse_box, 0), (self.text_box, 1)]:
            sb = tk.Scrollbar(panes, command=box.yview, bg="#1a1a2e",
                              troughcolor="#16213e", relief=tk.FLAT)
            sb.grid(row=1, column=col, sticky="nse", padx=(0 if col else 0, 0))
            box.configure(yscrollcommand=sb.set)

        # ── Hint bar ───────────────────────────────────────────────────────
        if self.mode == "morse_to_string":
            hint = "SPACE: tap=·  hold=—    TAB: commit letter    SHIFT: word break    ENTER: new line    Hold ENTER: finish"
        else:
            hint = "Type in the plain text box. Morse appears live on the left."

        tk.Label(
            self.root, text=hint, font=hint_font,
            bg="#16213e", fg="#555577", pady=5
        ).pack(fill=tk.X, side=tk.BOTTOM)

        # ── Bottom buttons ─────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(side=tk.BOTTOM, pady=8)

        if self.mode == "morse_to_string":
            self.commit_btn = tk.Button(
                btn_frame, text="✔  Commit Letter", font=hint_font,
                bg="#0f3460", fg="#a0c4ff", activebackground="#1a5a9a",
                activeforeground="#ffffff", relief=tk.FLAT,
                padx=16, pady=6, cursor="hand2",
                command=self._on_commit_click
            )
            self.commit_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame, text="Clear All", font=hint_font,
            bg="#16213e", fg="#ff8080", activebackground="#3a1a1a",
            activeforeground="#ffffff", relief=tk.FLAT,
            padx=16, pady=6, cursor="hand2",
            command=self._clear_all
        ).pack(side=tk.LEFT, padx=10)

        # ── Bind events ────────────────────────────────────────────────────
        if self.mode == "morse_to_string":
            # Use add='+' so our handler runs AFTER any widget-level handler,
            # meaning 'break' from a widget cannot suppress these callbacks.
            self.root.bind_all("<KeyPress-space>",    self._on_space_press,   add="+")
            self.root.bind_all("<KeyRelease-space>",  self._on_space_release, add="+")
            self.root.bind_all("<Shift_L>",           self._on_shift_press,   add="+")
            self.root.bind_all("<Shift_R>",           self._on_shift_press,   add="+")
            self.root.bind_all("<KeyPress-Return>",   self._on_enter_press,   add="+")
            self.root.bind_all("<KeyRelease-Return>", self._on_enter_release, add="+")

            # Tab commits the current letter
            self.root.bind_all("<KeyPress-Tab>", self._on_tab_press, add="+")

            # Suppress insertion of literal characters in text widgets
            self.morse_box.bind("<KeyPress-space>",   lambda e: "break")
            self.morse_box.bind("<KeyPress-Return>",  lambda e: "break")
            self.morse_box.bind("<KeyPress-Tab>",     lambda e: "break")
            self.text_box.bind("<KeyPress-space>",    lambda e: "break")
            self.text_box.bind("<KeyPress-Return>",   lambda e: "break")
            self.text_box.bind("<KeyPress-Tab>",      lambda e: "break")
        else:
            # Live translation as user types in text_box
            self.text_box.bind("<<Modified>>", self._on_text_modified)

        self._committed_morse = ""  # all fully committed morse so far
        self.root.focus_force()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _idle_status(self):
        if self.mode == "morse_to_string":
            return "  READY — Tap/hold SPACEBAR to enter Morse code"
        return "  READY — Type plain text in the green box"

    def _clear_all(self):
        for box in (self.morse_box, self.text_box):
            box.configure(state=tk.NORMAL)
            box.delete("1.0", tk.END)
        if self.mode == "string_to_morse":
            self.text_box.configure(state=tk.NORMAL)
            self.morse_box.configure(state=tk.DISABLED)
        else:
            self.morse_box.configure(state=tk.NORMAL)
            self.text_box.configure(state=tk.DISABLED)
        self._committed_morse = ""
        self.current_letter = []
        self.status_var.set(self._idle_status())

    def _append_symbol(self, sym):
        """Add a dot or dash to the current-letter buffer and update the preview."""
        self.current_letter.append(sym)
        # Show in-progress symbols joined (e.g. '.-') as preview
        pending = ''.join(self.current_letter)
        self._redraw_morse(extra=pending)

    def _flush_letter(self):
        """Commit buffered dots/dashes as one letter (e.g. ['-','-'] -> '-- ')."""
        if not self.current_letter:
            return
        # Join WITHOUT spaces so '--' is one morse symbol, then space = letter separator
        letter_morse = ''.join(self.current_letter) + ' '
        self.current_letter = []
        self._committed_morse += letter_morse
        self._redraw_morse()
        self._update_translation_from_morse()

    def _redraw_morse(self, extra=''):
        """Rewrite the morse box: committed content + optional in-progress preview."""
        self.morse_box.configure(state=tk.NORMAL)
        self.morse_box.delete("1.0", tk.END)
        self.morse_box.insert(tk.END, self._committed_morse + extra)
        self.morse_box.see(tk.END)
        self.morse_box.configure(state=tk.DISABLED)

    def _append_morse(self, text):
        """Commit a word-break ( '/ ' ) or newline — flushes pending letter first."""
        self._flush_letter()
        self._committed_morse += text
        self._redraw_morse()
        self._update_translation_from_morse()

    def _update_translation_from_morse(self):
        """Decode _committed_morse (not the box, which may have a pending preview)."""
        decoded = morse_to_string(self._committed_morse.strip()) if self._committed_morse.strip() else ""
        self.text_box.configure(state=tk.NORMAL)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, decoded)
        self.text_box.configure(state=tk.DISABLED)

    # ── Morse Input Handlers (morse_to_string mode) ──────────────────────────

    def _on_space_press(self, event):
        if self.space_timer is not None:
            self.root.after_cancel(self.space_timer)
            self.space_timer = None
        if not self.space_is_pressed:
            self.space_press_time = time.time()
            self.space_is_pressed = True
            self.status_var.set("  ● HOLDING…")
            self.status_bar.configure(bg="#1a3a5c")

    def _on_space_release(self, event):
        self.space_timer = self.root.after(50, self._execute_space_release)

    def _execute_space_release(self):
        self.space_is_pressed = False
        self.space_timer = None
        duration = time.time() - self.space_press_time
        symbol = "—" if duration >= LONG_PRESS_THRESHOLD else "·"
        morse_sym = "-" if duration >= LONG_PRESS_THRESHOLD else "."
        self._append_symbol(morse_sym)
        self.status_var.set(f"  Added: {symbol}   — Keep going, SHIFT=word break, ENTER=new line")
        self.status_bar.configure(bg="#0f3460")

    def _on_commit_click(self):
        """Commit button clicked — commit buffered symbols as a completed letter."""
        if self.current_letter:
            self._flush_letter()
            self.status_var.set("  Letter committed")
        else:
            self.status_var.set("  Nothing to commit — tap/hold SPACE first")
        self.root.focus_force()   # return focus to root for next key input

    def _on_tab_press(self, event):
        """Tab key — same as clicking Commit Letter."""
        self._on_commit_click()

    def _on_shift_press(self, event):
        self._append_morse("/ ")
        self.status_var.set("  Word break added ( / )")

    def _on_enter_press(self, event):
        if self.enter_timer is not None:
            self.root.after_cancel(self.enter_timer)
            self.enter_timer = None
        if not self.enter_is_pressed:
            self.enter_press_time = time.time()
            self.enter_is_pressed = True

    def _on_enter_release(self, event):
        self.enter_timer = self.root.after(50, self._execute_enter_release)

    def _execute_enter_release(self):
        self.enter_is_pressed = False
        self.enter_timer = None
        duration = time.time() - self.enter_press_time
        if duration >= 1.0:
            self.status_var.set("  Done! Close this window when ready.")
            self.status_bar.configure(bg="#1a3a1a")
        else:
            self._append_morse("\n")
            self.status_var.set("  New line added")

    # ── Text Input Handler (string_to_morse mode) ────────────────────────────

    def _on_text_modified(self, event):
        if not self.text_box.edit_modified():
            return
        raw = self.text_box.get("1.0", tk.END).rstrip("\n")
        morse = string_to_morse(raw) if raw.strip() else ""
        self.morse_box.configure(state=tk.NORMAL)
        self.morse_box.delete("1.0", tk.END)
        self.morse_box.insert(tk.END, morse)
        self.morse_box.configure(state=tk.DISABLED)
        self.text_box.edit_modified(False)

    # ── Run ──────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = show_option_selector()
    if mode:
        app = MorseTranslatorApp(mode)
        app.run()