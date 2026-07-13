# PDF Audiobook Converter 

A Python desktop app that converts PDF documents into spoken audio, with real-time word-by-word highlighting as the text is read aloud.

## Features

-  Open any PDF file and extract its text
-  Text-to-speech playback using `pyttsx3`
-  Live word highlighting synced with speech
-  Play / Stop controls
-  Page navigation (Next / Previous)

## Planned Features

- [ ] Adjustable playback speed and voice selection
- [ ] Export audio to file (save as MP3/WAV)
- [ ] Save and resume reading progress
- [ ] OCR support for scanned PDFs
- [ ] Chapter/bookmark navigation
- [ ] Skip blank or image-only pages automatically

## Tech Stack

- **Python 3.12**
- [`pyttsx3`](https://pypi.org/project/pyttsx3/) — offline text-to-speech engine
- [`PyPDF2`](https://pypi.org/project/pypdf2/) — PDF text extraction
- `tkinter` — GUI and file dialog
- `threading` — keeps the GUI responsive while audio plays

## Installation

1. Clone this repository
```bash
   git clone https://github.com/Adithyaa04/audiobook-converter.git
   cd audiobook-converter
```

2. Install dependencies
```bash
   pip install pyttsx3 PyPDF2
```

## Usage

Run the script:
```bash
python main.py
```

1. A file picker will open — select the PDF you want to convert
2. The current page's text will load into the window
3. Click **Play** to start listening — the word currently being spoken will highlight in real time
4. Use **Next / Previous** to move between pages, or **Stop** to end playback

## How It Works

- `PyPDF2` extracts raw text from each page of the PDF
- `pyttsx3` converts that text to speech and fires a `started-word` event for every word it speaks, including its position in the text
- That event is used to highlight the corresponding word in the GUI in sync with the audio
- Since speech playback blocks the main thread, it runs on a background thread — GUI updates are safely queued back to the main thread using `root.after()`

## Known Limitations

- Only works with text-based PDFs — scanned/image-only PDFs won't extract readable text (OCR support planned)
- Voice quality depends on the TTS voices installed on your OS
- No pause/resume mid-sentence yet — Stop ends playback entirely

## Contributing

This is a learning project — issues, suggestions, and pull requests are welcome!

## License

MIT