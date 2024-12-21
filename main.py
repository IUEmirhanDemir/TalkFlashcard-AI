import tkinter as tk
from tkinter import messagebox

from services.config_service import ConfigService
from services.chatgpt_service import ChatGPTService
from services.database_service import DatabaseService
from views.main_view import MainView
from views.module_view import ModuleView

import ssl

from utils.window_utils import center_window

class MainWindow(tk.Tk):
    """
    The main window of the application, responsible for managing the GUI and the communication
    between different views, such as the main view and the module view.
    """

    def __init__(self):
        """
        Initializes the main window, setting up services, frames, and UI elements.

        Sets up SSL context, API key handling, and initializes the database connection.
        """
        super().__init__()
        self.title("Karteikarten App")
        self.geometry("800x800")
        self.eval('tk::PlaceWindow . center')
        ssl._create_default_https_context = ssl._create_unverified_context

        self.config_service = ConfigService()

        try:
            self.chatgpt_service = ChatGPTService(config_service=self.config_service)
        except ValueError as e:
            messagebox.showwarning("API-Schlüssel fehlt", str(e))
            self.chatgpt_service = None

        self.db_service = DatabaseService()

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Creating and adding views to the window
        for F in (MainView, ModuleView):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainView")

        self.create_api_key_button()

    def refresh_module_view(self, module):
        """
        Refreshes the module view with the selected module and its flashcards.

        Args:
            module (object): The module to be displayed in the module view.
        """
        frame = self.frames["ModuleView"]
        frame.set_module(module)
        frame.display_flashcards()

    def show_frame(self, frame_name):
        """
        Displays the specified frame.

        Args:
            frame_name (str): The name of the frame to be displayed.
        """
        frame = self.frames[frame_name]
        frame.tkraise()

    def open_module_view(self, module):
        """
        Opens the module view for the selected module.

        Args:
            module (object): The module to be displayed in the module view.
        """
        module_view = self.frames["ModuleView"]
        module_view.set_module(module)
        module_view.display_flashcards()
        self.show_frame("ModuleView")

    def on_closing(self):
        """
        Handles the closing of the main window, closing database connection and destroying the window.
        """
        self.db_service.close_connection()
        self.destroy()

    def create_api_key_button(self):
        """
        Creates a button in the bottom frame for managing the ChatGPT API key.
        """
        api_key_frame = tk.Frame(self, bg="#615e5e")
        api_key_frame.pack(side="bottom", anchor="w", fill="x")

        self.api_key_status_label = tk.Label(api_key_frame, text=self.get_api_key_status(), bg="#000000", fg="#ffffff")
        self.api_key_status_label.pack(side="left", padx=10, pady=5)

        api_key_button = tk.Button(
            api_key_frame,
            text="ChatGPT API Key",
            command=self.open_api_key_popup,
            bg="#4CAF50",
            fg="black"
        )
        api_key_button.pack(side="left", padx=5, pady=5)


      # Powered By OpenAI Label
        powered_by_label = tk.Label(
            api_key_frame,
            text="Powered By OpenAi API (Whisper 1, TTTS, gpt-4o-mini)",
            bg="#615e5e",
            fg="#ffffff",
            anchor="e"
        )
        powered_by_label.pack(side="right", padx=10, pady=5)

    def get_api_key_status(self):
        """
        Checks if the ChatGPT API key is set and returns a status message.

        Returns:
            str: The status of the API key.
        """
        if self.chatgpt_service and self.chatgpt_service.api_key:
            return "ChatGPT API Key gesetzt."
        else:
            return "ChatGPT API Key nicht gesetzt."

    def open_api_key_popup(self):
        """
        Opens a popup window to input the ChatGPT API key.
        """
        popup = tk.Toplevel(self)
        popup.title("ChatGPT API Key hinzufügen")
        popup.geometry("400x200")
        popup.transient(self)
        popup.grab_set()
        center_window(self, popup)

        label = tk.Label(popup, text="Geben Sie Ihren ChatGPT API Key ein:", font=("Arial", 12))
        label.pack(pady=10)

        api_key_entry = tk.Entry(popup, width=40, show="*", font=("Arial", 12))
        api_key_entry.pack(pady=5)

        def save_api_key():
            """
            Saves the entered API key and sets it for both the config and ChatGPT services.
            """
            api_key = api_key_entry.get().strip()
            if api_key:
                try:
                    self.config_service.set_api_key(api_key)

                    if self.chatgpt_service:
                        self.chatgpt_service.set_api_key(api_key)
                    else:
                        self.chatgpt_service = ChatGPTService(config_service=self.config_service)

                    self.api_key_status_label.config(text=self.get_api_key_status())
                    messagebox.showinfo("Erfolg", "ChatGPT API Key wurde erfolgreich gespeichert.")
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Speichern des API Keys: {e}")
            else:
                messagebox.showwarning("Warnung", "Bitte einen gültigen API Key eingeben.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=20)

        save_button = tk.Button(button_frame, text="Speichern", command=save_api_key, bg="#4CAF50", fg="black")
        save_button.pack(side="left", padx=10)

        cancel_button = tk.Button(button_frame, text="Abbrechen", command=popup.destroy, bg="#f44336", fg="black")
        cancel_button.pack(side="right", padx=10)

if __name__ == "__main__":
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
