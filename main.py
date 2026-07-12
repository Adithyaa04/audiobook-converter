import pyttsx3
import PyPDF2
from tkinter.filedialog import *

book = askopenfilename()
pdfreader = PyPDF2.PdfReader(book)
pages = len(pdfreader.pages)

speaker = pyttsx3.init()  

for num in range(0, pages):
    page = pdfreader.pages[num]     
    text = page.extract_text()      
    speaker.say(text)
    speaker.runAndWait()