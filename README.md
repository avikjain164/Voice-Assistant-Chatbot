# voice_assistant

Small reusable package wrapping local model access and simple STT/TTS helpers.

Quick usage:

```python
from voice_assistant import ModelClient, listen, speak

client = ModelClient()
text = listen()
if text:
    resp = client.query(text)
    speak(resp)
```

Packaging: this repo contains a minimal `pyproject.toml` so it can be installed
locally with `pip install -e .`.

To use the new Tkinter-based assistant UI, run:

```bash
python main.py
```

Make sure Ollama is installed and available on your PATH before running the app.
