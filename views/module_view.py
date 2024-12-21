import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

from controller.interactive_mode_controller import InteractiveModeController
from controller.module_controller import ModuleController
from controller.generate_flashcards_controller import GenerateFlashcardsController
from utils.check_flashcard_existence import check_flashcard_existence
from utils.mousewheel_scroll_util import bind_mousewheel
from utils.right_click_util import bind_right_click
from controller.normal_mode_controller import NormalModeController
from views.interactive_mode_view import InteractiveModeView
from views.normal_mode_view import NormalModeView


class ModuleView(tk.Frame):
    """
    This class represents the view for a specific module, displaying its flashcards
    and options for interacting with the module in various modes.
    """

    def __init__(self, parent, controller):
        """
        Initializes the view for the module, setting up necessary widgets.

        Args:
            parent (tk.Widget): The parent widget (window).
            controller (object): The main controller of the application.
        """
        super().__init__(parent)
        self.controller = controller
        self.db_service = self.controller.db_service
        self.module = None
        self.flashcards_options_visible = False
        self.module_controller = ModuleController(controller, self, self.module)
        self.max_frage_length = 50
        self.max_antwort_length = 100
        self.create_widgets()

    def truncate_text(self, text, max_length):
        """
        Truncates the given text to the specified length, ensuring no line breaks.

        Args:
            text (str): The text to be truncated.
            max_length (int): The maximum length of the text.

        Returns:
            str: The truncated text.
        """
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())
        if len(text) > max_length:
            return text[:max_length].rstrip() + "..."
        return text

    def create_widgets(self):
        """
        Creates and arranges all the widgets for displaying the module and its flashcards.
        """
        label_frame = tk.Frame(self)
        label_frame.pack(pady=10, anchor="n")

        self.module_text_label = tk.Label(
            label_frame,
            text="Module: ",
            font=("Arial", 16, "bold")
        )
        self.module_text_label.pack(side="left")

        self.module_name_label = tk.Label(
            label_frame,
            text="",
            font=("Arial", 16, "bold"),
            fg="#002cb0"
        )
        self.module_name_label.pack(side="left")

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20, anchor="center")

        back_button = ttk.Button(
            button_frame,
            text="Zurück",
            command=lambda: self.controller.show_frame("MainView")
        )
        back_button.pack(side="left", padx=5)

        self.add_flashcards_button = ttk.Button(
            button_frame,
            text="Karteikarten hinzufügen zum Modul",
            command=self.toggle_flashcards_options
        )
        self.add_flashcards_button.pack(side="left", padx=5)

        interactive_mode_button = ttk.Button(
            button_frame,
            text="Interaktiver Lernmodus",
            command=self.start_interactive_mode
        )
        interactive_mode_button.pack(side="left", padx=5)

        normal_mode_button = ttk.Button(
            button_frame,
            text="Normaler Lernmodus",
            command=self.start_normal_mode
        )
        normal_mode_button.pack(side="left", padx=5)

        self.flashcards_options_frame = tk.Frame(self)

        self.create_flashcards_options()

        self.flashcards_display_frame = tk.Frame(self)
        self.flashcards_display_frame.pack(pady=10, fill='both', expand=True)

        self.flashcards_label = tk.Label(
            self.flashcards_display_frame,
            text="Karteikarten:",
            font=("Arial", 14, "bold")
        )
        self.flashcards_label.pack(anchor="w", padx=10)

        self.flashcards_tree = ttk.Treeview(
            self.flashcards_display_frame,
            columns=("Frage", "Antwort"),
            show="headings",
            selectmode="extended"
        )

        self.flashcards_tree.heading("Frage", text="Frage")
        self.flashcards_tree.heading("Antwort", text="Antwort")
        self.flashcards_tree.column("Frage", width=300, anchor="w")
        self.flashcards_tree.column("Antwort", width=500, anchor="w")
        self.flashcards_tree.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(
            self.flashcards_display_frame,
            orient="vertical",
            command=self.flashcards_tree.yview
        )
        self.flashcards_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        bind_mousewheel(self.flashcards_tree, self.flashcards_tree)

        self.flashcards_tree.bind("<Double-1>", self.on_double_click)

        bind_right_click(self.flashcards_tree, self.on_right_click)

    def set_module(self, module):
        """
        Sets the module for this view and updates the display.

        Args:
            module (object): The module to be set.
        """
        self.module = module
        self.module_controller.set_module(module)
        self.update_module_label()
        self.display_flashcards()

    def update_module_label(self):
        """
        Updates the label showing the current module name.
        """
        if self.module:
            self.module_name_label.config(text=f"{self.module.name}")
        else:
            self.module_name_label.config(text="")

    def toggle_flashcards_options(self):
        """
        Toggles the visibility of the flashcards options frame.
        """
        if not self.flashcards_options_visible:
            self.flashcards_options_frame.pack(
                padx=15, pady=10, fill='both', expand=True)
            self.flashcards_options_visible = True
        else:
            self.flashcards_options_frame.pack_forget()
            self.flashcards_options_visible = False

    def create_flashcards_options(self):
        """
        Creates options for adding or generating flashcards.
        """
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        add_flashcards_logo_path = os.path.join(
            assets_path, 'add_flashcards.png')
        generate_flashcards_logo_path = os.path.join(
            assets_path, 'generate_flashcards.png')

        try:
            add_flashcards_image = Image.open(add_flashcards_logo_path)
            generate_flashcards_image = Image.open(
                generate_flashcards_logo_path)
        except FileNotFoundError:
            messagebox.showerror("Fehler", "Logo-Bilder nicht gefunden.")
            return

        logo_size = (75, 75)
        add_flashcards_image = add_flashcards_image.resize(
            logo_size, Image.LANCZOS)
        generate_flashcards_image = generate_flashcards_image.resize(
            logo_size, Image.LANCZOS)

        self.add_flashcards_photo = ImageTk.PhotoImage(add_flashcards_image)
        self.generate_flashcards_photo = ImageTk.PhotoImage(
            generate_flashcards_image)

        options_button_frame = tk.Frame(self.flashcards_options_frame)
        options_button_frame.pack(fill='both', expand=True,
                                  padx=20, pady=20)

        add_flashcards_button = tk.Button(
            options_button_frame,
            text="Karteikarten selber hinzufügen",
            image=self.add_flashcards_photo,
            compound="top",
            command=self.module_controller.add_flashcard_manually,
            bg="#f0f0f0",
            relief="solid"
        )
        add_flashcards_button.pack(
            side="left", expand=True, fill='both', padx=10, pady=10)

        generate_flashcards_chatgpt_button = tk.Button(
            options_button_frame,
            text="Karteikarten generieren mit ChatGPT",
            image=self.generate_flashcards_photo,
            compound="top",
            command=self.open_generate_flashcards,
            bg="#f0f0f0",
            relief="solid"
        )
        generate_flashcards_chatgpt_button.pack(
            side="right", expand=True, fill='both', padx=10, pady=10)

    def open_generate_flashcards(self):
        """
        Opens the popup for generating flashcards using ChatGPT.
        """
        print("open_generate_flashcards aufgerufen")
        if self.module and self.controller.chatgpt_service:
            print("Module und ChatGPTService vorhanden")
            generate_controller = GenerateFlashcardsController(
                main_window=self.controller,
                module=self.module,
                chatgpt_service=self.controller.chatgpt_service
            )
            generate_controller.open_generate_flashcards_popup()
        else:
            messagebox.showwarning(
                "Warnung",
                "Bitte wählen Sie ein Modul aus und stellen Sie sicher, dass der API Key gesetzt ist."
            )

    def display_flashcards(self):
        """
        Displays all flashcards for the current module in the treeview.
        """
        for item in self.flashcards_tree.get_children():
            self.flashcards_tree.delete(item)

        if not self.module:
            print("Module ist nicht gesetzt!")
            return

        flashcards = self.db_service.get_flashcards_by_module(self.module.id)

        if flashcards:
            for fc in flashcards:
                truncated_frage = self.truncate_text(fc.question, self.max_frage_length)
                truncated_antwort = self.truncate_text(fc.answer, self.max_antwort_length)
                self.flashcards_tree.insert(
                    "", tk.END, iid=fc.id, values=(truncated_frage, truncated_antwort))
        else:
            self.flashcards_tree.insert(
                "", tk.END, iid="no_flashcards", values=("Keine Karteikarten vorhanden.", ""))

    def on_right_click(self, event):
        """
        Displays the right-click context menu for deleting selected flashcards.
        """
        selected_items = self.flashcards_tree.selection()
        if selected_items:
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(
                label="Ausgewählte Karteikarten löschen", command=self.delete_selected_flashcards)
            context_menu.tk_popup(event.x_root, event.y_root)
        else:
            pass

    def delete_selected_flashcards(self):
        """
        Deletes selected flashcards after confirmation.
        """
        selected_items = self.flashcards_tree.selection()
        if selected_items:
            confirm = messagebox.askyesno(
                "Karteikarten löschen",
                f"Möchten Sie die ausgewählten Karteikarten wirklich löschen?"
            )
            if confirm:
                for item_id in selected_items:
                    try:
                        flashcard_id = int(item_id)
                        self.db_service.delete_flashcard(flashcard_id)
                        self.flashcards_tree.delete(item_id)
                    except Exception as e:
                        messagebox.showerror(
                            "Fehler", f"Fehler beim Löschen der Karteikarte: {e}")
                messagebox.showinfo(
                    "Erfolg", "Die ausgewählten Karteikarten wurden gelöscht.")
        else:
            messagebox.showwarning(
                "Warnung", "Keine Karteikarten ausgewählt.")

    def on_double_click(self, event):
        """
        Edits the selected flashcard on a double-click event.
        """
        selected_item = self.flashcards_tree.selection()
        if selected_item:
            selected_item_id = selected_item[0]

            if selected_item_id == "no_flashcards":
                return

            try:
                flashcard_id = int(selected_item_id)
                flashcard = next(
                    (fc for fc in self.db_service.get_flashcards_by_module(
                        self.module.id) if fc.id == flashcard_id),
                    None
                )
                if flashcard:
                    self.module_controller.edit_flashcard(flashcard)
            except ValueError:
                return

    def start_interactive_mode(self):
        """
        Starts the interactive learning mode if flashcards are available.
        """
        if self.module:
            if not check_flashcard_existence(self.db_service, self.module.id):
                messagebox.showinfo(
                    "Keine Karteikarten", "Keine Karteikarten zum Lernen vorhanden.")
                return

            interactive_mode_controller = InteractiveModeController(
                self.controller, self.module)
            interactive_mode_view = InteractiveModeView(
                self.controller, self.module, interactive_mode_controller)
        else:
            messagebox.showwarning("Warnung", "Kein Modul ausgewählt.")

    def start_normal_mode(self):
        """
        Starts the normal learning mode if flashcards are available.
        """
        if self.module:
            if not check_flashcard_existence(self.db_service, self.module.id):
                messagebox.showinfo(
                    "Keine Karteikarten", "Keine Karteikarten zum Lernen vorhanden.")
                return

            normal_mode_controller = NormalModeController(
                self.controller, self.module)
            if normal_mode_controller.load_flashcards():
                normal_mode_view = NormalModeView(
                    self.controller, normal_mode_controller)
                normal_mode_controller.start_round()
        else:
            messagebox.showwarning("Warnung", "Kein Modul ausgewählt.")
