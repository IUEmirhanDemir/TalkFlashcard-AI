def check_flashcard_existence(db_service, module_id):
    """
    Checks if any flashcards exist for the given module.

    Args:
        db_service (DatabaseService): The database service used to query flashcards.
        module_id (int): The ID of the module to check.

    Returns:
        bool: True if flashcards exist for the module, otherwise False.
    """
    flashcards = db_service.get_flashcards_by_module(module_id)  # Retrieve flashcards for the module
    return len(flashcards) > 0  # Check if the flashcard list is not empty
