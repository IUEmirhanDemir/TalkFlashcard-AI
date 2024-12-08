class InteractiveModeController:
    def __init__(self, main_window, module):
        self.main_window = main_window
        self.module = module
        self.db_service = self.main_window.db_service
        self.all_flashcards = self.db_service.get_flashcards_by_module(module.id)
        self.current_index = -1
        self.current_flashcard = None

    def reset_flashcards(self):

        self.current_index = -1
        self.current_flashcard = None

    def get_next_flashcard(self):

        if self.all_flashcards and self.current_index + 1 < len(self.all_flashcards):
            return self.all_flashcards[self.current_index + 1]
        return None

    def move_to_next_flashcard(self):

        if self.all_flashcards and self.current_index + 1 < len(self.all_flashcards):
            self.current_index += 1
            self.current_flashcard = self.all_flashcards[self.current_index]
            return self.current_flashcard
        return None

    def get_current_flashcard_answer(self):
        if self.current_flashcard:
            return self.current_flashcard.answer
        return None

    def get_current_flashcard_question(self):
        if self.current_flashcard:
            return self.current_flashcard.question
        return None
