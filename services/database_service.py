import sqlite3
from models.module_model import Module, Flashcard

class DatabaseService:
    """
    Provides database operations for modules and flashcards.
    """

    def __init__(self, db_name="modules.db"):
        """
        Initializes the database connection and tables.

        Args:
            db_name (str): The database file name.
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_modules_table()
        self.create_flashcards_table()

    def create_modules_table(self):
        """
        Creates the modules table if it does not exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    def create_flashcards_table(self):
        """
        Creates the flashcards table if it does not exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
            )
        ''')
        self.connection.commit()

    def get_all_modules(self):
        """
        Retrieves all modules from the database.

        Returns:
            List[Module]: A list of Module objects.
        """
        self.cursor.execute("SELECT * FROM modules")
        rows = self.cursor.fetchall()
        return [Module(*row) for row in rows]

    def add_module(self, module_name):
        """
        Adds a new module to the database.

        Args:
            module_name (str): The name of the module.
        """
        self.cursor.execute("INSERT INTO modules (name) VALUES (?)", (module_name,))
        self.connection.commit()

    def add_flashcard(self, module_id, question, answer):
        """
        Adds a flashcard to a specific module.

        Args:
            module_id (int): The ID of the module.
            question (str): The question text.
            answer (str): The answer text.
        """
        self.cursor.execute(
            "INSERT INTO flashcards (module_id, question, answer) VALUES (?, ?, ?)",
            (module_id, question, answer)
        )
        self.connection.commit()

    def get_flashcards_by_module(self, module_id):
        """
        Retrieves all flashcards for a specific module.

        Args:
            module_id (int): The ID of the module.

        Returns:
            List[Flashcard]: A list of Flashcard objects.
        """
        self.cursor.execute(
            "SELECT * FROM flashcards WHERE module_id = ?",
            (module_id,)
        )
        rows = self.cursor.fetchall()
        return [Flashcard(*row) for row in rows]

    def update_flashcard(self, flashcard_id, question, answer):
        """
        Updates a specific flashcard.

        Args:
            flashcard_id (int): The ID of the flashcard to update.
            question (str): The updated question text.
            answer (str): The updated answer text.
        """
        self.cursor.execute(
            "UPDATE flashcards SET question = ?, answer = ? WHERE id = ?",
            (question, answer, flashcard_id)
        )
        self.connection.commit()

    def delete_module_with_flashcards(self, module_id):
        """
        Deletes a module and all its associated flashcards.

        Args:
            module_id (int): The ID of the module to delete.
        """
        self.cursor.execute("DELETE FROM flashcards WHERE module_id = ?", (module_id,))
        self.cursor.execute("DELETE FROM modules WHERE id = ?", (module_id,))
        self.connection.commit()

    def delete_flashcards_by_module(self, module_id):
        """
        Deletes all flashcards for a specific module.

        Args:
            module_id (int): The ID of the module.
        """
        self.cursor.execute("DELETE FROM flashcards WHERE module_id = ?", (module_id,))
        self.connection.commit()

    def delete_flashcard(self, flashcard_id):
        """
        Deletes a specific flashcard.

        Args:
            flashcard_id (int): The ID of the flashcard to delete.
        """
        self.cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
        self.connection.commit()

    def close_connection(self):
        """
        Closes the database connection.
        """
        self.connection.close()
