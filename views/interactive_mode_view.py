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
    def __init__(self, main_window, module, controller=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.module = module
        self.controller = controller or InteractiveModeController(main_window, module)

        self.config_service = config_service or ConfigService()
        self.api_key = openai.api_key or self.config_service.get_api_key()
        openai.api_key = self.api_key

        self.session_data = []
        self.attempts = 0
        self.playback_process = None

        self.max_attempts = 3
        self.current_attempt = 1
        self.current_flashcard = None
        self.speech_speed = 1.0
        self.is_listening = False
        self.is_speaking = False
        self.summary = {"gut": [], "mittel": [], "schlecht": []}
        self.recording = False
        self.window_closed = False

        # Verwendung eines temporären Verzeichnisses für Audiodateien
        self.audio_dir = tempfile.mkdtemp(prefix="audio_")
        self.speech_file_path = os.path.join(self.audio_dir, "speech.mp3")
        self.recorded_audio_path = os.path.join(self.audio_dir, "recorded.wav")

        self.title("Interaktiver Lernmodus")
        self.geometry("600x600")
        center_window(self.main_window, self)

        self.chat_frame = scrolledtext.ScrolledText(self, state='disabled', wrap='word', font=("Helvetica", 12))
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.chat_frame.tag_configure('user_message', background='#347004', justify='right', lmargin1=100, lmargin2=100)
        self.chat_frame.tag_configure('partner_message', background='#4d4c4c', justify='left', rmargin=100)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        self.start_button = tk.Button(button_frame, text="Start", command=self.start_interactive_mode)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = tk.Button(button_frame, text="Beenden", command=self.stop_interactive_mode)
        self.stop_button.pack(side="left", padx=10)

        self.bind_all('<space>', lambda event: self.stop_recording())
        self.bind('<FocusIn>', lambda event: self.focus_set())
        self.bind('<space>', lambda event: self.stop_recording())

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_interactive_mode(self):
        if self.is_listening or self.is_speaking or self.window_closed:
            return

        # Deaktiviere den Start-Button
        self.start_button.config(state=tk.DISABLED)

        self.controller.reset_flashcards()
        self.summary = {"gut": [], "mittel": [], "schlecht": []}
        self.display_message("Interaktiver Modus gestartet. Lass uns mit der ersten Frage beginnen.", "System")
        self.speak_text("Interaktiver Modus gestartet. Lass uns mit der ersten Frage beginnen.",
                        listen_after_speech=False, callback=self.ask_next_question)

    def stop_interactive_mode(self):
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
            self.speak_text("Keine weiteren Karteikarten verfügbar. Möchtest du die Karten wiederholen?",
                            listen_after_speech=False)
            self.prompt_for_repeat()

    def prompt_for_repeat(self):
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
                    if self.playback_process and self.playback_process.poll() is None:
                        self.playback_process.terminate()

                    if sys.platform == 'win32':
                        self.playback_process = subprocess.Popen(
                            ['cmd', '/c', f'start /min wmplayer "{self.speech_file_path}"'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    elif sys.platform == 'darwin':
                        self.playback_process = subprocess.Popen(
                            ['afplay', self.speech_file_path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        self.playback_process = subprocess.Popen(
                            ['aplay', self.speech_file_path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
        if self.is_listening or self.window_closed:
            return

        def run_stt():
            if self.window_closed:
                return
            try:
                self.is_listening = True
                self.safe_display_message("Bitte antworte jetzt mündlich (max. 60 Sekunden). Drücke die Leertaste zum Beenden.", "KI-Lernpartner")
                print("Start der Audioaufnahme...")

                duration = 60
                fs = 16000
                channels = 1

                recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='float32')
                self.recording = True

                while self.recording and not self.window_closed:
                    sd.sleep(100)

                sd.stop()
                print("Aufnahme gestoppt.")

                if self.window_closed:
                    return

                sf.write(self.recorded_audio_path, recording, fs)

                print(f"Audio gespeichert unter: {self.recorded_audio_path}")

                if not os.path.exists(self.recorded_audio_path) or os.path.getsize(self.recorded_audio_path) == 0:
                    raise ValueError("Die aufgezeichnete Audiodatei existiert nicht oder ist leer.")

                with wave.open(self.recorded_audio_path, 'rb') as wf:
                    assert wf.getnchannels() == 1, "Audio ist nicht mono."
                    assert wf.getframerate() == 16000, "Audio hat nicht die richtige Abtastrate."
                    assert wf.getsampwidth() == 2, "Audio hat nicht die richtige Bit-Tiefe."
                print("Audio-Datei validiert.")

                with open(self.recorded_audio_path, "rb") as audio_file:
                    transcription = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                user_response = transcription.text.strip()

                self.safe_display_message(f"Transkription: {user_response}", "Nutzer")

                if not user_response:
                    self.safe_display_message("Keine Antwort erkannt. Versuchen wir es mit der nächsten Frage", "KI-Lernpartner")
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
                self.is_listening = False

        threading.Thread(target=run_stt, daemon=True).start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.safe_display_message("Aufnahme gestoppt.", "System")
            print("Aufnahme gestoppt durch Benutzer.")
        else:
            pass

    def evaluate_response(self, user_response):
        if self.window_closed:
            return
        correct_answer = self.current_flashcard.answer

        negative_responses = ["ich weiß es nicht", "weiß nicht", "keine ahnung", "kann ich nicht sagen"]
        if user_response.strip().lower() in negative_responses:
            self.safe_display_message(f"Keine Sorge, hier ist die richtige Antwort: {correct_answer}", "KI-Lernpartner")
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
            f"- Zusätzliche Informationen sind in Ordnung. (Nice to Habe)\n"
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
                        self.safe_display_message(f"Das ist teilweise korrekt. Versuch es noch einmal. ({self.current_attempt}/{self.max_attempts})", "KI-Lernpartner")
                        self.summary["mittel"].append(self.current_flashcard.question)

                        second_prompt = (
                            f"Als KI-Lernpartner möchtest du dem Nutzer helfen, die richtige Antwort zu finden.\n"
                            f"Ursprüngliche Frage: {self.current_flashcard.question}\n"
                            f"Karteikarten-Antwort: {correct_answer}\n"
                            f"Nutzerantwort: {user_response}\n"
                            f"Bewertung der bisherigen Antwort: {evaluation}\n\n"
                            f"Bitte formuliere die ursprüngliche Frage um, um dem Nutzer einen Hinweis zu geben. Gib **nur** die umformulierte Frage aus."
                        )
                        print("Generiere eine verbesserte Frage für den Nutzer...")
                        correction_response = openai.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Du bist ein hilfreicher KI-Lernpartner."},
                                {"role": "user", "content": second_prompt}
                            ],
                            max_tokens=150
                        )
                        corrected_question = correction_response.choices[0].message.content.strip()
                        print(f"Korrigierte Frage: {corrected_question}")
                        self.current_attempt += 1
                        self.safe_display_message(f"Neue Frage: {corrected_question}", "KI-Lernpartner")
                        self.speak_text("Vielleicht hilft dir diese Frage weiter: " + corrected_question)
                    else:
                        self.safe_display_message(f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}", "KI-Lernpartner")
                        self.summary["schlecht"].append(self.current_flashcard.question)
                        def after_feedback():
                            self.ask_next_question()
                        self.speak_text(f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}", callback=after_feedback)

                elif "schlecht" in evaluation:
                    if self.current_attempt < self.max_attempts:
                        self.safe_display_message(f"Deine Antwort geht in eine falsche Richtung ({self.current_attempt}/{self.max_attempts})", "KI-Lernpartner")
                        self.summary["schlecht"].append(self.current_flashcard.question)

                        third_prompt = (
                            f"Als KI-Lernpartner möchtest du dem Nutzer helfen, die richtige Antwort zu finden.\n"
                            f"Ursprüngliche Frage: {self.current_flashcard.question}\n"
                            f"Karteikarten-Antwort: {correct_answer}\n"
                            f"Nutzerantwort: {user_response}\n"
                            f"Bewertung der bisherigen Antwort: {evaluation}\n\n"
                            f"Bitte formuliere die ursprüngliche Frage um und gib dem Nutzer einen Tipp. Gib **nur** die umformulierte Frage und den Tipp aus."
                        )
                        print("Generiere einen Tipp für den Nutzer...")
                        correction_response = openai.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Du bist ein hilfreicher KI-Lernpartner."},
                                {"role": "user", "content": third_prompt}
                            ],
                            max_tokens=150
                        )
                        tip_corrected_question = correction_response.choices[0].message.content.strip()
                        print(f"Frage und Tipp: {tip_corrected_question}")
                        self.current_attempt += 1
                        self.safe_display_message(f"Frage und Tipp: {tip_corrected_question}", "KI-Lernpartner")
                        self.speak_text("Hier ist ein Tipp für dich: " + tip_corrected_question)
                    else:
                        self.safe_display_message(f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}", "KI-Lernpartner")
                        self.summary["schlecht"].append(self.current_flashcard.question)
                        def after_feedback():
                            self.ask_next_question()
                        self.speak_text(f"Maximale Versuche erreicht. Die richtige Antwort lautet: {correct_answer}", callback=after_feedback)

                elif "gar nicht" in evaluation:
                    self.safe_display_message(f"Keine Sorge, die richtige Antwort lautet: {correct_answer}", "KI-Lernpartner")
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
        # Entfernt die Abfrage if self.window_closed: return, damit auch bei Fenster geschlossen eine Zusammenfassung erstellt wird.
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
        if hasattr(self, 'summary_text') and self.summary_text.strip():
            cleaned_summary = self.summary_text.replace("**", "")
            messagebox.showinfo("Zusammenfassung", cleaned_summary)
        else:
            messagebox.showinfo("Zusammenfassung", "Keine Zusammenfassung verfügbar.")

    def stop_listening(self):
        if self.is_listening:
            self.recording = False
            self.safe_display_message("Aufnahme wird beendet.", "System")
            print("Aufnahme wird beendet.")
        else:
            pass

    def display_message(self, message, sender):
        if self.window_closed:
            return

        def update_chat():
            if self.window_closed:
                return
            try:
                self.chat_frame.configure(state='normal')
                timestamp = time.strftime("%H:%M")

                if sender == "Nutzer" or sender == "Du":
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
        if self.window_closed:
            return
        self.after(0, lambda: self.display_message(message, sender))

    def on_closing(self):
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
