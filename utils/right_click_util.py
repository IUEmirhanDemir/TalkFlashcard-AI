import platform

def bind_right_click(widget, callback):
    """
    Binds the right-click event to a widget, handling platform-specific differences.

    Args:
        widget (tk.Widget): The widget to bind the right-click event to.
        callback (function): The function to call when the right-click event happens.
    """
    system = platform.system()
    if system == 'Darwin':  # macOS
        # On macOS, bind both Button-2 and Control-Button-1 to handle right-clicks
        widget.bind('<Button-2>', callback)
        widget.bind('<Control-Button-1>', callback)
    else:
        # On Windows and Linux, right-click is usually Button-3
        widget.bind('<Button-3>', callback)  # Windows und Linux
