import tkinter as tk
from tkinter import messagebox
import random

from views import normal_mode_view

class NormalModeController:
    """
    Controller for managing the normal mode of flashcard learning.
    Handles loading flashcards, starting rounds, showing questions, and tracking results.
    """

    def __init__(self, main_window, module):
        """
        Initializes the controller with the main window and module.

        Args:
            main_window (tk.Tk): The main application window.
            module (object): The module for which flashcards will be displayed and tested.
        """
        self.main_window = main_window
        self.module = module
        self.db_service = self.main_window.db_service  # Database service for fetching flashcards
        self.normal_mode_view = normal_mode_view  # The view for displaying questions and results

        self.flashcards = []
        self.current_flashcard = None  # Store the current flashcard
        self.round = 1  # Start at round 1
        self.correct_answers = []  # Store correct answers for each round
        self.incorrect_answers = []  # Store incorrect answers for each round
        self.results_per_round = []  # Store round results
        self.all_flashcards = []  # List of all available flashcards
        self.load_flashcards()  # Load flashcards from the database

    def load_flashcards(self):
        """
        Loads flashcards from the database for the current module.

        Returns:
            bool: True if flashcards are loaded successfully, False if no flashcards are found.
        """
        self.all_flashcards = self.db_service.get_flashcards_by_module(self.module.id)
        if not self.all_flashcards:
            messagebox.showwarning("Warning", "No flashcards available in the module.")  # Show warning if no flashcards
            return False
        return True

    def start_round(self):
        """
        Starts a new round by resetting the necessary variables and shuffling flashcards.
        """
        self.current_index = 0  # Reset the current index to 0
        self.correct_answers = []  # Reset correct answers
        self.incorrect_answers = []  # Reset incorrect answers
        self.flashcards = self.all_flashcards.copy()  # Copy flashcards for this round
        random.shuffle(self.flashcards)  # Shuffle the flashcards randomly
        self.show_question()  # Show the first question

    def end_round(self):
        """
        Ends the current round, calculates the success rate, and displays the results.
        """
        total = len(self.correct_answers) + len(self.incorrect_answers)
        correct = len(self.correct_answers)
        incorrect = len(self.incorrect_answers)
        success_rate = (correct / total) * 100 if total > 0 else 0  # Calculate success rate
        self.results_per_round.append({
            'round': self.round,
            'correct': correct,
            'incorrect': incorrect,
            'success_rate': success_rate
        })

        self.normal_mode_view.show_round_summary(self.correct_answers, self.incorrect_answers, success_rate)  # Show round summary
        self.round += 1  # Increment the round number

    def show_question(self):
        """
        Displays the current flashcard question.
        If there are no more flashcards, ends the round.
        """
        if self.current_index < len(self.flashcards):
            self.current_flashcard = self.flashcards[self.current_index]  # Get the next flashcard
            self.normal_mode_view.display_question(self.current_flashcard.question)  # Display the question
            self.normal_mode_view.update_idletasks()  # Update the view
        else:
            self.end_round()  # End round if no more flashcards

    def show_answer(self):
        """
        Displays the answer of the current flashcard.
        """
        if self.current_flashcard:
            self.normal_mode_view.display_answer(self.current_flashcard.answer)  # Display the answer

    def user_answered(self, correct):
        """
        Handles the user's answer. Updates the correct or incorrect answers list and shows the next question.

        Args:
            correct (bool): Whether the user's answer was correct or not.
        """
        if correct:
            self.correct_answers.append(self.current_flashcard)  # Add to correct answers if answered correctly
        else:
            self.incorrect_answers.append(self.current_flashcard)  # Add to incorrect answers if answered wrongly
        self.current_index += 1  # Move to the next flashcard
        self.show_question()  # Show the next question

    def repeat_round(self):
        """
        Repeats the current round by restarting it.
        """
        self.start_round()  # Restart the round

    def finish_learning(self):
        """
        Ends the learning session and shows the final results.
        """
        self.normal_mode_view.show_final_results(self.results_per_round)  # Show the final results of the learning session
