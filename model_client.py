import json
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def _load_config():
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        raise RuntimeError(f"Missing configuration file: {CONFIG_PATH}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in configuration file: {exc}") from exc


def _ollama_available() -> bool:
    return shutil.which("ollama") is not None


def _is_linux_arm() -> bool:
    return platform.system() == "Linux" and platform.machine().startswith(("arm", "aarch64"))


def query_model(user_text):
    """Query the configured Ollama model and return the response."""
    config = _load_config()
    model = config.get("ollama_model")
    if not model:
        raise RuntimeError("Configuration must include 'ollama_model'")

    if not _ollama_available():
        return (
            "Ollama CLI is not available on this system. "
            "Install Ollama and ensure it is on PATH, or configure a smaller local model."
        )

    fallback_model = config.get("safe_model")
    if _is_linux_arm() and fallback_model:
        model = fallback_model

    if _is_linux_arm() and "26b" in model.lower() and not fallback_model:
        return (
            "The configured model appears too large for a Raspberry Pi/ARM device. "
            "Please set `safe_model` in config.json to a small Ollama model such as `gemma2:1b`."
        )

    prompt_template = config.get(
        "prompt_template",
        "Answer this in one short sentence: {user_text}"
    )
    prompt = prompt_template.format(user_text=user_text)

    think = config.get("think", False)
    hide_thinking = config.get("hide_thinking", True)

    command = ["ollama", "run"]
    if hide_thinking:
        command.append("--hidethinking")
    command.append(f"--think={str(think).lower()}")
    command.extend([model, prompt])

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        if result.stderr:
            print(f"Ollama stderr: {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception:
        return "I am having trouble connecting to my local processing unit."
