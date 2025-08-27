// --- Global variable to store the selected file path ---
let selectedVideoPath = null;

// --- Get references to all HTML elements ---
const selectFileBtn = document.getElementById('select-file-btn');
const fileNameDisplay = document.getElementById('file-name-display');
const modelSelect = document.getElementById('model-select');
const languageSelect = document.getElementById('language-select');
const startBtn = document.getElementById('start-btn');
const statusLog = document.getElementById('status-log');
const splitModeRadios = document.querySelectorAll('input[name="split-mode"]');
const wordsContainer = document.getElementById('words-container');
const charsContainer = document.getElementById('chars-container');
const wordsInput = document.getElementById('words-input');
const charsInput = document.getElementById('chars-input');

// New advanced options checkboxes
const continuousCaptionsCheck = document.getElementById('continuous-captions-check');
const nlpCheck = document.getElementById('nlp-check');


// --- Event listener for the file selection button ---
selectFileBtn.addEventListener('click', async () => {
    const path = await eel.select_file()();
    if (path) {
        selectedVideoPath = path;
        fileNameDisplay.textContent = path.split(/[\\/]/).pop();
        fileNameDisplay.style.fontStyle = 'normal';
        fileNameDisplay.style.color = '#d4d4d4';
        startBtn.disabled = false;
    }
});

// --- Event listeners for radio buttons to toggle input fields ---
splitModeRadios.forEach(radio => {
    radio.addEventListener('change', (event) => {
        if (event.target.value === 'words') {
            wordsContainer.classList.remove('hidden');
            charsContainer.classList.add('hidden');
        } else {
            wordsContainer.classList.add('hidden');
            charsContainer.classList.remove('hidden');
        }
    });
});


// --- Event listener for the start button ---
startBtn.addEventListener('click', () => {
    if (!selectedVideoPath) {
        update_status("Error: No video file selected.");
        return;
    }

    startBtn.disabled = true;
    startBtn.textContent = "Processing...";
    statusLog.innerHTML = "";

    // Get all settings from the form
    const modelSize = modelSelect.value;
    const language = languageSelect.value;
    const splitMode = document.querySelector('input[name="split-mode"]:checked').value;
    const splitValue = splitMode === 'words' ? wordsInput.value : charsInput.value;
    const useContinuous = continuousCaptionsCheck.checked;
    const useNlp = nlpCheck.checked;
    
    // Call the main Python processing function with all new arguments
    eel.start_processing(selectedVideoPath, modelSize, language, splitMode, splitValue, useContinuous, useNlp);
});


// --- Functions exposed to Python ---
eel.expose(update_status, 'update_status');
function update_status(message) {
    statusLog.innerHTML += message + '\n';
    statusLog.scrollTop = statusLog.scrollHeight;
}

eel.expose(process_finished, 'process_finished');
function process_finished(success, message) {
    startBtn.disabled = false;
    startBtn.textContent = "Generate Captions";
    
    const finalMessage = success ? `✅ ${message}` : `❌ ${message}`;
    update_status(`\n-----------------------\n${finalMessage}`);
    
    if (success) {
        alert("Caption generation successful!");
    } else {
        alert("An error occurred during caption generation. Check the log for details.");
    }
}