
def check_flashcard_existence(db_service, module_id):
    flashcards = db_service.get_flashcards_by_module(module_id)
    return len(flashcards) > 0
