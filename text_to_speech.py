import os
import platform
import shutil
import subprocess
from typing import List, Optional


def _run_command(command: List[str]) -> None:
    try:
        subprocess.run(command, check=False)
    except Exception:
        pass


def _speak_with_mac_say(text: str) -> None:
    _run_command(["say", text])


def _speak_with_espeak(text: str) -> None:
    _run_command(["espeak", text])


def _pyttsx3_available() -> bool:
    try:
        import pyttsx3  # type: ignore
        return True
    except ImportError:
        return False


def _speak_with_pyttsx3(text: str) -> bool:
    try:
        import pyttsx3  # type: ignore
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        return False


def _backend_available(name: str) -> bool:
    return shutil.which(name) is not None


def speak(text: str, backend: Optional[str] = None) -> None:
    """Convert text to speech with a platform-safe backend."""
    print(f"AI: {text}")
    clean_text = text.replace('"', '').replace('*', '').replace('#', '').strip()
    if not clean_text:
        return

    system = platform.system()
    chosen_backend = backend
    if chosen_backend is None or chosen_backend == "auto":
        if system == "Darwin" and _backend_available("say"):
            chosen_backend = "say"
        elif _backend_available("espeak"):
            chosen_backend = "espeak"
        elif _pyttsx3_available():
            chosen_backend = "pyttsx3"
        else:
            chosen_backend = "print"

    if chosen_backend == "say" and system == "Darwin":
        _speak_with_mac_say(clean_text)
    elif chosen_backend == "espeak":
        _speak_with_espeak(clean_text)
    elif chosen_backend == "pyttsx3":
        if not _speak_with_pyttsx3(clean_text):
            print(clean_text)
    else:
        print(clean_text)
