import tkinter as tk
from tkinter import ttk, messagebox
from controller.add_module_controller import AddModuleController
from utils.mousewheel_scroll_util import bind_mousewheel
from utils.right_click_util import bind_right_click
from controller import add_module_controller

class MainView(tk.Frame):
    """
    The main view of the application. Displays the available modules and allows users to manage them.
    """

    def __init__(self, parent, controller):
        """
        Initializes the main view.

        Args:
            parent (tk.Widget): The parent widget for this view.
            controller (object): The main controller of the application.
        """
        super().__init__(parent)
        self.add_module_controller = add_module_controller  # Controller for adding modules
        self.controller = controller
        self.db_service = self.controller.db_service  # Database service for fetching and modifying modules
        self.create_widgets()  # Initialize the UI components

    def create_widgets(self):
        """
        Creates and arranges all widgets in the main view.
        """
        module_label = tk.Label(self, text="Module:", font=("Arial", 16, "bold"))
        module_label.pack(pady=10, anchor="center")

        # Button to add a new module
        self.add_module_controller = AddModuleController(self.controller, self)
        add_module_button = ttk.Button(self, text="Modul hinzufügen", command=self.add_module_controller.on_click, width=30)
        add_module_button.pack(pady=10, anchor="center", fill=tk.X)

        # Scrollable canvas for displaying modules
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: [
                canvas.configure(scrollregion=canvas.bbox("all")),
                scrollable_frame.update_idletasks(),
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())
            ]
        )

        bind_mousewheel(canvas, canvas)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bind_mousewheel(canvas, canvas)

        # Frame to hold module buttons
        self.modules_frame = tk.Frame(scrollable_frame)
        self.modules_frame.pack(pady=20)

        self.display_modules()  # Populate the frame with modules

    def display_modules(self):
        """
        Displays all modules in the database as buttons. Each button corresponds to a module.
        """
        for widget in self.modules_frame.winfo_children():
            widget.destroy()  # Clear the frame before displaying modules

        modules = self.db_service.get_all_modules()  # Fetch all modules
        if modules:
            for module in modules:
                # Create a button for each module
                module_button = ttk.Button(
                    self.modules_frame,
                    text=(module.name if len(module.name) <= 20 else module.name[:17] + '...'),
                    command=lambda m=module: self.controller.open_module_view(m)
                )
                module_button.pack(anchor="center", pady=5, ipadx=10, ipady=5, fill=tk.X)

                self.create_context_menu(module_button, module)  # Add a context menu to the button
        else:
            empty_label = tk.Label(self.modules_frame, text="Keine Module vorhanden", font=("Arial", 12, "italic"))
            empty_label.pack(anchor="center")

    def create_context_menu(self, module_button, module):
        """
        Creates a right-click context menu for a module button.

        Args:
            module_button (tk.Widget): The button representing the module.
            module (object): The module associated with the button.
        """
        context_menu = tk.Menu(self.modules_frame, tearoff=0)

        def delete_module():
            self.delete_module(module)

        def delete_flashcards():
            self.delete_flashcards(module)

        context_menu.add_command(label="Modul löschen", command=delete_module)
        context_menu.add_command(label="Karteikarten löschen", command=delete_flashcards)

        def show_context_menu(event):
            """
            Displays the context menu at the mouse pointer's location.

            Args:
                event (tk.Event): The right-click event.
            """
            context_menu.tk_popup(event.x_root, event.y_root)
            return "break"

        bind_right_click(module_button, show_context_menu)

    def delete_module(self, module):
        """
        Deletes a module along with all its flashcards after confirmation.

        Args:
            module (object): The module to be deleted.
        """
        confirm = messagebox.askyesno("Modul löschen", f"Möchten Sie das Modul '{module.name}' und alle zugehörigen Karteikarten wirklich löschen?")
        if confirm:
            try:
                self.db_service.delete_module_with_flashcards(module.id)
                messagebox.showinfo("Erfolg", f"Das Modul '{module.name}' wurde erfolgreich gelöscht.")
                self.display_modules()  # Refresh the module list
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen des Moduls: {e}")

    def delete_flashcards(self, module):
        """
        Deletes all flashcards in a module after confirmation.

        Args:
            module (object): The module whose flashcards will be deleted.
        """
        confirm = messagebox.askyesno("Karteikarten löschen", f"Möchten Sie alle Karteikarten im Modul '{module.name}' wirklich löschen?")
        if confirm:
            try:
                self.db_service.delete_flashcards_by_module(module.id)
                messagebox.showinfo("Erfolg", f"Alle Karteikarten im Modul '{module.name}' wurden gelöscht.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen der Karteikarten: {e}")
