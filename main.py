import tkinter as tk
from tkinter.filedialog import askopenfilename
import threading
import pyttsx3
import PyPDF2
import pythoncom  # ships with pywin32, which pyttsx3 already depends on for its SAPI5 driver

# ── Load the PDF ──────────────────────────────────────────────
book = askopenfilename(filetypes=[("PDF files", "*.pdf")])
if not book:
    raise SystemExit("No file selected.")

pdfreader = PyPDF2.PdfReader(book)
pages = pdfreader.pages
current_page = 0

# ── TTS engine ──────────────────────────────────────────────────
# IMPORTANT: pyttsx3's Windows driver (SAPI5) is built on COM, and COM
# objects are tied to the thread that created them. Creating ONE engine
# on the main thread and then calling runAndWait() on it from a
# background thread (like the original version did) crashes with a
# fatal COM/GIL error. The fix: each playback session creates its own
# engine, on the same thread that will use it, with COM explicitly
# initialized for that thread.
is_speaking = False        # tracks whether we're currently mid-playback
current_engine = None       # the engine object currently speaking, if any
engine_lock = threading.Lock()  # protects current_engine from race conditions


# ── GUI setup ───────────────────────────────────────────────────
root = tk.Tk()
root.title("PDF Audiobook")
root.geometry("750x550")

text_widget = tk.Text(root, wrap="word", font=("Arial", 14), padx=10, pady=10)
text_widget.pack(fill="both", expand=True, padx=10, pady=10)
text_widget.tag_config("highlight", background="yellow")

status_label = tk.Label(root, text="", font=("Arial", 10))
status_label.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)


def load_page(num):
    """Load a page's text into the Text widget and clear any old highlight."""
    global current_page
    current_page = num
    text_widget.delete("1.0", "end")
    page_text = pages[num].extract_text() or "(No extractable text on this page)"
    text_widget.insert("1.0", page_text)
    status_label.config(text=f"Page {num + 1} of {len(pages)}")


def highlight_range(start_index, end_index):
    """Runs on the MAIN thread only. Moves the highlight to a new word."""
    text_widget.tag_remove("highlight", "1.0", "end")
    text_widget.tag_add("highlight", start_index, end_index)
    # Auto-scroll so the highlighted word stays visible
    text_widget.see(start_index)


def on_word(name, location, length):
    """
    Fires on the WORKER thread, once per word, while speaker.runAndWait()
    is running. `location` is the character offset into the text we
    handed to speaker.say(), and `length` is how many characters the
    word is.

    We must NOT touch the Text widget directly from this thread —
    tkinter isn't thread-safe. Instead we schedule the actual update
    to run on the main thread via root.after(0, ...).
    """
    start = f"1.0+{location}c"
    end = f"1.0+{location + length}c"
    root.after(0, highlight_range, start, end)


def speak_current_page():
    """
    Runs on a background thread so the GUI doesn't freeze while speaking.

    Creates its OWN pyttsx3 engine, on this thread, with COM explicitly
    initialized first. This is what avoids the "GIL held but released" /
    SAPI5 crash — the engine now lives entirely on the thread that uses it.
    """
    global is_speaking, current_engine

    is_speaking = True
    text = text_widget.get("1.0", "end-1c")  # -1c drops the trailing newline Text always adds

    pythoncom.CoInitialize()  # required before touching SAPI5 on this thread
    try:
        engine = pyttsx3.init()
        engine.connect("started-word", on_word)

        with engine_lock:
            current_engine = engine

        engine.say(text)
        engine.runAndWait()
    finally:
        with engine_lock:
            current_engine = None
        pythoncom.CoUninitialize()

    is_speaking = False
    root.after(0, lambda: text_widget.tag_remove("highlight", "1.0", "end"))


def play():
    if is_speaking:
        return  # already playing, ignore extra clicks
    threading.Thread(target=speak_current_page, daemon=True).start()


def stop():
    """Stop whatever engine is currently speaking, if any."""
    with engine_lock:
        if current_engine is not None:
            current_engine.stop()


def next_page():
    stop()
    if current_page < len(pages) - 1:
        load_page(current_page + 1)


def prev_page():
    stop()
    if current_page > 0:
        load_page(current_page - 1)


# ── Buttons ─────────────────────────────────────────────────────
tk.Button(button_frame, text="◀ Prev", width=10, command=prev_page).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="▶ Play", width=10, command=play).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="■ Stop", width=10, command=stop).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Next ▶", width=10, command=next_page).grid(row=0, column=3, padx=5)

# ── Start ───────────────────────────────────────────────────────
load_page(0)
root.mainloop()