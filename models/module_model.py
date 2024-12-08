
class Module:
    def __init__(self, module_id, name):
        self.id = module_id
        self.name = name


class Flashcard:
    def __init__(self, flashcard_id, module_id, question, answer):
        self.id = flashcard_id
        self.module_id = module_id
        self.question = question
        self.answer = answer
