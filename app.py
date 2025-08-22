import eel
import os
import sys
import subprocess
import srt
from datetime import timedelta
from faster_whisper import WhisperModel
import tkinter as tk
from tkinter import filedialog

# Initialize Eel and point it to the 'web' folder
eel.init('web')

# --- Expose a function to open a file dialog ---
@eel.expose
def select_file():
    """ Open a file dialog to select a video file and return its path """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")]
    )
    return file_path

def format_and_save_srt(segments, output_path, split_mode, split_value):
    """
    A more advanced function to format subtitles. It splits lines based on
    word/character limits and respects sentence boundaries.
    """
    all_words = [word for segment in segments for word in segment.words]
    if not all_words:
        raise ValueError("Transcription failed to produce any words.")

    # Punctuation that indicates a sentence end
    sentence_enders = ('.', '?', '!')

    new_subs = []
    current_line_words = []

    for i, word in enumerate(all_words):
        current_line_words.append(word)
        
        # --- Strip each word before joining to calculate length ---
        line_text = ' '.join(w.word.strip() for w in current_line_words)

        # --- Check conditions to finalize the current line ---
        finalize_line = False

        # 1. Split by word count
        if split_mode == 'words' and len(current_line_words) >= split_value:
            finalize_line = True
        
        # 2. Split by character count
        elif split_mode == 'chars':
            if len(line_text) >= split_value and len(current_line_words) > 1:
                last_word = current_line_words.pop()
                finalize_line = True
                all_words.insert(i + 1, last_word)

        # 3. Check for sentence end
        cleaned_word = word.word.strip().rstrip(')"\'')
        if cleaned_word.endswith(sentence_enders):
            finalize_line = True
            
        # 4. Check if it's the last word of the entire transcription
        if i == len(all_words) - 1:
            finalize_line = True

        # --- Create the subtitle if any condition was met ---
        if finalize_line and current_line_words:
            start_time = timedelta(seconds=current_line_words[0].start)
            end_time = timedelta(seconds=current_line_words[-1].end)
            
            # --- FIX HERE: Strip each word before joining for the final content ---
            final_content = ' '.join(w.word.strip() for w in current_line_words)
            
            new_subs.append(srt.Subtitle(
                index=len(new_subs) + 1,
                start=start_time,
                end=end_time,
                content=final_content
            ))
            # Reset for the next line
            current_line_words = []

    # Save the composed SRT file
    srt_content = srt.compose(new_subs)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)


# --- The main processing logic, exposed to JavaScript ---
@eel.expose
def start_processing(video_path, model_size, language, split_mode, split_value_str):
    """
    Main function to orchestrate the process.
    """
    def update_status(message):
        print(message)
        eel.update_status(message)

    output_dir = os.path.dirname(video_path)
    base_filename = os.path.splitext(os.path.basename(video_path))[0]
    temp_audio_file = os.path.join(output_dir, f"{base_filename}_temp_audio.mp3")
    output_srt_file = os.path.join(output_dir, f"{base_filename}_captions.srt")
    
    try:
        split_value = int(split_value_str)

        # 1. Extract Audio
        update_status(f"Step 1/4: Extracting audio from '{os.path.basename(video_path)}'...")
        command = ['ffmpeg', '-i', video_path, '-vn', '-c:a', 'mp3', '-ab', '192k', '-y', temp_audio_file]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        update_status("Audio extracted successfully.")

        # 2. Transcribe Audio
        update_status(f"Step 2/4: Loading Whisper model '{model_size}'...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        update_status("Model loaded. Starting transcription... (This may take a long time)")
        segments, _ = model.transcribe(temp_audio_file, language=language, word_timestamps=True)
        segments = list(segments)
        update_status("Transcription complete.")

        # 3. Format SRT
        update_status(f"Step 3/4: Formatting subtitles (by {split_mode}, max {split_value})...")
        format_and_save_srt(segments, output_srt_file, split_mode, split_value)
        update_status(f"Formatted SRT file saved as '{os.path.basename(output_srt_file)}'")
        
        # 4. Cleanup
        update_status("Step 4/4: Cleaning up temporary files...")
        os.remove(temp_audio_file)
        update_status(f"Process complete! Your caption file is ready.")
        eel.process_finished(True, f"Success! Saved to {output_srt_file}")

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        update_status(error_msg)
        eel.process_finished(False, error_msg)
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)

# Start the Eel application
print("Starting GUI... Close this window to exit.")
eel.start('main.html', size=(700, 850))
print("GUI closed.")