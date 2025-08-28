import eel
import os
import sys
import subprocess
import srt
from datetime import timedelta
from faster_whisper import WhisperModel
import tkinter as tk
from tkinter import filedialog
# NEW: Import spaCy if it's going to be used
try:
    import spacy
except ImportError:
    spacy = None


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

def format_and_save_srt(segments, output_path, split_mode, split_value, use_continuous, use_nlp, nlp_doc):
    """
    The ultimate, advanced function to format subtitles with professional-grade logic.
    """
    # --- Part 1: Pre-process words and identify NLP break points ---
    clean_words = [{'text': w.word.strip().rstrip('-'), 'start': w.start, 'end': w.end} for segment in segments for w in segment.words]
    if not clean_words:
        raise ValueError("Transcription failed to produce any words.")

    # Get preferred break points from NLP if enabled
    nlp_break_points = set()
    if use_nlp and nlp_doc:
        # Find the word index for the end of each noun chunk
        char_to_word_map = {}
        char_count = 0
        for i, word in enumerate(clean_words):
            for _ in range(len(word['text'])):
                char_to_word_map[char_count] = i
                char_count += 1
            char_count += 1 # Account for space
        
        for chunk in nlp_doc.noun_chunks:
            end_word_index = char_to_word_map.get(chunk.end_char -1)
            if end_word_index:
                nlp_break_points.add(end_word_index)

    break_enders = ('.', '?', '!', ',')

    # --- Part 2: Build subtitle lines with advanced logic ---
    new_subs = []
    current_line_words = []
    for i, word in enumerate(clean_words):
        current_line_words.append(word)
        line_text = ' '.join(w['text'] for w in current_line_words)

        finalize_line = False
        is_manual_break = False

        # --- Check all conditions to finalize the current line ---
        # 1. NLP break point (highest priority)
        if use_nlp and i in nlp_break_points:
            finalize_line = True
            is_manual_break = True
        
        # 2. Punctuation break point
        cleaned_word_text = word['text'].strip().rstrip(')"\'')
        if cleaned_word_text.endswith(break_enders):
            finalize_line = True
            is_manual_break = True
        
        # 3. Length limits (word or character count)
        if not is_manual_break: # Only check length if not already broken by punctuation/NLP
            if split_mode == 'words' and len(current_line_words) >= split_value:
                finalize_line = True
            elif split_mode == 'chars' and len(line_text) >= split_value:
                finalize_line = True
        
        # 4. Orphan control (lookahead logic)
        if finalize_line and not is_manual_break and (i + 1) < len(clean_words):
            next_word = clean_words[i+1]
            # If the next word is short and would be alone on a line, pull it back
            if len(next_word['text']) <= 3 and (i + 2 == len(clean_words) or clean_words[i+2]['text'].endswith(break_enders)):
                current_line_words.append(next_word)
                i += 1 # Manually advance the loop
        
        # 5. End of transcript
        if i == len(clean_words) - 1:
            finalize_line = True

        # --- Finalize the line if any condition was met ---
        if finalize_line and current_line_words:
            start_time = timedelta(seconds=current_line_words[0]['start'])
            end_time = timedelta(seconds=current_line_words[-1]['end'])
            final_content = ' '.join(w['text'] for w in current_line_words)
            
            new_subs.append(srt.Subtitle(
                index=len(new_subs) + 1, start=start_time, end=end_time, content=final_content
            ))
            current_line_words = []

    # --- Part 3: Post-process for minimum display time ---
    min_duration = timedelta(seconds=1.2)
    for sub in new_subs:
        duration = sub.end - sub.start
        if duration < min_duration:
            sub.end = sub.start + min_duration

    # --- Part 4: Post-process for gap filling (conditional) ---
    if len(new_subs) > 1:
        if use_continuous: # Always-on style
            for i in range(len(new_subs) - 1):
                new_subs[i].end = new_subs[i+1].start
        else: # Pause-sensitive style
            max_gap_to_fill = timedelta(seconds=1.5)
            for i in range(len(new_subs) - 1):
                gap = new_subs[i+1].start - new_subs[i].end
                if gap < max_gap_to_fill:
                    new_subs[i].end = new_subs[i+1].start

    # Save the composed SRT file
    srt_content = srt.compose(new_subs)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)

# --- The main processing logic, exposed to JavaScript ---
@eel.expose
def start_processing(video_path, model_size, language, split_mode, split_value_str, use_continuous, use_nlp):
    def update_status(message):
        print(message)
        eel.update_status(message)

    output_dir = os.path.dirname(video_path)
    base_filename = os.path.splitext(os.path.basename(video_path))[0]
    temp_audio_file = os.path.join(output_dir, f"{base_filename}_temp_audio.mp3")
    output_srt_file = os.path.join(output_dir, f"{base_filename}_captions.srt")
    
    try:
        split_value = int(split_value_str)

        update_status("Step 1/5: Extracting audio...")
        command = ['ffmpeg', '-i', video_path, '-vn', '-c:a', 'mp3', '-ab', '192k', '-y', temp_audio_file]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        update_status("Audio extracted successfully.")

        update_status(f"Step 2/5: Loading Whisper model '{model_size}'...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        update_status("Model loaded. Starting transcription...")
        segments, _ = model.transcribe(temp_audio_file, language=language, word_timestamps=True)
        segments = list(segments)
        update_status("Transcription complete.")

        nlp_doc = None
        if use_nlp:
            update_status("Step 3/5: Performing NLP analysis (this may be slow)...")
            if spacy is None:
                raise ImportError("spaCy is not installed. Please run 'pip install spacy'.")
            try:
                nlp = spacy.load("en_core_web_sm")
            except OSError:
                raise OSError("spaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'.")
            
            full_text = ' '.join(w.word.strip() for seg in segments for w in seg.words)
            nlp_doc = nlp(full_text)
            update_status("NLP analysis complete.")
        else:
            update_status("Step 3/5: Skipping NLP analysis.")

        update_status("Step 4/5: Formatting subtitles with advanced logic...")
        format_and_save_srt(segments, output_srt_file, split_mode, split_value, use_continuous, use_nlp, nlp_doc)
        update_status(f"Formatted SRT file saved as '{os.path.basename(output_srt_file)}'")
        
        update_status("Step 5/5: Cleaning up temporary files...")
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
eel.start('main.html', size=(700, 900))
print("GUI closed.")