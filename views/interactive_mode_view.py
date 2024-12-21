import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

import openai
import json
import os
import time
import sounddevice as sd
import soundfile as sf
from playsound import playsound
import wave
import sys
import subprocess
import tempfile
import shutil

from services import config_service
from services.config_service import ConfigService
from controller.interactive_mode_controller import InteractiveModeController
from utils.window_utils import center_window


class InteractiveModeView(tk.Toplevel):
    """
    This class provides an interactive learning view window for the user.
    It manages a separate Tkinter Toplevel window and controls an interactive
    Q&A session with speech recognition (STT) and text-to-speech (TTS).

    All user-facing texts are in German, while docstrings and comments are in English
    for pdoc documentation.

    :param main_window: The main application window (parent) of this Toplevel window.
    :param module: The module (flashcard set) used in the interactive session.
    :param controller: An optional InteractiveModeController instance; if None, a new one is created.
    """

    def __init__(self, main_window, module, controller=None):
        """
        Constructor method that initializes the interactive mode view and its UI components.
        Also sets up session management variables, audio file paths, and event bindings.
        """
        super().__init__(main_window)
        self.main_window = main_window
        self.module = module
        self.controller = controller or InteractiveModeController(main_window, module)

        # Services and configuration
        self.config_service = config_service or ConfigService()
        self.api_key = openai.api_key or self.config_service.get_api_key()
        openai.api_key = self.api_key

        # Session state management
        self.session_data = []
        self.attempts = 0
        self.playback_process = None
        self.max_attempts = 3
        self.current_attempt = 1
        self.current_flashcard = None
        self.speech_speed = 1.0

        # Flags for controlling concurrency
        self.is_listening = False      # True if we are currently recording user audio
        self.is_speaking = False       # True if TTS playback is ongoing
        self.is_transcribing = False   # True if we are currently running Whisper STT
        self.recording = False         # True while sounddevice is actively recording

        self.window_closed = False

        # Result summary
        self.summary = {"gut": [], "mittel": [], "schlecht": []}

        # Using a temporary directory to store audio files
        self.audio_dir = tempfile.mkdtemp(prefix="audio_")
        self.speech_file_path = os.path.join(self.audio_dir, "speech.mp3")
        self.recorded_audio_path = os.path.join(self.audio_dir, "recorded.wav")

        self.title("Interaktiver Lernmodus")
        self.geometry("600x600")
        center_window(self.main_window, self)

        # Create a scrollable text widget for chat display
        self.chat_frame = scrolledtext.ScrolledText(self, state='disabled', wrap='word', font=("Helvetica", 12))
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure message tags for visual differentiation
        self.chat_frame.tag_configure('user_message', background='#347004', justify='right', lmargin1=100, lmargin2=100)
        self.chat_frame.tag_configure('partner_message', background='#4d4c4c', justify='left', rmargin=100)

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        self.start_button = tk.Button(button_frame, text="Start", command=self.start_interactive_mode)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = tk.Button(button_frame, text="Beenden", command=self.stop_interactive_mode)
        self.stop_button.pack(side="left", padx=10)

        # Bindings for space key
        # We use an intermediary method (on_space_pressed) to control early stop of recording
        # but prevent multiple presses while TTS or STT is active.
        self.bind_all('<space>', self.on_space_pressed)
        self.bind('<FocusIn>', lambda event: self.focus_set())

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_space_pressed(self, event=None):
        """
        This method is triggered when the space key is pressed.

        Logic:
        - If TTS (is_speaking) or STT (is_transcribing) is active, ignore the space press.
        - If we are not currently recording, ignore the space press.
        - Otherwise, stop the recording to accept the user's answer early.
        """
        if self.is_speaking or self.is_transcribing:
            print("Leertaste ignoriert: KI spricht oder transkribiert noch.")
            return

        if not self.recording:
            print("Leertaste ignoriert: Keine Aufnahme aktiv.")
            return

        # If we're here, the user is speaking (is_listening=True), and we can stop early
        self.stop_recording()

    def start_interactive_mode(self):
        """
        Starts the interactive learning mode.
        Resets flashcards, clears summaries, and begins the first question.
        Also provides a spoken introduction to the user in German.
        """
        if self.is_listening or self.is_speaking or self.window_closed:
            return

        self.start_button.config(state=tk.DISABLED)
        self.controller.reset_flashcards()
        self.controller.reset_flashcards()
        self.summary = {"gut": [], "mittel": [], "schlecht": []}

        self.display_message("Interaktiver Modus gestartet. Lass uns mit der ersten Frage beginnen.", "System")
        self.speak_text(
            "Interaktiver Modus gestartet. Lass uns mit der ersten Frage beginnen.",
            listen_after_speech=False,
            callback=self.ask_next_question
        )

    def stop_interactive_mode(self):
        """
        Stops the interactive mode gracefully.
        Halts any ongoing recording or speech playback, generates a summary,
        and closes the current window, displaying a summary popup afterwards.
        """
        if self.window_closed:
            return

        self.window_closed = True
        self.stop_recording()
        self.stop_listening()

        if self.is_speaking:
            self.is_speaking = False
            if self.playback_process and self.playback_process.poll() is None:
                self.playback_process.terminate()
                self.playback_process = None

        self.start_button.config(state=tk.NORMAL)
        self.generate_summary()
        self.destroy()
        self.main_window.after(100, self.show_summary_popup)

    def ask_next_question(self):
        """
        Fetches the next flashcard question.
        If no more flashcards are available, prompts the user to repeat or end the session.
        """
        if self.window_closed:
            return

        self.current_attempt = 1
        flashcard = self.controller.move_to_next_flashcard()
        if flashcard:
            self.current_flashcard = flashcard
            self.attempts = 0
            question = self.controller.get_current_flashcard_question()
            self.display_message(f"Frage: {question}", "KI-Lernpartner")
            self.speak_text(question)
        else:
            self.display_message("Keine weiteren Karteikarten verfügbar. Möchtest du die Karten wiederholen?", "KI-Lernpartner")
            self.speak_text("Keine weiteren Karteikarten verfügbar. Möchtest du die Karten wiederholen?", listen_after_speech=False)
            self.prompt_for_repeat()

    def prompt_for_repeat(self):
        """
        Asks the user if they want to repeat the flashcards.
        Creates two buttons in the chat (Ja/Nein).
        If 'Ja', flashcards are reset. If 'Nein', the session ends.
        """
        if self.window_closed:
            return

        def yes_action():
            self.safe_display_message("Du hast gewählt, die Karteikarten zu wiederholen.", "System")
            self.controller.reset_flashcards()
            self.summary = {"gut": [], "mittel": [], "schlecht": []}
            self.chat_frame.configure(state='normal')
            self.chat_frame.delete("repeat_buttons_start", "repeat_buttons_end")
            self.chat_frame.configure(state='disabled')
            self.ask_next_question()

        def no_action():
            self.safe_display_message("Du hast gewählt, die Lernsession zu beenden.", "System")
            self.chat_frame.configure(state='normal')
            self.chat_frame.delete("repeat_buttons_start", "repeat_buttons_end")
            self.chat_frame.configure(state='disabled')
            self.stop_interactive_mode()

        self.chat_frame.configure(state='normal')
        self.chat_frame.mark_set("repeat_buttons_start", tk.END)
        yes_button = tk.Button(self.chat_frame, text="Ja", command=yes_action)
        no_button = tk.Button(self.chat_frame, text="Nein", command=no_action)
        self.chat_frame.window_create(tk.END, window=yes_button)
        self.chat_frame.insert(tk.END, "   ")
        self.chat_frame.window_create(tk.END, window=no_button)
        self.chat_frame.insert(tk.END, "\n")
        self.chat_frame.mark_set("repeat_buttons_end", tk.END)
        self.chat_frame.configure(state='disabled')
        self.chat_frame.see(tk.END)

    def speak_text(self, text, callback=None, listen_after_speech=True):
        """
        Converts the given text into speech (TTS) using OpenAI (model='tts-1')
        and plays it back via a platform-specific audio player.

        :param text: The text to be spoken in German.
        :param callback: A callable executed after speech playback finishes.
        :param listen_after_speech: If True, listening for a user answer starts automatically.
        """
        if self.is_speaking or self.window_closed:
            return

        def run_tts():
            if self.window_closed:
                return
            try:
                self.is_speaking = True
                response = openai.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=text,
                    speed=1.1
                )
                audio_data = response.content

                with open(self.speech_file_path, "wb") as speech_file:
                    speech_file.write(audio_data)

                print(f"Audio gespeichert unter: {self.speech_file_path}")

                if not self.window_closed:
                    # If something is still playing, terminate it
                    if self.playback_process and self.playback_process.poll() is None:
                        self.playback_process.terminate()

                    # Platform-specific audio playback
                    if sys.platform == 'win32':
                        self.playback_process = subprocess.Popen(
                            ['cmd', '/c', f'start /min wmplayer "{self.speech_file_path}"'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    elif sys.platform == 'darwin':
                        self.playback_process = subprocess.Popen(
                            ['afplay', self.speech_file_path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    else:
                        self.playback_process = subprocess.Popen(
                            ['aplay', self.speech_file_path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )

                    self.playback_process.wait()

            except Exception as e:
                self.safe_display_message(f"Fehler bei der Sprachausgabe: {str(e)}", "System")
                print(f"Fehler bei der Sprachausgabe: {str(e)}")
            finally:
                self.is_speaking = False
                self.playback_process = None
                if callback and not self.window_closed:
                    self.after(0, callback)
                elif listen_after_speech and not self.window_closed:
                    self.listen_for_answer()

        threading.Thread(target=run_tts, daemon=True).start()

    def listen_for_answer(self):
        """
        Starts listening for the user's spoken answer.
        Records up to 60 seconds of audio at 48 kHz, then transcribes the result with Whisper.

        We do NOT set is_transcribing to True until AFTER the recording ends,
        so the user can press space to stop early.
        """
        if self.is_listening or self.window_closed:
            return

        def run_stt():
            if self.window_closed:
                return
            try:
                # Start listening/recording, so the user can press space
                self.is_listening = True
                self.safe_display_message(
                    "Bitte antworte jetzt mündlich (max. 60 Sekunden). Drücke die Leertaste zum Beenden.",
                    "KI-Lernpartner"
                )
                print("Start der Audioaufnahme...")

                duration = 60
                fs = 48000  # Higher sample rate for better audio quality
                channels = 1

                # Record audio for up to 60 seconds or until stopped by space
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='float32')
                self.recording = True

                # Keep waiting until user stops (self.recording=False) or window closes
                while self.recording and not self.window_closed:
                    sd.sleep(100)
                sd.stop()

                # Recording phase is done
                self.is_listening = False

                if self.window_closed:
                    print("Fenster bereits geschlossen, breche ab.")
                    return

                sf.write(self.recorded_audio_path, recording, fs)
                print(f"Audio gespeichert unter: {self.recorded_audio_path}")

                if not os.path.exists(self.recorded_audio_path) or os.path.getsize(self.recorded_audio_path) == 0:
                    raise ValueError("Die aufgezeichnete Audiodatei existiert nicht oder ist leer.")

                # Now we set is_transcribing = True to block space if user tries again
                self.is_transcribing = True

                # Validate the audio file
                with wave.open(self.recorded_audio_path, 'rb') as wf:
                    assert wf.getnchannels() == 1, "Audio ist nicht mono."
                    assert wf.getframerate() == 48000, "Audio hat nicht die richtige Abtastrate (erwartet: 48000)."
                    assert wf.getsampwidth() == 2, "Audio hat nicht die richtige Bit-Tiefe."
                print("Audio-Datei validiert.")

                # Transcribe with Whisper
                with open(self.recorded_audio_path, "rb") as audio_file:
                    transcription = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                user_response = transcription.text.strip()
                self.safe_display_message(f"Transkription: {user_response}", "Nutzer")

                if not user_response:
                    self.safe_display_message(
                        "Keine Antwort erkannt. Versuchen wir es mit der nächsten Frage",
                        "KI-Lernpartner"
                    )
                    self.ask_next_question()
                    return

                self.evaluate_response(user_response)

            except AssertionError as ae:
                self.safe_display_message(f"Audio Validierungsfehler: {str(ae)}", "System")
                print(f"Audio Validierungsfehler: {str(ae)}")
            except Exception as e:
                self.safe_display_message(f"Fehler bei der Aufnahme oder Verarbeitung: {str(e)}", "System")
                print(f"Fehler bei der Aufnahme oder Verarbeitung: {str(e)}")
            finally:
                self.is_transcribing = False

        threading.Thread(target=run_stt, daemon=True).start()

    def stop_recording(self):
        """
        Stops the current recording if it is in progress.
        Logs a message and updates the UI accordingly.
        """
        if self.recording:
            self.recording = False
            self.safe_display_message("Aufnahme gestoppt.", "System")
            print("Aufnahme gestoppt durch Benutzer.")
        else:
            print("stop_recording() wurde aufgerufen, aber es wurde nicht aufgenommen.")

    def evaluate_response(self, user_response):
        """
        Evaluates the user's response against the correct flashcard answer.
        Calls the assistant to rate the user's answer and provides feedback/hints
        or reveals the correct answer.

        :param user_response: The transcribed user response.
        """
        if self.window_closed:
            return

        correct_answer = self.current_flashcard.answer
        negative_responses = ["ich weiß es nicht", "weiß nicht", "keine ahnung", "kann ich nicht sagen"]

        if user_response.strip().lower() in negative_responses:
            self.safe_display_message(
                f"Keine Sorge, hier ist die richtige Antwort: {correct_answer}",
                "KI-Lernpartner"
            )
            self.summary["schlecht"].append(self.current_flashcard.question)

            def after_feedback():
                self.ask_next_question()

            self.speak_text(f"Keine Sorge, hier ist die richtige Antwort: {correct_answer}", callback=after_feedback)
            return

        prompt = (
            f"Als KI-Lernpartner sollst du die Antwort des Nutzers bewerten.\n"
            f"Karteikarten-Antwort: {correct_answer}\n"
            f"Nutzerantwort: {user_response}\n"
            f"Bitte bewerte, wie gut die Nutzerantwort mit der Karteikarten-Antwort übereinstimmt, unter Berücksichtigung folgender Punkte:\n"
            f"- Die Reihenfolge der Informationen ist egal.\n"
            f"- Zusätzliche Informationen sind in Ordnung (Nice to Have).\n"
            f"- Wenn die Kerninhalte (Must Have) übereinstimmen, ist die Antwort korrekt.\n"
            f"- Wenn der Nutzer 'Ich weiß es nicht' oder Ähnliches sagt, bewerte es als 'gar nicht'.\n\n"
            f"Antworte **nur** mit einer der folgenden Bewertungen:\n"
            f"- 'ganz'\n"
            f"- 'mittel'\n"
            f"- 'schlecht'\n"
            f"- 'gar nicht'\n"
        )

        def run_evaluation():
            if self.window_closed:
                return
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du bist ein hilfreicher KI-Lernpartner für Karteikarten."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                evaluation = response.choices[0].message.content.strip().lower()
                print(f"Bewertung von ChatGPT: {evaluation}")

                if "ganz" in evaluation:
                    self.safe_display_message("Das ist korrekt! Gut gemacht.", "KI-Lernpartner")
                    self.summary["gut"].append(self.current_flashcard.question)

                    def after_feedback():
                        self.ask_next_question()

                    self.speak_text("Das ist korrekt! Gut gemacht.", callback=after_feedback)

                elif "mittel" in evaluation:
                    if self.current_attempt < self.max_attempts:
                        self.safe_display_message(
                            f"Das ist teilweise korrekt. Versuch es noch einmal. ({self.current_attempt}/{self.max_attempts})",
                            "KI-Lernpartner"
                        )
                        self.summary["mittel"].append(self.current_flashcard.question)

                        second_prompt = (
                            f"Als KI-Lernpartner möchtest du dem Nutzer helfen, die richtige Antwort zu finden.\n"
                            f"Ursprüngliche Frage: {self.current_flashcard.question}\n"
                            f"Karteikarten-Antwort: {correct_answer}\n"
                            f"Nutzerantwort: {user_response}\n"
                            f"Bewertung der bisherigen Antwort: {evaluation}\n\n"
                            f"Bitte formuliere die ursprüngliche Frage um, um dem Nutzer einen Hinweis zu geben. "
                            f"Gib **nur** die umformulierte Frage aus."
                        )
                        correction_response = openai.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Du bist ein hilfreicher KI-Lernpartner."},
                                {"role": "user", "content": second_prompt}
                            ],
                            max_tokens=150
                        )
                        corrected_question = correction_response.choices[0].message.content.strip()
                        self.current_attempt += 1
                        self.safe_display_message(f"Neue Frage: {corrected_question}", "KI-Lernpartner")
                        self.speak_text("Vielleicht hilft dir diese Frage weiter: " + corrected_question)
                    else:
                        self.safe_display_message(
                            f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}",
                            "KI-Lernpartner"
                        )
                        self.summary["schlecht"].append(self.current_flashcard.question)

                        def after_feedback():
                            self.ask_next_question()

                        self.speak_text(
                            f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}",
                            callback=after_feedback
                        )

                elif "schlecht" in evaluation:
                    if self.current_attempt < self.max_attempts:
                        self.safe_display_message(
                            f"Deine Antwort geht in eine falsche Richtung ({self.current_attempt}/{self.max_attempts})",
                            "KI-Lernpartner"
                        )
                        self.summary["schlecht"].append(self.current_flashcard.question)

                        third_prompt = (
                            f"Als KI-Lernpartner möchtest du dem Nutzer helfen, die richtige Antwort zu finden.\n"
                            f"Ursprüngliche Frage: {self.current_flashcard.question}\n"
                            f"Karteikarten-Antwort: {correct_answer}\n"
                            f"Nutzerantwort: {user_response}\n"
                            f"Bewertung der bisherigen Antwort: {evaluation}\n\n"
                            f"Bitte formuliere die ursprüngliche Frage um und gib dem Nutzer einen Tipp. "
                            f"Gib **nur** die umformulierte Frage und den Tipp aus."
                        )
                        correction_response = openai.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Du bist ein hilfreicher KI-Lernpartner."},
                                {"role": "user", "content": third_prompt}
                            ],
                            max_tokens=150
                        )
                        tip_corrected_question = correction_response.choices[0].message.content.strip()
                        self.current_attempt += 1
                        self.safe_display_message(f"Frage und Tipp: {tip_corrected_question}", "KI-Lernpartner")
                        self.speak_text("Hier ist ein Tipp für dich: " + tip_corrected_question)
                    else:
                        self.safe_display_message(
                            f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}",
                            "KI-Lernpartner"
                        )
                        self.summary["schlecht"].append(self.current_flashcard.question)

                        def after_feedback():
                            self.ask_next_question()

                        self.speak_text(
                            f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}",
                            callback=after_feedback
                        )

                elif "gar nicht" in evaluation:
                    self.safe_display_message(
                        f"Keine Sorge, die richtige Antwort lautet: {correct_answer}",
                        "KI-Lernpartner"
                    )
                    self.summary["schlecht"].append(self.current_flashcard.question)

                    def after_feedback():
                        self.ask_next_question()

                    self.speak_text(f"Keine Sorge, die richtige Antwort lautet: {correct_answer}", callback=after_feedback)

                else:
                    self.safe_display_message(f"Die richtige Antwort lautet: {correct_answer}", "KI-Lernpartner")
                    self.summary["schlecht"].append(self.current_flashcard.question)

                    def after_feedback():
                        self.ask_next_question()

                    self.speak_text(f"Die richtige Antwort lautet: {correct_answer}", callback=after_feedback)

            except Exception as e:
                self.safe_display_message(f"Fehler bei der Bewertung: {str(e)}", "System")
                print(f"Fehler bei der Bewertung: {str(e)}")

        threading.Thread(target=run_evaluation, daemon=True).start()

    def generate_summary(self):
        """
        Generates a summary of the entire session, listing which questions were answered
        'gut', 'mittel', or 'schlecht'. This text is inserted into the chat and also used
        by a popup after the session ends.
        """
        gut = "\n".join(self.summary["gut"]) if self.summary["gut"] else "Keine guten Antworten."
        mittel = "\n".join(self.summary["mittel"]) if self.summary["mittel"] else "Keine mittleren Antworten."
        schlecht = "\n".join(self.summary["schlecht"]) if self.summary["schlecht"] else "Keine schlechten Antworten."

        summary_text = (
            f"**Zusammenfassung:**\n\n"
            f"**Gut gelaufene Themen:**\n{gut}\n\n"
            f"**Mittel gelaufene Themen:**\n{mittel}\n\n"
            f"**Schlecht gelaufene Themen:**\n{schlecht}"
        )
        self.display_message(summary_text, "System")
        print("Zusammenfassung generiert.")
        print(summary_text)

        self.summary_text = summary_text

    def show_summary_popup(self):
        """
        Displays the summary popup after the window is closed.
        """
        if hasattr(self, 'summary_text') and self.summary_text.strip():
            cleaned_summary = self.summary_text.replace("**", "")
            messagebox.showinfo("Zusammenfassung", cleaned_summary)
        else:
            messagebox.showinfo("Zusammenfassung", "Keine Zusammenfassung verfügbar.")

    def stop_listening(self):
        """
        Interrupts the current listening process if it is active,
        forcing the recording to stop.
        """
        if self.is_listening:
            self.recording = False
            self.safe_display_message("Aufnahme wird beendet.", "System")
            print("Aufnahme wird beendet.")
        else:
            pass

    def display_message(self, message, sender):
        """
        Displays a given message in the chat frame with a given sender label.

        :param message: The text to display.
        :param sender: The role of the message sender (e.g., 'Nutzer', 'KI-Lernpartner', 'System').
        """
        if self.window_closed:
            return

        def update_chat():
            if self.window_closed:
                return
            try:
                self.chat_frame.configure(state='normal')
                timestamp = time.strftime("%H:%M")

                if sender in ("Nutzer", "Du"):
                    tag = 'user_message'
                else:
                    tag = 'partner_message'

                self.chat_frame.insert(tk.END, f"[{timestamp}] {sender}: {message}\n\n", tag)
                self.chat_frame.configure(state='disabled')
                self.chat_frame.see(tk.END)
            except tk.TclError:
                pass

        self.after(0, update_chat)

    def safe_display_message(self, message, sender):
        """
        Safely displays a message on the Tkinter event loop thread to avoid concurrency issues.
        """
        if self.window_closed:
            return
        self.after(0, lambda: self.display_message(message, sender))

    def on_closing(self):
        """
        Handles the window closing event.
        Stops any ongoing processes, generates a summary, and then destroys this window.
        Finally, it shows the summary popup and cleans up any temporary audio files.
        """
        if self.window_closed:
            return

        self.window_closed = True
        self.stop_recording()
        self.stop_listening()

        if self.is_speaking:
            self.is_speaking = False
            if self.playback_process and self.playback_process.poll() is None:
                self.playback_process.terminate()
                self.playback_process = None

        self.generate_summary()
        self.destroy()
        self.main_window.after(100, self.show_summary_popup)
        shutil.rmtree(self.audio_dir, ignore_errors=True)
