
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
from utils.mousewheel_scroll_util import bind_mousewheel


class NormalModeView(tk.Toplevel):
    def __init__(self, main_window, controller):
        super().__init__(main_window)
        self.main_window = main_window
        self.controller = controller
        self.controller.normal_mode_view = self
        self.title(f"Normaler Lernmodus - Modul: {self.controller.module.name}")
        self.geometry("800x600")
        center_window(self.main_window, self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.answer_shown = False
        self.is_summary_displayed = False
        self.buttons_active = False
        self.summary_widgets = []
        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        self.question_label = tk.Label(self, text="", font=("Arial", 18, "bold"), wraplength=700)
        self.question_label.pack(pady=30)

        self.answer_label = tk.Label(self, text="", font=("Arial", 16), wraplength=700, fg="green")
        self.answer_label.pack(pady=20)

    def bind_events(self):
        self.bind('<KeyPress-space>', self.on_space_press)
        self.bind('<KeyPress-1>', lambda event: self.on_number_key_press(1))
        self.bind('<KeyPress-KP_1>', lambda event: self.on_number_key_press(1))
        self.bind('<KeyPress-2>', lambda event: self.on_number_key_press(2))
        self.bind('<KeyPress-KP_2>', lambda event: self.on_number_key_press(2))

    def on_space_press(self, event):
        if not self.answer_shown and not self.is_summary_displayed:
            self.controller.show_answer()

    def display_question(self, question):
        self.answer_shown = False
        self.is_summary_displayed = False
        self.clear_summary_widgets()
        self.question_label.config(text=f"Frage:\n\n{question}")
        self.question_label.pack(pady=30)
        self.answer_label.config(text="")
        self.answer_label.pack(pady=20)
        self.clear_buttons()

        self.show_answer_button = tk.Button(
            self,
            text="Antwort anzeigen (Leertaste)",
            command=self.controller.show_answer,
            font=("Arial", 14),
            width=20
        )
        self.show_answer_button.pack(pady=20)

    def display_answer(self, answer):
        if self.answer_shown:
            return
        self.answer_shown = True
        self.answer_label.config(text=f"Antwort:\n\n{answer}")
        if hasattr(self, 'show_answer_button'):
            self.show_answer_button.destroy()
            del self.show_answer_button
        self.buttons_active = True

        self.right_wrong_frame = tk.Frame(self)
        self.right_wrong_frame.pack(pady=20)

        self.right_button = tk.Button(
            self.right_wrong_frame,
            text="Hatte ich richtig (1)",
            command=lambda: self.controller.user_answered(True),
            font=("Arial", 14),
            bg="#4CAF50",
            fg="black",
            width=20
        )
        self.right_button.pack(side="left", padx=10)

        self.wrong_button = tk.Button(
            self.right_wrong_frame,
            text="Hatte ich falsch (2)",
            command=lambda: self.controller.user_answered(False),
            font=("Arial", 14),
            bg="#f44336",
            fg="black",
            width=20
        )
        self.wrong_button.pack(side="left", padx=10)

    def on_number_key_press(self, number):
        if self.buttons_active and not self.is_summary_displayed:
            if number == 1:
                self.controller.user_answered(True)
            elif number == 2:
                self.controller.user_answered(False)
        else:
            pass

    def clear_buttons(self):
        if hasattr(self, 'show_answer_button'):
            self.show_answer_button.destroy()
            del self.show_answer_button
        if hasattr(self, 'right_wrong_frame'):
            self.right_wrong_frame.destroy()
            del self.right_wrong_frame
        self.buttons_active = False

    def clear_summary_widgets(self):
        for widget in self.summary_widgets:
            widget.destroy()
        self.summary_widgets.clear()
        self.is_summary_displayed = False

    def show_round_summary(self, correct_answers, incorrect_answers, success_rate):
        self.question_label.pack_forget()
        self.answer_label.pack_forget()
        self.clear_buttons()
        self.is_summary_displayed = True

        summary_label = tk.Label(self, text=f"Runde {self.controller.round } beendet", font=("Arial", 20, "bold"))
        summary_label.pack(pady=20)
        self.summary_widgets.append(summary_label)

        stats_label = tk.Label(
            self,
            text=f"Richtig: {len(correct_answers)}\nFalsch: {len(incorrect_answers)}\nErfolgsquote: {success_rate:.2f}%",
            font=("Arial", 16)
        )
        stats_label.pack(pady=10)
        self.summary_widgets.append(stats_label)

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=20)
        self.summary_widgets.append(buttons_frame)

        repeat_button = tk.Button(
            buttons_frame,
            text="Erneut wiederholen",
            command=self.controller.repeat_round,
            font=("Arial", 14),
            width=20
        )
        repeat_button.pack(side="left", padx=10)

        finish_button = tk.Button(
            buttons_frame,
            text="Beenden",
            command=self.controller.finish_learning,
            font=("Arial", 14),
            width=20
        )
        finish_button.pack(side="left", padx=10)

        self.summary_widgets.extend([repeat_button, finish_button])

    def show_final_results(self, results_per_round):
        self.question_label.pack_forget()
        self.answer_label.pack_forget()
        self.clear_buttons()
        self.is_summary_displayed = True
        self.clear_summary_widgets()

        title_label = tk.Label(self, text="Lernsession beendet", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        self.summary_widgets.append(title_label)

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )


        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.summary_widgets.extend([canvas, scrollbar])
        bind_mousewheel(scrollable_frame, canvas)

        for result in results_per_round:
            frame = tk.Frame(scrollable_frame)
            frame.pack(pady=10, fill="x", padx=20)

            round_label = tk.Label(frame, text=f"Runde {result['round']}", font=("Arial", 16, "bold"))
            round_label.pack(anchor="w")

            stats_label = tk.Label(
                frame,
                text=f"Richtig: {result['correct']}\nFalsch: {result['incorrect']}\nErfolgsquote: {result['success_rate']:.2f}%",
                font=("Arial", 14)
            )
            stats_label.pack(anchor="w")

        close_button = tk.Button(
            self,
            text="Schließen",
            command=self.on_closing,
            font=("Arial", 14),
            width=20
        )
        close_button.pack(pady=20)
        self.summary_widgets.append(close_button)


    def on_closing(self):
        self.unbind('<KeyPress-space>')
        self.unbind('<KeyPress-1>')
        self.unbind('<KeyPress-KP_1>')
        self.unbind('<KeyPress-2>')
        self.unbind('<KeyPress-KP_2>')
        self.destroy()
