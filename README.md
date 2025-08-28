# Auto-Caption Generator

A user-friendly desktop application to automatically generate and format `.srt` subtitle files from any video. Built with Python and faster-whisper.


## Version 2.0.0 - The Professional Flow Update! 🎉

This is a major upgrade that introduces several advanced features for creating more natural, professional-grade captions.

**New Features:**
- ✨ **Advanced NLP Analysis:** A new option to use grammatical analysis (`spaCy`) for the most intelligent and natural line breaks possible.
- 🧠 **Orphan Word Prevention:** The formatting logic now avoids leaving single, short words on a line, improving readability.
- ⏱️ **Minimum Display Time:** Captions are now guaranteed to be on-screen long enough to be read, preventing jarring "flashes" of text.
- ⏯️ **Pause-Sensitive Captions:** A new option to disable "always-on" captions, which respects long, dramatic pauses in speech.
- 🐛 **Bug Fixes:** General improvements to the formatting engine.


**Note:** You still need to have [FFmpeg](https://ffmpeg.org/download.html) installed on your system for the application to work.

![Screenshot of the App](https://github.com/user-attachments/assets/ca61d81e-bd27-4fe3-b6ad-f547e9cca445)

## Features

- **High-Quality Transcription:** Powered by OpenAI's Whisper model for accurate speech-to-text.
- **Flexible Line Splitting:** Choose to format captions by maximum words per line OR characters per line.
- **Natural Pacing:** Automatically creates new lines at the end of sentences for better readability.
- **Simple GUI:** An easy-to-use interface for selecting files and configuring settings.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

## Prerequisites

Before you begin, you need to have the following installed on your system:

1.  **Python 3.8+:** [Download Python](https://www.python.org/downloads/)
2.  **FFmpeg:** This is crucial for audio extraction. [Download FFmpeg](https://ffmpeg.org/download.html) and make sure it's added to your system's PATH.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/carter-a-lim/Video-Srt-Generator.git](https://github.com/carter-a-lim/Video-Srt-Generator.git)
    cd Video-Srt-Generator
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Simply run the `app.py` script to launch the application:
```bash
python app.py
