def bind_mousewheel(widget, canvas):
    """
    Binds the mouse wheel event to the canvas for vertical scrolling.
    Handles platform-specific differences in mouse wheel events.

    Args:
        widget (tk.Widget): The widget to which the mouse wheel event is bound.
        canvas (tk.Canvas): The canvas to scroll when the mouse wheel is used.
    """
    import platform  # Import platform module to detect the operating system

    def _on_mousewheel(event):
        """
        Handles the mouse wheel event and adjusts the canvas view.

        Args:
            event (tk.Event): The mouse wheel event.
        """
        if platform.system() == 'Windows':  # For Windows systems
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == 'Darwin':  # For macOS systems
            canvas.yview_scroll(int(-1 * (event.delta)), "units")
        else:  # For Linux systems
            if event.num == 4:  # Scroll up
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                canvas.yview_scroll(1, "units")

    # Bind the mouse wheel event based on the operating system
    if platform.system() in ('Windows', 'Darwin'):
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Use "<MouseWheel>" event for Windows and macOS
    else:
        canvas.bind("<Button-4>", _on_mousewheel)  # Use "<Button-4>" for scrolling up on Linux
        canvas.bind("<Button-5>", _on_mousewheel)  # Use "<Button-5>" for scrolling down on Linux
