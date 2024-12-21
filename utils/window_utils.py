def center_window(parent, child):
    """
    Centers a child window relative to its parent window or the screen.

    Args:
        parent (tk.Widget): The parent window to center the child window relative to.
        child (tk.Widget): The child window to be centered.
    """
    # Update the geometry information for both parent and child windows
    parent.update_idletasks()
    child.update_idletasks()

    # Get dimensions of the child window
    child_width = child.winfo_width()
    child_height = child.winfo_height()

    # Handle edge case where parent dimensions are not properly initialized
    if parent.winfo_width() == 1 and parent.winfo_height() == 1:
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()  # Get screen width
        screen_height = root.winfo_screenheight()  # Get screen height
        root.destroy()  # Destroy temporary root window
    else:
        screen_width = parent.winfo_screenwidth()  # Get parent screen width
        screen_height = parent.winfo_screenheight()  # Get parent screen height

    # Calculate new x and y coordinates to center the child window
    new_x = (screen_width // 2) - (child_width // 2)
    new_y = (screen_height // 2) - (child_height // 2)

    # Apply new geometry to center the window
    child.geometry(f"+{new_x}+{new_y}")
