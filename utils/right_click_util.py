
import platform

def bind_right_click(widget, callback):
    system = platform.system()
    if system == 'Darwin':  # macOS
        widget.bind('<Button-2>', callback)
        widget.bind('<Control-Button-1>', callback)
    else:
        widget.bind('<Button-3>', callback)  # Windows und Linux
