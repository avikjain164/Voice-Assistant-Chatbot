import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional

from voice_assistant.model_client import ModelClient
from voice_assistant.speech_to_text import DEFAULT_TRIGGER_PHRASE, SpeechToText
from voice_assistant.text_to_speech import TextToSpeech

EXIT_COMMANDS = {"exit", "stop", "quit", "goodbye", "shutdown"}


class VoiceAssistantApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("540x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#eff3f7")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", background="#eff3f7", foreground="#1f2937")
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#111827")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#4b5563")
        style.configure("Info.TLabel", font=("Segoe UI", 10))

        self.tts = TextToSpeech().speak
        self.stt = SpeechToText()
        self.model = ModelClient()
        self.trigger_phrase = DEFAULT_TRIGGER_PHRASE
        self.running = False

        self.status_var = tk.StringVar(value="Press Start to listen for 'Hey Assistant'.")
        self.button_text = tk.StringVar(value="Start Listening")
        self._build_ui()

    def _build_ui(self) -> None:
        header = ttk.Label(self.root, text="Hey Assistant", style="Title.TLabel")
        header.pack(pady=(18, 6))

        subtitle = ttk.Label(
            self.root,
            text="Say the wake phrase to activate the assistant. Then speak your command clearly.",
            style="Subtitle.TLabel",
            wraplength=480,
            justify="center",
        )
        subtitle.pack(pady=(0, 6))

        trigger_note = ttk.Label(
            self.root,
            text="Wake phrase: 'Hey Assistant'",
            style="Subtitle.TLabel",
            wraplength=480,
            justify="center",
        )
        trigger_note.pack(pady=(0, 14))

        card = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        card.pack(fill="both", padx=16, pady=(0, 14), expand=True)

        self.log = ScrolledText(
            card,
            height=13,
            state="disabled",
            font=("Segoe UI", 10),
            wrap="word",
            bg="#f7fafc",
            bd=0,
            padx=10,
            pady=10,
        )
        self.log.pack(fill="both", expand=True)

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=16, pady=(0, 12))
        ttk.Label(status_frame, text="Status:", style="Info.TLabel").pack(side="left")
        ttk.Label(status_frame, textvariable=self.status_var, style="Info.TLabel").pack(side="left", padx=(6, 0))

        button_frame = tk.Frame(self.root, bg="#eff3f7")
        button_frame.pack(pady=(0, 16))
        self.start_button = tk.Button(
            button_frame,
            textvariable=self.button_text,
            command=self.start_listening,
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            bd=1,
            relief="ridge",
            padx=18,
            pady=10,
            font=("Segoe UI", 11, "bold"),
            highlightthickness=0,
        )
        self.start_button.pack(side="left", padx=8)
        tk.Button(
            button_frame,
            text="Quit",
            command=self.stop,
            bg="#f3f4f6",
            fg="#111827",
            activebackground="#e5e7eb",
            bd=1,
            relief="ridge",
            padx=18,
            pady=10,
            font=("Segoe UI", 11, "bold"),
            highlightthickness=0,
        ).pack(side="left", padx=8)

    def _append_log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.yview("end")
        self.log.configure(state="disabled")

    def log_message(self, message: str) -> None:
        self.root.after(0, self._append_log, message)

    def update_status(self, text: str) -> None:
        self.root.after(0, self.status_var.set, text)

    def start_listening(self) -> None:
        if self.running:
            return
        self.running = True
        self.start_button.configure(state="disabled")
        self.button_text.set("Listening...")
        self.start_button.configure(bg="#16a34a", activebackground="#15803d")
        self.status_var.set("Listening for wake phrase...")
        self.log_message("Wake-word detection active. Say 'Hey Assistant'.")
        threading.Thread(target=self._main_loop, daemon=True).start()

    def _reset_start_button(self) -> None:
        self.start_button.configure(state="normal")
        self.button_text.set("Start Listening")
        self.start_button.configure(bg="#2563eb", activebackground="#1d4ed8")

    def _main_loop(self) -> None:
        while self.running:
            self.update_status("Listening for wake phrase...")
            trigger_text = self.stt.listen_for_trigger(self.trigger_phrase)

            if not self.running:
                break

            if trigger_text is None:
                continue

            self.log_message(f"Wake phrase detected: {trigger_text}")
            self.update_status("Wake phrase detected. Listening for command...")
            self.tts("Yes? How can I help?")

            user_command = self.stt.listen_for_command()
            if not self.running:
                break

            if user_command is None:
                self.log_message("No command detected. Waiting for wake phrase again.")
                self.tts("I didn't catch that. Please try again.")
                continue

            self.log_message(f"You said: {user_command}")
            if user_command.strip().lower() in EXIT_COMMANDS:
                self.tts("Goodbye.")
                self.stop()
                break

            self.update_status("Processing your command...")
            ai_response = self.model.query(user_command)
            self.log_message(f"Assistant: {ai_response}")
            self.tts(ai_response)
            self.update_status("Waiting for wake phrase...")

        self.update_status("Stopped.")
        if self.running is False:
            self.root.after(0, self._reset_start_button)

    def stop(self) -> None:
        self.running = False
        try:
            self.root.quit()
        except tk.TclError:
            pass


def main() -> None:
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()


if __name__ == "__main__":
    main()
