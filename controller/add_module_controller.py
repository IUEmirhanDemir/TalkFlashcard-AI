import tkinter as tk
from tkinter import messagebox
from services.database_service import DatabaseService

class AddModuleController:
    """
    Controller for adding new modules to the application.
    Manages the module addition popup and interaction with the database.
    """

    def __init__(self, main_window, parent_view):
        """
        Initializes the controller with the main window and parent view.

        Args:
            main_window (tk.Tk): The main application window.
            parent_view (tk.Frame): The parent view that will display modules.
        """
        self.main_window = main_window
        self.parent_view = parent_view
        self.db_service = self.main_window.db_service  # Database service for interaction with DB

    def on_click(self):
        """
        Opens the popup window to add a new module when clicked.
        """
        self.open_add_module_popup()

    def open_add_module_popup(self):
        """
        Opens the popup window where the user can input the module name.
        Also handles the positioning and UI elements.
        """
        popup = tk.Toplevel(self.main_window)
        popup.title("Neues Modul hinzufügen")  # Title of the popup window
        popup.geometry("400x150")  # Window size
        popup.transient(self.main_window)  # Make popup transient
        popup.grab_set()  # Grab input for this window

        window_width = popup.winfo_reqwidth()
        window_height = popup.winfo_reqheight()
        position_right = int(self.main_window.winfo_x() + (self.main_window.winfo_width() / 2 - window_width / 2))
        position_down = int(self.main_window.winfo_y() + (self.main_window.winfo_height() / 2 - window_height / 2))
        popup.geometry("+{}+{}".format(position_right, position_down))

        # Label and Entry widget for module name
        label = tk.Label(popup, text="Module Name:", font=("Arial", 12))
        label.pack(pady=10)
        module_name_entry = tk.Entry(popup, width=30, font=("Arial", 12))
        module_name_entry.pack(pady=5)

        def save_module():
            """
            Saves the module name to the database and updates the parent view.
            """
            module_name = module_name_entry.get().strip()
            if module_name:
                try:
                    self.db_service.add_module(module_name)  # Add module to DB
                    self.parent_view.display_modules()  # Update module view
                    popup.destroy()  # Close the popup
                except Exception as e:
                    messagebox.showerror("Error", f"Error adding module: {e}")
            else:
                messagebox.showwarning("Warning", "Please enter a module name.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        save_button = tk.Button(button_frame, text="Speichern", command=save_module, width=15, bg="#4CAF50", fg="black")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Abbrechen", command=popup.destroy, width=15, bg="#f44336", fg="black")
        cancel_button.pack(side=tk.RIGHT, padx=10)
