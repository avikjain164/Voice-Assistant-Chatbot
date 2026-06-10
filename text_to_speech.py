import os


def speak(text):
    """Convert text to speech using the macOS `say` command."""
    print(f"AI: {text}")
    clean_text = text.replace('"', '').replace('*', '').replace('#', '').strip()
    os.system(f'say "{clean_text}"')
