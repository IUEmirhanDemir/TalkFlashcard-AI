
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
    def __init__(self):
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

        for F in (MainView, ModuleView):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainView")

        self.create_api_key_button()

    def refresh_module_view(self, module):
        frame = self.frames["ModuleView"]
        frame.set_module(module)
        frame.display_flashcards()

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

    def open_module_view(self, module):
        module_view = self.frames["ModuleView"]
        module_view.set_module(module)
        module_view.display_flashcards()
        self.show_frame("ModuleView")




    def on_closing(self):
        self.db_service.close_connection()
        self.destroy()

    def create_api_key_button(self):
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

    def get_api_key_status(self):
        if self.chatgpt_service and self.chatgpt_service.api_key:
            return "ChatGPT API Key gesetzt."
        else:
            return "ChatGPT API Key nicht gesetzt."

    def open_api_key_popup(self):
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
