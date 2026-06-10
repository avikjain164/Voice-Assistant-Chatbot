import os
from typing import Optional


def speak(text: str, backend: Optional[str] = None) -> None:
    """Convert text to speech.

    Default behavior uses macOS `say`. A `backend` parameter is reserved
    for future extension (e.g., `pyttsx3`, cloud TTS).
    """
    print(f"AI: {text}")
    clean_text = text.replace('"', '').replace('*', '').replace('#', '').strip()
    os.system(f'say "{clean_text}"')


class TextToSpeech:
    """Wrapper class for TTS functionality."""

    def speak(self, text: str) -> None:
        return speak(text)
