import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading

from utils.mousewheel_scroll_util import bind_mousewheel
from utils.window_utils import center_window

class GenerateFlashcardsController:
    """
    Controller to manage the generation of flashcards using ChatGPT.
    Handles the creation of the flashcard generation popup, interaction with ChatGPT, and display of generated flashcards.
    """

    def __init__(self, main_window, module, chatgpt_service):
        """
        Initializes the controller with necessary services and settings.

        Args:
            main_window (tk.Tk): The main window of the application.
            module (object): The module for which flashcards will be generated.
            chatgpt_service (object): The ChatGPT service to generate flashcards.
        """
        self.main_window = main_window
        self.module = module
        self.db_service = self.main_window.db_service
        self.chatgpt_service = chatgpt_service
        self.generate_flashcards_view = None

    def open_generate_flashcards_popup(self):
        """
        Opens a popup for generating flashcards using ChatGPT. Displays a text input area and handles the process of
        generating flashcards asynchronously.
        """
        if not self.chatgpt_service:
            messagebox.showerror("Fehler", "ChatGPT API-Key ist nicht gesetzt.")
            return

        self.generate_flashcards_view = tk.Toplevel(self.main_window)
        self.generate_flashcards_view.title("Karteikarten mit ChatGPT generieren")
        self.generate_flashcards_view.geometry("600x400")
        self.generate_flashcards_view.transient(self.main_window)
        self.generate_flashcards_view.grab_set()
        center_window(self.main_window, self.generate_flashcards_view)

        label = tk.Label(self.generate_flashcards_view, text="Geben Sie den Textabschnitt ein:", font=("Arial", 12))
        label.pack(pady=10)
        text_section_entry = tk.Text(self.generate_flashcards_view, height=10, width=70, font=("Arial", 12))
        text_section_entry.pack(pady=5)

        def generate_flashcards():
            """
            Generates flashcards by passing the entered text to the ChatGPT service.
            Displays progress and handles any errors during the generation process.
            """
            text_section = text_section_entry.get("1.0", tk.END).strip()
            if text_section:
                loading_popup = tk.Toplevel(self.generate_flashcards_view)
                loading_popup.title("Generiere Karteikarten...")
                loading_label = tk.Label(loading_popup, text="Karteikarten werden generiert, bitte warten...")
                loading_label.pack(pady=10)
                progress_bar = ttk.Progressbar(loading_popup, mode='indeterminate')
                progress_bar.pack(pady=10)
                progress_bar.start()

                center_window(self.generate_flashcards_view, loading_popup)

                flashcards_result = []
                error_result = [None]

                def generate():
                    try:
                        flashcards = self.chatgpt_service.generate_flashcards(text_section)
                        flashcards_result.extend(flashcards)
                    except Exception as e:
                        error_result[0] = str(e)

                thread = threading.Thread(target=generate)
                thread.start()

                def check_thread():
                    if thread.is_alive():
                        self.generate_flashcards_view.after(100, check_thread)
                    else:
                        progress_bar.stop()
                        loading_popup.destroy()
                        if error_result[0]:
                            messagebox.showerror("Fehler", f"Fehler beim Generieren der Karteikarten: {error_result[0]}")
                        elif flashcards_result:
                            self.show_flashcards_editor(flashcards_result)
                        else:
                            messagebox.showwarning("Warnung", "Keine Karteikarten generiert. Bitte versuchen Sie es erneut.")

                check_thread()
            else:
                messagebox.showwarning("Warnung", "Bitte einen Textabschnitt eingeben.")

        button_frame = tk.Frame(self.generate_flashcards_view)
        button_frame.pack(pady=20)

        generate_button = tk.Button(
            button_frame,
            text="Generieren",
            command=generate_flashcards,
            width=15,
            bg="#2196F3",
            fg="black"
        )
        generate_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(
            button_frame,
            text="Abbrechen",
            command=self.generate_flashcards_view.destroy,
            width=15,
            bg="#f44336",
            fg="black"
        )
        cancel_button.pack(side=tk.RIGHT, padx=10)

    def show_flashcards_editor(self, flashcards):
        """
        Displays a popup where the user can edit, delete, or save the generated flashcards.

        Args:
            flashcards (list): List of generated flashcards to be displayed and edited.
        """
        self.generate_flashcards_view.destroy()
        editor_view = tk.Toplevel(self.main_window)
        editor_view.title("Generierte Karteikarten")
        editor_view.geometry("600x500")
        editor_view.transient(self.main_window)
        editor_view.grab_set()
        center_window(self.main_window, editor_view)

        main_frame = tk.Frame(editor_view)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        scroll_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        bind_mousewheel(scroll_frame, canvas)

        for idx, fc in enumerate(flashcards):
            frame = tk.LabelFrame(scroll_frame, text=f"Karteikarte {idx+1}", padx=10, pady=10)
            frame.pack(fill="x", expand=True, padx=10, pady=5)

            question_label = tk.Label(frame, text="Frage:", font=("Arial", 10))
            question_label.pack(anchor='w')
            question_entry = tk.Text(frame, height=3, width=70)
            question_entry.insert(tk.END, fc['question'])
            question_entry.pack()

            answer_label = tk.Label(frame, text="Antwort:", font=("Arial", 10))
            answer_label.pack(anchor='w')
            answer_entry = tk.Text(frame, height=5, width=70)
            answer_entry.insert(tk.END, fc['answer'])
            answer_entry.pack()

            def delete_flashcard(fc=fc, frame=frame):
                """
                Deletes the selected flashcard from the list and the UI.
                """
                flashcards.remove(fc)
                frame.destroy()

            delete_button = tk.Button(frame, text="Löschen", command=delete_flashcard, bg="#f44336", fg="black")
            delete_button.pack(anchor='e', pady=5)

            fc['question_entry'] = question_entry
            fc['answer_entry'] = answer_entry

        bind_mousewheel(scroll_frame, canvas)

        button_frame = tk.Frame(editor_view)
        button_frame.pack(fill="x")

        def save_all():
            """
            Saves all edited flashcards to the database.
            """
            try:
                for fc in flashcards:
                    question = fc['question_entry'].get("1.0", tk.END).strip()
                    answer = fc['answer_entry'].get("1.0", tk.END).strip()
                    self.db_service.add_flashcard(self.module.id, question, answer)
                messagebox.showinfo("Erfolg", "Alle Karteikarten wurden erfolgreich gespeichert.")
                editor_view.destroy()
                self.main_window.refresh_module_view(self.module)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern der Karteikarten: {e}")

        save_button = tk.Button(
            button_frame,
            text="Alle Speichern",
            command=save_all,
            width=15,
            bg="#4CAF50",
            fg="black"
        )
        save_button.pack(side=tk.LEFT, padx=10, pady=10)

        cancel_button = tk.Button(
            button_frame,
            text="Abbrechen",
            command=editor_view.destroy,
            width=15,
            bg="#f44336",
            fg="black"
        )
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)
