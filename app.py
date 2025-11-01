import streamlit as st
import os
from google import genai
from gtts import gTTS
import io
import pandas as pd
import pypdf
from typing import Dict, Any, Optional

# --- Configuration and Utility Functions ---

# Define supported languages and their ISO 639-1 codes for gTTS and for display
LANGUAGE_CODES: Dict[str, str] = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese (Mandarin)": "zh-cn",
    "Hindi": "hi",
    "Arabic": "ar",
    "English": "en"
    # Add more languages as needed, checking gTTS support
}

# Supported file extensions for upload
ALLOWED_EXTENSIONS = ['pdf', 'txt', 'csv', 'xlsx']

def translate_text_with_gemini(api_key: str, text: str, target_language: str) -> Optional[str]:
    """Translates text using the Gemini API."""
    if not text:
        return None
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"Translate the following text into {target_language}.\n\nText: {text}"
        
        # CORRECTED: The function body was redundant and had incorrect indentation
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        # CORRECTED: Use .text and strip whitespace
        return response.text.strip()
    
    # CORRECTED: Fixed incorrect indentation and multiple redundant except blocks
    except Exception as e: 
        st.error(f"An API error occurred: {e}")
        return None

def convert_text_to_speech(text: str, lang_code: str) -> Optional[io.BytesIO]:
    """Converts text to speech using gTTS and returns an audio BytesIO object."""
    
    if not text:
        return None
        
    try:
        # gTTS object - the 'lang_code' must be a supported ISO 639-1 code
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save the audio into a BytesIO object (in-memory file)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    
    # CORRECTED: Fixed missing colon in except statement
    except Exception as e:
        st.error(f"Speech Conversion Error (gTTS): The language code '{lang_code}' might not be supported for speech. Error: {e}")
        return None

def extract_text_from_uploaded_file(uploaded_file: Any) -> Optional[str]:
    """Extracts text content from various file types (PDF, TXT, CSV, XLSX)."""
    text_content = "" # Initialize variable
    
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == "pdf":
            # Use pypdf to read the PDF
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                # CORRECTED: Added fallback to empty string and fixed indentation
                text_content += page.extract_text() or ""
            
        elif file_extension == "txt":
            # Read text files
            text_content = uploaded_file.getvalue().decode("utf-8")

        elif file_extension in ['csv', 'xlsx', 'xls']:
            # Use pandas for tabular data
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension in ["xlsx", "xls"]:
                df = pd.read_excel(uploaded_file)
            
            # Convert DataFrame to a single string for translation (simple approach)
            text_content = df.to_string(index=False)
            
            # CORRECTED: Fixed f-string quotes and ensures this is inside the elif block
            st.warning(f"For large or complex tables, the simple text representation might lose formatting. Consider translating sections or columns for better results.")
        
        # CORRECTED: Aligned else with its corresponding if/elif block
        else:
            # CORRECTED: Fixed f-string quotes
            st.error(f"Unsupported file type: {file_extension}. Please use a supported format: {', '.join(ALLOWED_EXTENSIONS)}")
            return None

        # CORRECTED: Fixed missing colon
        if not text_content:
            st.warning("The uploaded file was empty or contained no readable text.")
            return None

        return text_content
    
    # CORRECTED: Aligned except with its corresponding try block and fixed f-string quotes
    except Exception as e:
        st.error(f"File Processing Error: Could not read the file. Error: {e}")
        return None

# --- Streamlit Application Layout ---

# CORRECTED: Added colon to function definition
def main():
    # CORRECTED: Added quotes around string arguments
    st.set_page_config(page_title="Universal AI Translator & Speaker", layout="wide")
    st.title("Universal AI Translator & Speaker")
    st.markdown(
        "Translate text instantly using the power of Google Gemini, then convert the translation to speech and download the audio!"
    )
    st.divider()

    # Sidebar for API Key and setup
    # CORRECTED: Added colon to 'with' statement
    with st.sidebar:
        st.header("Setup & Configuration")
        # Get the API key from the user
        # CORRECTED: Added quotes around string arguments
        gemini_api_key = st.text_input(
            "Enter your Gemini API Key",
            type="password",
            help="Get your key from Google AI Studio."
        )
        
        # CORRECTED: Added colon to if/else blocks and fixed indentation
        if gemini_api_key:
            st.success("API Key successfully entered.")
        else:
            st.error("Please enter your Gemini API Key to proceed.")
            
        st.header("Upload or Input")
        # Option to upload a file
        # CORRECTED: Added quotes around string arguments
        uploaded_file = st.file_uploader(
            "Upload a File for Translation", 
            type=ALLOWED_EXTENSIONS
        )

    # Main application logic
    # CORRECTED: Added colon
    if not gemini_api_key:
        st.stop() # Stop execution if the key is missing

    # --- Input Section ---
    st.header("1. Input Text or File Content")
    
    source_text = "" # Initialize source_text
    
    # CORRECTED: Added colon and fixed indentation
    if uploaded_file:
        # CORRECTED: Fixed f-string quotes
        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            # CORRECTED: Fixed indentation
            source_text = extract_text_from_uploaded_file(uploaded_file)
        
        # CORRECTED: Added colon and fixed indentation
        if source_text:
            # CORRECTED: Fixed string arguments
            source_text = st.text_area(
                "Extracted Text (You can edit this)", 
                source_text, 
                height=250, 
                key="source_text_area"
            )
        # CORRECTED: Added colon and fixed indentation
        else:
            # If extraction failed, allow manual entry as fallback
            # CORRECTED: Fixed string arguments
            source_text = st.text_area("Enter Text for Translation", "", height=250, key="source_text_area")
    # CORRECTED: Added colon and fixed indentation
    else:
        # Default manual entry if no file is uploaded
        # CORRECTED: Fixed string arguments
        source_text = st.text_area("Enter Text for Translation", "", height=250, key="source_text_area")

    # Update source_text from the text area if a file was uploaded but text was edited
    # CORRECTED: Ensure st.session_state is checked consistently
    if "source_text_area" in st.session_state:
        source_text = st.session_state.source_text_area

    # --- Translation and Action Section ---
    st.header("2. Choose Language & Action")
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    # CORRECTED: Fixed string arguments
    target_language_name = col1.selectbox(
        "Select Target Language", 
        options=list(LANGUAGE_CODES.keys())
    )
    
    target_lang_code = LANGUAGE_CODES.get(target_language_name, 'en') # Default to English code
    
    # Button to trigger the translation and speech process
    # CORRECTED: Added colon and fixed string arguments
    if col2.button("Translate & Generate Speech", use_container_width=True):
        # CORRECTED: Added colon
        if not source_text or source_text.isspace():
            st.error("Please enter or upload some text to translate.")
        # CORRECTED: Added colon
        else:
            # CORRECTED: Fixed f-string quotes
            with st.spinner(f"Translating to {target_language_name} and generating audio..."):
                
                # 1. Translate
                translated_text = translate_text_with_gemini(
                    api_key=gemini_api_key, 
                    text=source_text, 
                    target_language=target_language_name
                )
                
                # CORRECTED: Added colon
                if translated_text:
                    # Store the result in session state for display and speech
                    st.session_state['translated_text'] = translated_text
                    
                    # 2. Generate Speech
                    audio_bytes_io = convert_text_to_speech(translated_text, target_lang_code)
                    st.session_state['audio_bytes_io'] = audio_bytes_io
                    st.session_state['target_language_name'] = target_language_name
                    st.session_state['target_lang_code'] = target_lang_code

# --- Output Section ---

    st.header("3. Results")
    
    # CORRECTED: Fixed indentation
    if 'translated_text' in st.session_state and st.session_state['translated_text']:
        translated_text = st.session_state['translated_text']
        audio_bytes_io = st.session_state.get('audio_bytes_io')
        target_language_name = st.session_state['target_language_name']
        target_lang_code = st.session_state['target_lang_code']

        # Display the translated text
        # CORRECTED: Fixed f-string quotes
        st.subheader(f"Translated Text ({target_language_name})")
        st.success(translated_text)

        # Display the audio player
        # CORRECTED: Added colon
        if audio_bytes_io:
            st.subheader("Audio Playback")
            # Use the audio object in Streamlit
            st.audio(audio_bytes_io.getvalue(), format='audio/mp3')

            # Button to download the audio file
            st.subheader("Download Audio")
            audio_bytes_io.seek(0) # Reset pointer for download
            # CORRECTED: Fixed f-string quotes and mime type
            st.download_button(
                label=f"Download {target_language_name} Speech (MP3)",
                data=audio_bytes_io.read(),
                file_name=f"translated_speech_{target_lang_code}.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
        # CORRECTED: Added colon
        else:
            st.warning("Speech could not be generated for this translation.")

# CORRECTED: Added colon
if __name__ == "__main__":
    main()
