
import openai
from services.config_service import ConfigService

class ChatGPTService:
    def __init__(self, config_service=None, api_key=None):
        self.config_service = config_service or ConfigService()
        self.api_key = api_key or self.config_service.get_api_key()
        if not self.api_key:
            raise ValueError(
                "API-Key für OpenAI nicht gefunden. Bitte setzen Sie die Umgebungsvariable 'OPENAI_API_KEY' "
                "oder fügen Sie ihn über die Anwendung hinzu."
            )
        openai.api_key = self.api_key

    def set_api_key(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key
        if self.config_service:
            self.config_service.set_api_key(api_key)

    def generate_flashcards(self, text_section):

        client = openai

        """Generiert Karteikarten basierend auf einem Textabschnitt."""
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
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein Prof"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            generated_text = response.choices[0].message.content
            flashcards = self.parse_flashcards(generated_text)
            return flashcards
        except Exception as e:
            raise e

    def parse_flashcards(self, generated_text):
        flashcards = []
        entries = generated_text.strip().split('\n\n')
        for entry in entries:
            if "Frage:" in entry and "Antwort:" in entry:
                parts = entry.split('Antwort:')
                question = parts[0].replace('Frage:', '').strip()
                answer = parts[1].strip()
                flashcards.append({'question': question, 'answer': answer})
        return flashcards

