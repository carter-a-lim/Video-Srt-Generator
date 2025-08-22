# Auto-Caption Generator

A user-friendly desktop application to automatically generate and format `.srt` subtitle files from any video. Built with Python and faster-whisper.

## Download (Easy Installation)

For a simple, one-click experience, download the latest version from the **[Releases Page](https://github.com/carter-a-lim/Video-Srt-Generator.git)**.

Just download the `.zip` file, extract the executable, and run it.

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
