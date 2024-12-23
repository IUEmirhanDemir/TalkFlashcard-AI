import tkinter as tk
from tkinter import messagebox, scrolledtext

class ModuleController:
    """
    Controller for managing the module view and handling flashcard interactions.
    Provides functionality for adding and editing flashcards.
    """

    def __init__(self, main_window, module_view, module=None):
        """
        Initializes the controller with the main window, module view, and optionally a module.

        Args:
            main_window (tk.Tk): The main application window.
            module_view (object): The view that displays flashcards for the module.
            module (object, optional): The module for which flashcards are managed. Defaults to None.
        """
        self.main_window = main_window
        self.module_view = module_view
        self.module = module  # The current module being managed
        self.db_service = self.main_window.db_service  # Database service to interact with the database

    def set_module(self, module):
        """
        Sets the module for the controller.

        Args:
            module (object): The module to be set.
        """
        self.module = module

    def add_flashcard_manually(self):
        """
        Opens a popup for adding a new flashcard manually to the module.
        The user can enter a question and an answer for the new flashcard.
        """
        popup = tk.Toplevel(self.main_window)
        popup.title("Karteikarten hinzufügen")  # Popup title
        popup.geometry("600x500")  # Set size of the popup window
        popup.transient(self.main_window)  # Make popup transient
        popup.grab_set()  # Grab the input for this window

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
            """
            Saves the new flashcard with the entered question and answer to the database.
            """
            question = question_text.get("1.0", tk.END).strip()
            answer = answer_text.get("1.0", tk.END).strip()
            if question and answer:
                try:
                    self.db_service.add_flashcard(self.module.id, question, answer)  # Add flashcard to DB
                    self.module_view.display_flashcards()  # Update flashcard view
                    popup.destroy()  # Close the popup
                except Exception as e:
                    messagebox.showerror("Error", f"Error adding flashcard: {e}")
            else:
                messagebox.showwarning("Warning", "Please fill in both question and answer.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=20)

        save_button = tk.Button(button_frame, text="Speichern", command=save_flashcard, width=15, bg="#4CAF50", fg="black")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Abbrechen", command=popup.destroy, width=15, bg="#f44336", fg="black")
        cancel_button.pack(side=tk.RIGHT, padx=10)

    def edit_flashcard(self, flashcard):
        """
        Opens a popup for editing an existing flashcard.
        The user can modify the question and answer of the selected flashcard.

        Args:
            flashcard (object): The flashcard to be edited.
        """
        popup = tk.Toplevel(self.main_window)
        popup.title("Edit Flashcard")  # Popup title
        popup.geometry("600x500")  # Set the size of the popup window
        popup.transient(self.main_window)  # Make popup transient
        popup.grab_set()  # Grab the input for this window

        window_width = popup.winfo_reqwidth()
        window_height = popup.winfo_reqheight()
        position_right = int(self.main_window.winfo_x() + (self.main_window.winfo_width() / 2 - window_width / 2))
        position_down = int(self.main_window.winfo_y() + (self.main_window.winfo_height() / 2 - window_height / 2))
        popup.geometry("+{}+{}".format(position_right, position_down))

        question_label = tk.Label(popup, text="Question:", font=("Arial", 12))
        question_label.pack(pady=5)
        question_text = tk.Text(popup, width=60, height=5, font=("Arial", 12))
        question_text.pack(pady=5)
        question_text.insert(tk.END, flashcard.question)  # Pre-fill the question

        answer_label = tk.Label(popup, text="Answer:", font=("Arial", 12))
        answer_label.pack(pady=5)
        answer_text = tk.Text(popup, width=60, height=10, font=("Arial", 12))
        answer_text.pack(pady=5)
        answer_text.insert(tk.END, flashcard.answer)  # Pre-fill the answer

        def save_edit():
            """
            Saves the edited flashcard with the new question and answer to the database.
            """
            new_question = question_text.get("1.0", tk.END).strip()
            new_answer = answer_text.get("1.0", tk.END).strip()
            if new_question and new_answer:
                try:
                    self.db_service.update_flashcard(flashcard.id, new_question, new_answer)  # Update flashcard in DB
                    self.module_view.display_flashcards()  # Update flashcard view
                    popup.destroy()  # Close the popup
                except Exception as e:
                    messagebox.showerror("Error", f"Error updating flashcard: {e}")
            else:
                messagebox.showwarning("Warning", "Please fill in both question and answer.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=20)

        save_button = tk.Button(button_frame, text="Speichern", command=save_edit, width=15, bg="#4CAF50", fg="black")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Abbrechen", command=popup.destroy, width=15, bg="#f44336", fg="black")
        cancel_button.pack(side=tk.RIGHT, padx=10)
