
import tkinter as tk
from tkinter import messagebox, scrolledtext


class ModuleController:
    def __init__(self, main_window, module_view, module=None):
        self.main_window = main_window
        self.module_view = module_view
        self.module = module
        self.db_service = self.main_window.db_service


    def set_module(self, module):
        self.module = module

    def add_flashcard_manually(self):

        popup = tk.Toplevel(self.main_window)
        popup.title("Karteikarten hinzufügen")
        popup.geometry("600x500")
        popup.transient(self.main_window)
        popup.grab_set()


        window_width = popup.winfo_reqwidth()
        window_height = popup.winfo_reqheight()
        position_right = int(self.main_window.winfo_x() + (self.main_window.winfo_width() / 2 - window_width / 2))
        position_down = int(self.main_window.winfo_y() + (self.main_window.winfo_height() / 2 - window_height / 2))
        popup.geometry("+{}+{}".format(position_right, position_down))



        question_label = tk.Label(popup, text="Frage:", font=("Arial", 12))
        question_label.pack(pady=5)
        question_text = tk.Text(popup, width=60, height=5, font=("Arial", 12))
        question_text.pack(pady=5)

        answer_label = tk.Label(popup, text="Antwort:", font=("Arial", 12))
        answer_label.pack(pady=5)
        answer_text = tk.Text(popup, width=60, height=10, font=("Arial", 12))
        answer_text.pack(pady=5)

        def save_flashcard():
            question = question_text.get("1.0", tk.END).strip()
            answer = answer_text.get("1.0", tk.END).strip()
            if question and answer:
                try:
                    self.db_service.add_flashcard(self.module.id, question, answer)
                    self.module_view.display_flashcards()
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Hinzufügen der Karteikarte: {e}")
            else:
                messagebox.showwarning("Warnung", "Bitte sowohl Frage als auch Antwort ausfüllen.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=20)

        save_button = tk.Button(button_frame, text="Speichern", command=save_flashcard, width=15, bg="#4CAF50", fg="black")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Abbrechen", command=popup.destroy, width=15, bg="#f44336", fg="black")
        cancel_button.pack(side=tk.RIGHT, padx=10)


    def edit_flashcard(self, flashcard):

        popup = tk.Toplevel(self.main_window)
        popup.title("Karteikarte bearbeiten")
        popup.geometry("600x500")
        popup.transient(self.main_window)
        popup.grab_set()


        window_width = popup.winfo_reqwidth()
        window_height = popup.winfo_reqheight()
        position_right = int(self.main_window.winfo_x() + (self.main_window.winfo_width() / 2 - window_width / 2))
        position_down = int(self.main_window.winfo_y() + (self.main_window.winfo_height() / 2 - window_height / 2))
        popup.geometry("+{}+{}".format(position_right, position_down))



        question_label = tk.Label(popup, text="Frage:", font=("Arial", 12))
        question_label.pack(pady=5)
        question_text = tk.Text(popup, width=60, height=5, font=("Arial", 12))
        question_text.pack(pady=5)
        question_text.insert(tk.END, flashcard.question)

        answer_label = tk.Label(popup, text="Antwort:", font=("Arial", 12))
        answer_label.pack(pady=5)
        answer_text = tk.Text(popup, width=60, height=10, font=("Arial", 12))
        answer_text.pack(pady=5)
        answer_text.insert(tk.END, flashcard.answer)

        def save_edit():
            new_question = question_text.get("1.0", tk.END).strip()
            new_answer = answer_text.get("1.0", tk.END).strip()
            if new_question and new_answer:
                try:
                    self.db_service.update_flashcard(flashcard.id, new_question, new_answer)
                    self.module_view.display_flashcards()
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Aktualisieren der Karteikarte: {e}")
            else:
                messagebox.showwarning("Warnung", "Bitte sowohl Frage als auch Antwort ausfüllen.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=20)

        save_button = tk.Button(button_frame, text="Speichern", command=save_edit, width=15, bg="#4CAF50", fg="black")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Abbrechen", command=popup.destroy, width=15, bg="#f44336", fg="black")
        cancel_button.pack(side=tk.RIGHT, padx=10)
