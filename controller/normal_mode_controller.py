
import tkinter as tk
from tkinter import messagebox
import random

from views import normal_mode_view


class NormalModeController:
    def __init__(self, main_window, module):
        self.main_window = main_window
        self.module = module
        self.db_service = self.main_window.db_service
        self.normal_mode_view = normal_mode_view

        self.flashcards = []
        self.current_flashcard = None
        self.round = 1
        self.correct_answers = []
        self.incorrect_answers = []
        self.results_per_round = []
        self.all_flashcards = []
        self.load_flashcards()

    def load_flashcards(self):
        self.all_flashcards = self.db_service.get_flashcards_by_module(self.module.id)
        if not self.all_flashcards:
            messagebox.showwarning("Warnung", "Keine Karteikarten im Modul vorhanden.")
            return False
        return True

    def start_round(self):
        self.current_index = 0
        self.correct_answers = []
        self.incorrect_answers = []
        self.flashcards = self.all_flashcards.copy()
        random.shuffle(self.flashcards)
        self.show_question()

    def end_round(self):
        total = len(self.correct_answers) + len(self.incorrect_answers)
        correct = len(self.correct_answers)
        incorrect = len(self.incorrect_answers)
        success_rate = (correct / total) * 100 if total > 0 else 0
        self.results_per_round.append({
            'round': self.round,
            'correct': correct,
            'incorrect': incorrect,
            'success_rate': success_rate
        })

        self.normal_mode_view.show_round_summary(self.correct_answers, self.incorrect_answers, success_rate)
        self.round += 1

    def show_question(self):
        if self.current_index < len(self.flashcards):
            self.current_flashcard = self.flashcards[self.current_index]
            self.normal_mode_view.display_question(self.current_flashcard.question)
            self.normal_mode_view.update_idletasks()
        else:
            self.end_round()

    def show_answer(self):
        if self.current_flashcard:
            self.normal_mode_view.display_answer(self.current_flashcard.answer)

    def user_answered(self, correct):
        if correct:
            self.correct_answers.append(self.current_flashcard)
        else:
            self.incorrect_answers.append(self.current_flashcard)
        self.current_index += 1
        self.show_question()

    def repeat_round(self):
        self.start_round()

    def finish_learning(self):
        self.normal_mode_view.show_final_results(self.results_per_round)
