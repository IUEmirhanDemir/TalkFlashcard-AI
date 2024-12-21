class Module:
    """
    Represents a module in the system.
    A module can have many flashcards associated with it.
    """

    def __init__(self, module_id, name):
        """
        Initializes the module with its ID and name.

        Args:
            module_id (int): The unique ID of the module.
            name (str): The name of the module.
        """
        self.id = module_id  # Module ID
        self.name = name  # Module name


class Flashcard:
    """
    Represents a flashcard in the system.
    A flashcard contains a question and an answer, and is associated with a module.
    """

    def __init__(self, flashcard_id, module_id, question, answer):
        """
        Initializes the flashcard with its ID, associated module ID, question, and answer.

        Args:
            flashcard_id (int): The unique ID of the flashcard.
            module_id (int): The ID of the module this flashcard belongs to.
            question (str): The question of the flashcard.
            answer (str): The answer to the flashcard's question.
        """
        self.id = flashcard_id  # Flashcard ID
        self.module_id = module_id  # Module ID this flashcard belongs to
        self.question = question  # The question of the flashcard
        self.answer = answer  # The answer to the flashcard's question
