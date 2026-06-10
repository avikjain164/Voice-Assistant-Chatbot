from typing import Optional

import speech_recognition as sr

DEFAULT_TRIGGER_PHRASE = "hey assistant"


def listen() -> Optional[str]:
    """Compatibility wrapper for module-level listen."""
    return SpeechToText().listen()


def _recognize_audio(
    recognizer: sr.Recognizer,
    source: sr.AudioSource,
    timeout: int = 5,
    phrase_time_limit: int = 4,
) -> Optional[str]:
    try:
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        print("Processing audio...")
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("System: Could not understand audio.")
        return None
    except sr.RequestError:
        print("System: Speech recognition service unavailable.")
        return None
    except sr.WaitTimeoutError:
        return None
    except Exception as e:
        print(f"System: Error: {e}")
        return None


class SpeechToText:
    """Lightweight wrapper that exposes `listen` and wake-word helpers."""

    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 250
        self.recognizer.pause_threshold = 0.4
        self.recognizer.non_speaking_duration = 0.25
        self.microphone = sr.Microphone()
        self._calibrate()

    def _calibrate(self) -> None:
        with self.microphone as source:
            print("Calibrating microphone. Please stay quiet...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def _capture_audio(
        self,
        timeout: int,
        phrase_time_limit: int,
    ) -> Optional[str]:
        with self.microphone as source:
            return _recognize_audio(
                self.recognizer,
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

    def listen(self) -> Optional[str]:
        print("\nListening... (Speak clearly into your microphone)")
        return self._capture_audio(timeout=4, phrase_time_limit=5)

    def listen_for_trigger(
        self,
        trigger_phrase: str = DEFAULT_TRIGGER_PHRASE,
        timeout: int = 4,
        phrase_time_limit: int = 4,
    ) -> Optional[str]:
        print(f"\nWaiting for wake phrase: '{trigger_phrase}'")
        text = self._capture_audio(timeout=timeout, phrase_time_limit=phrase_time_limit)
        if text is None:
            return None
        print(f"Heard: {text}")
        if trigger_phrase.lower() in text.lower():
            return text
        return None

    def listen_for_command(self, timeout: int = 5, phrase_time_limit: int = 6) -> Optional[str]:
        print("\nListening for command...")
        return self._capture_audio(timeout=timeout, phrase_time_limit=phrase_time_limit)
