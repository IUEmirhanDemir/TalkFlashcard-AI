
def center_window(parent, child):
    parent.update_idletasks()
    child.update_idletasks()

    child_width = child.winfo_width()
    child_height = child.winfo_height()

    if parent.winfo_width() == 1 and parent.winfo_height() == 1:
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
    else:
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()

    new_x = (screen_width // 2) - (child_width // 2)
    new_y = (screen_height // 2) - (child_height // 2)

    child.geometry(f"+{new_x}+{new_y}")
