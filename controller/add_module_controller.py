
import tkinter as tk
from tkinter import messagebox
from services.database_service import DatabaseService

class AddModuleController:
    def __init__(self, main_window, parent_view):
        self.main_window = main_window
        self.parent_view = parent_view
        self.db_service = self.main_window.db_service

    def on_click(self):
        self.open_add_module_popup()

    def open_add_module_popup(self):
        popup = tk.Toplevel(self.main_window)
        popup.title("Neues Modul hinzufügen")
        popup.geometry("400x150")
        popup.transient(self.main_window)
        popup.grab_set()

        window_width = popup.winfo_reqwidth()
        window_height = popup.winfo_reqheight()
        position_right = int(self.main_window.winfo_x() + (self.main_window.winfo_width() / 2 - window_width / 2))
        position_down = int(self.main_window.winfo_y() + (self.main_window.winfo_height() / 2 - window_height / 2))
        popup.geometry("+{}+{}".format(position_right, position_down))

        label = tk.Label(popup, text="Modulname:", font=("Arial", 12))
        label.pack(pady=10)
        module_name_entry = tk.Entry(popup, width=30, font=("Arial", 12))
        module_name_entry.pack(pady=5)

        def save_module():
            module_name = module_name_entry.get().strip()
            if module_name:
                try:
                    self.db_service.add_module(module_name)
                    self.parent_view.display_modules()
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Hinzufügen des Moduls: {e}")
            else:
                messagebox.showwarning("Warnung", "Bitte einen Modulnamen eingeben.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        save_button = tk.Button(button_frame, text="Hinzufügen und Speichern", command=save_module, width=15, bg="#4CAF50", fg="black")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Abbrechen", command=popup.destroy, width=15, bg="#f44336", fg="black")
        cancel_button.pack(side=tk.RIGHT, padx=10)
