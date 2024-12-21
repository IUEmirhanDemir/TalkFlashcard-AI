import openai
from services.config_service import ConfigService

class ChatGPTService:
    """
    Service for interacting with the OpenAI API to generate flashcards.
    This service allows setting the API key and generating flashcards based on a text section.
    """

    def __init__(self, config_service=None, api_key=None):
        """
        Initializes the ChatGPTService with a config service and an API key.

        Args:
            config_service (ConfigService, optional): The configuration service for API key management.
            api_key (str, optional): The API key for OpenAI. If not provided, it is fetched from the config service.
        """
        self.config_service = config_service or ConfigService()  # Use provided config service or create a new one
        self.api_key = api_key or self.config_service.get_api_key()  # Get API key from service or provided
        if not self.api_key:
            raise ValueError(
                "API-Key für OpenAI nicht gefunden. Bitte setzen Sie die Umgebungsvariable 'OPENAI_API_KEY' "
                "oder fügen Sie ihn über die Anwendung hinzu."
            )
        openai.api_key = self.api_key  # Set the OpenAI API key

    def set_api_key(self, api_key):
        """
        Sets a new API key for OpenAI and updates the configuration service if available.

        Args:
            api_key (str): The new API key for OpenAI.
        """
        self.api_key = api_key
        openai.api_key = self.api_key  # Update OpenAI API key
        if self.config_service:
            self.config_service.set_api_key(api_key)  # Save the API key in the config service

    def generate_flashcards(self, text_section):
        """
        Generates flashcards based on the provided text section using OpenAI's GPT model.

        Args:
            text_section (str): The text section from which flashcards will be generated.

        Returns:
            list: A list of generated flashcards, each containing a question and an answer.
        """
        client = openai

        # Prompt for generating flashcards (content remains in German as requested)
        prompt = (
            f"Erstelle 10 kurze und einfache Karteikarten basierend auf dem folgenden Textabschnitt:\n\n"
            f"\"{text_section}\"\n\n"
            f"Für jede Karteikarte gib eine Frage und eine Antwort an.\n"
            f"Die Karteikarten müssen nicht nummeriert werden, sondern nur Frage und Antwort enthalten.\n"
            f"Ohne Karteikarte bzw. Karteikartenummer aufzulisten nur die folgende Struktur beibehalten.\n"
            f"Verwende genau folgende Struktur:\n"
            f"Frage:\n"
            f"Antwort:\n\n"
            f"Verwende maximal 10 Stichpunkte.\n"
            f"Nutze Stichpunkte oder kurze Texterklärungen, je nachdem, was für das jeweilige Thema sinnvoller ist.\n"
            f"Füge am Ende jeder Karteikarte immer ein explizites Beispiel hinzu."
        )

        try:
            # Request flashcard generation from OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Du bist ein Prof."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            generated_text = response.choices[0].message.content  # Get the generated content
            flashcards = self.parse_flashcards(generated_text)  # Parse the generated text into flashcards
            return flashcards
        except Exception as e:
            raise e  # Raise an exception if something goes wrong

    def parse_flashcards(self, generated_text):
        """
        Parses the generated text into a list of flashcards.

        Args:
            generated_text (str): The text returned by the OpenAI API containing the flashcards.

        Returns:
            list: A list of flashcards where each flashcard is a dictionary with 'question' and 'answer'.
        """
        flashcards = []
        entries = generated_text.strip().split('\n\n')  # Split the text into separate entries
        for entry in entries:
            if "Frage:" in entry and "Antwort:" in entry:
                parts = entry.split('Antwort:')
                question = parts[0].replace('Frage:', '').strip()  # Extract the question
                answer = parts[1].strip()  # Extract the answer
                flashcards.append({'question': question, 'answer': answer})
        return flashcards
