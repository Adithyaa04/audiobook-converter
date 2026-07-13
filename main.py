import tkinter as tk
from tkinter.filedialog import askopenfilename
import threading
import pyttsx3
import PyPDF2
 

book = askopenfilename(filetypes=[("PDF files", "*.pdf")])
if not book:
    raise SystemExit("No file selected.")
 
pdfreader = PyPDF2.PdfReader(book)
pages = pdfreader.pages
current_page = 0


speaker = pyttsx3.init()
is_speaking = False  


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
