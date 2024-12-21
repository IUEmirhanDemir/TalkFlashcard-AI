class InteractiveModeController:
    """
    Controller for interactive flashcard mode.
    Manages the navigation and display of flashcards during study sessions.
    """

    def __init__(self, main_window, module):
        """
        Initializes the controller with the main window and module.

        Args:
            main_window (tk.Tk): The main application window.
            module (object): The module for which flashcards will be displayed.
        """
        self.main_window = main_window
        self.module = module
        self.db_service = self.main_window.db_service  # Database service to fetch flashcards
        self.all_flashcards = self.db_service.get_flashcards_by_module(module.id)  # Fetch all flashcards for the module
        self.current_index = -1  # Index of the current flashcard
        self.current_flashcard = None  # Currently displayed flashcard

    def reset_flashcards(self):
        """
        Resets the flashcard session, starting from the first flashcard.
        """
        self.current_index = -1  # Reset the index
        self.current_flashcard = None  # Reset the current flashcard

    def get_next_flashcard(self):
        """
        Returns the next flashcard in the sequence.

        Returns:
            Flashcard or None: The next flashcard if available, otherwise None.
        """
        if self.all_flashcards and self.current_index + 1 < len(self.all_flashcards):
            return self.all_flashcards[self.current_index + 1]
        return None

    def move_to_next_flashcard(self):
        """
        Moves to the next flashcard and updates the current flashcard.

        Returns:
            Flashcard or None: The next flashcard if available, otherwise None.
        """
        if self.all_flashcards and self.current_index + 1 < len(self.all_flashcards):
            self.current_index += 1  # Move to the next flashcard
            self.current_flashcard = self.all_flashcards[self.current_index]  # Update current flashcard
            return self.current_flashcard
        return None

    def get_current_flashcard_answer(self):
        """
        Returns the answer of the current flashcard.

        Returns:
            str or None: The answer of the current flashcard, or None if no flashcard is selected.
        """
        if self.current_flashcard:
            return self.current_flashcard.answer  # Return the answer of the current flashcard
        return None

    def get_current_flashcard_question(self):
        """
        Returns the question of the current flashcard.

        Returns:
            str or None: The question of the current flashcard, or None if no flashcard is selected.
        """
        if self.current_flashcard:
            return self.current_flashcard.question  # Return the question of the current flashcard
        return None
