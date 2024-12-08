
import sqlite3
from models.module_model import Module, Flashcard

class DatabaseService:
    def __init__(self, db_name="modules.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_modules_table()
        self.create_flashcards_table()

    def create_modules_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    def create_flashcards_table(self):
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
        self.cursor.execute("SELECT * FROM modules")
        rows = self.cursor.fetchall()
        return [Module(*row) for row in rows]

    def add_module(self, module_name):
        self.cursor.execute("INSERT INTO modules (name) VALUES (?)", (module_name,))
        self.connection.commit()

    def add_flashcard(self, module_id, question, answer):
        self.cursor.execute(
            "INSERT INTO flashcards (module_id, question, answer) VALUES (?, ?, ?)",
            (module_id, question, answer)
        )
        self.connection.commit()

    def get_flashcards_by_module(self, module_id):
        self.cursor.execute(
            "SELECT * FROM flashcards WHERE module_id = ?",
            (module_id,)
        )
        rows = self.cursor.fetchall()
        return [Flashcard(*row) for row in rows]

    def update_flashcard(self, flashcard_id, question, answer):
        self.cursor.execute(
            "UPDATE flashcards SET question = ?, answer = ? WHERE id = ?",
            (question, answer, flashcard_id)
        )
        self.connection.commit()

    def close_connection(self):
        self.connection.close()

    def delete_module_with_flashcards(self, module_id):
        self.cursor.execute("DELETE FROM flashcards WHERE module_id = ?", (module_id,))
        self.cursor.execute("DELETE FROM modules WHERE id = ?", (module_id,))
        self.connection.commit()

    def delete_flashcards_by_module(self, module_id):
        self.cursor.execute("DELETE FROM flashcards WHERE module_id = ?", (module_id,))
        self.connection.commit()

    def delete_flashcard(self, flashcard_id):

        self.cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
        self.connection.commit()
