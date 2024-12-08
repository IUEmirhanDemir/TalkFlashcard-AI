def bind_mousewheel(widget, canvas):
    import platform

    def _on_mousewheel(event):
        if platform.system() == 'Windows':
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == 'Darwin':  # macOS
            canvas.yview_scroll(int(-1 * (event.delta)), "units")
        else:  # Linux
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    if platform.system() in ('Windows', 'Darwin'):
        canvas.bind("<MouseWheel>", _on_mousewheel)
    else:
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)
