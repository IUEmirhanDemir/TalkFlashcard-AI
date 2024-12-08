
import tkinter as tk
from tkinter import ttk, messagebox

from controller.add_module_controller import AddModuleController
from utils.mousewheel_scroll_util import bind_mousewheel
from utils.right_click_util import bind_right_click
from controller import add_module_controller
class MainView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.add_module_controller = add_module_controller
        self.controller = controller
        self.db_service = self.controller.db_service
        self.create_widgets()

    def create_widgets(self):
        module_label = tk.Label(self, text="Module:", font=("Arial", 16, "bold"))
        module_label.pack(pady=10, anchor="center")

        self.add_module_controller = AddModuleController(self.controller, self)
        add_module_button = ttk.Button(self, text="Modul hinzufügen", command=self.add_module_controller.on_click, width=30)
        add_module_button.pack(pady=10, anchor="center", fill=tk.X)

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

        self.modules_frame = tk.Frame(scrollable_frame)
        self.modules_frame.pack(pady=20)

        self.display_modules()

    def display_modules(self):
        for widget in self.modules_frame.winfo_children():
            widget.destroy()

        modules = self.db_service.get_all_modules()
        if modules:
            for module in modules:
                module_button = ttk.Button(
                    self.modules_frame,
                    text=(module.name if len(module.name) <= 20 else module.name[:17] + '...'),
                    command=lambda m=module: self.controller.open_module_view(m)
                )
                module_button.pack(anchor="center", pady=5, ipadx=10, ipady=5, fill=tk.X)

                self.create_context_menu(module_button, module)
        else:
            empty_label = tk.Label(self.modules_frame, text="Keine Module vorhanden", font=("Arial", 12, "italic"))
            empty_label.pack(anchor="center")

    def create_context_menu(self, module_button, module):
        context_menu = tk.Menu(self.modules_frame, tearoff=0)

        def delete_module():
            self.delete_module(module)

        def delete_flashcards():
            self.delete_flashcards(module)

        context_menu.add_command(label="Modul löschen", command=delete_module)
        context_menu.add_command(label="Karteikarten löschen", command=delete_flashcards)

        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)
            return "break"

        bind_right_click(module_button, show_context_menu)

    def delete_module(self, module):
        confirm = messagebox.askyesno("Modul löschen", f"Möchten Sie das Modul '{module.name}' und alle zugehörigen Karteikarten wirklich löschen?")
        if confirm:
            try:
                self.db_service.delete_module_with_flashcards(module.id)
                messagebox.showinfo("Erfolg", f"Das Modul '{module.name}' wurde erfolgreich gelöscht.")
                self.display_modules()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen des Moduls: {e}")

    def delete_flashcards(self, module):
        confirm = messagebox.askyesno("Karteikarten löschen", f"Möchten Sie alle Karteikarten im Modul '{module.name}' wirklich löschen?")
        if confirm:
            try:
                self.db_service.delete_flashcards_by_module(module.id)
                messagebox.showinfo("Erfolg", f"Alle Karteikarten im Modul '{module.name}' wurden gelöscht.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen der Karteikarten: {e}")
