import speech_recognition as sr


def listen():
    """Capture microphone audio and return the recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening... (Speak clearly into your microphone)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            print("Processing audio...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("System: Could not understand audio.")
            return None
        except sr.RequestError:
            print("System: Speech recognition service unavailable.")
            return None
        except Exception as e:
            print(f"System: Error: {e}")
            return None
