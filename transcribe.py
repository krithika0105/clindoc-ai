import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def transcribe_audio(file_path: str, language: str = None) -> str:
    """
    Transcribe an audio file using Groq's Whisper V3.
    
    Args:
        file_path: Path to the audio file.
        language: Optional ISO 639-1 language code (e.g. 'hi', 'ta', 'kn').
                  If None, Whisper auto-detects the language.
    
    Returns:
        Transcribed text as a string.
    """
    with open(file_path, "rb") as audio_file:
        kwargs = dict(
            file=(file_path, audio_file, "audio/mpeg"),
            model="whisper-large-v3",
            response_format="text",
            temperature=0.0,
        )
        if language:
            kwargs["language"] = language

        transcription = client.audio.transcriptions.create(**kwargs)

    # Groq returns a string when response_format="text"
    return transcription if isinstance(transcription, str) else transcription.text