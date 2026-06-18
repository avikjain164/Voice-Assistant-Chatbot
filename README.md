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

## Raspberry Pi Compatibility

- This app can run on Linux-based Raspberry Pi devices, but the default model `gemma4:26b` is too large for a 4 GB or 8 GB Pi.
- For a Raspberry Pi, use a much smaller Ollama model and install an ARM-compatible Ollama build if available.
- Recommended hardware:
  - Raspberry Pi 5 with 8 GB RAM for the best experience.
  - Raspberry Pi 4 with 8 GB RAM may work with a lightweight model.
- On Raspberry Pi, install offline TTS support such as `espeak`, or install `pyttsx3`.
- If you want fully offline speech recognition, install `pocketsphinx` and set `SPEECH_RECOGNITION_BACKEND=sphinx` before running.

## Recommended configuration updates

If you use Raspberry Pi or a low-memory machine, set `safe_model` in `config.json` to a small, ARM-friendly Ollama model such as `gemma2:1b` or another tiny model.
