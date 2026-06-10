import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


def _load_config_from_path(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        raise RuntimeError(f"Missing configuration file: {path}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in configuration file: {exc}") from exc


class ModelClient:
    """Client for querying a local Ollama model.

    Usage:
        client = ModelClient()
        response = client.query("Hello")

    You can pass a `config` dict directly or a `config_path`.
    """

    def __init__(self, config_path: Optional[Path] = None, config: Optional[Dict[str, Any]] = None):
        if config is not None:
            self._config = config
        else:
            if config_path is None:
                config_path = Path(__file__).resolve().parent.parent / "config.json"
            self._config = _load_config_from_path(config_path)

    def query(self, user_text: str) -> str:
        config = self._config
        model = config.get("ollama_model")
        if not model:
            raise RuntimeError("Configuration must include 'ollama_model'")

        prompt_template = config.get("prompt_template", "Answer this in one short sentence: {user_text}")
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
                encoding="utf-8",
            )
            if result.stderr:
                # Preserve stderr for diagnostics but don't raise
                print(f"Ollama stderr: {result.stderr.strip()}")
            return result.stdout.strip()
        except Exception:
            return "I am having trouble connecting to my local processing unit."


def query_model(user_text: str, config_path: Optional[Path] = None, config: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function for one-off queries.

    Either `config` (dict) or `config_path` (Path) may be provided.
    """
    client = ModelClient(config_path=config_path, config=config)
    return client.query(user_text)
