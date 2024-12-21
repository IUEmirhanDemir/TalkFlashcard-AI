## Inhaltsverzeichnis
1. [Sprache wechseln](#sprache-wechseln)
    - [Englische Version](#english-version)
    - [Deutsche Version](#deutsche-version)
2. [Systemvoraussetzungen](#systemvoraussetzungen)
3. [Projekt einrichten](#projekt-einrichten)
    - [Repository klonen](#repository-klonen)
    - [Virtuelle Umgebung erstellen](#virtuelle-umgebung-erstellen)
    - [Virtuelle Umgebung aktivieren](#virtuelle-umgebung-aktivieren)
4. [Projekt ausführen](#projekt-ausf%C3%BChren)
    - [Starten des Programms](#starten-des-programms)
    - [Ausführen über eine ausführbare Datei](#ausf%C3%BChren-%C3%BCber-eine-ausf%C3%BChrbare-datei)
5. [Nützliche Ressourcen](#n%C3%BCtzliche-ressourcen)

---

<a name="sprache-wechseln"></a>
### Sprache wechseln

- Für die [**Englische Version**](#english-version), klicke hier.
- Für die [**Deutsche Version**](#deutsche-version), lies weiter.

---

<a name="systemvoraussetzungen"></a>
## Systemvoraussetzungen

- **Python-Version**: Mindestens Python 3.
- Abhängigkeiten: Siehe `requirements.txt`.
- Unterstützte Betriebssysteme: Linux, macOS, Windows.
- Internetverbindung: Für das Klonen des Repositories und das Installieren von Abhängigkeiten notwendig. Auch für den interaktiven Lernmodus und das Generieren von Karteikarten, ist zwgend eine Internetverbindung erforderlich, da es die OpenAI API verwendet.

### Python installieren

- **Windows**: Lade Python von [python.org](https://www.python.org/downloads/) herunter und installiere es. Stelle sicher, dass du die Option "Add Python to PATH" während der Installation aktivierst.
- **macOS**: Verwende `brew install python` (Homebrew erforderlich).
- **Linux**: Installiere Python über deinen Paketmanager, z. B. `sudo apt-get install python3` (Debian/Ubuntu).

Tipp: Überprüfe die Python-Version mit folgendem Befehl:

```bash
python --version
```

---

<a name="projekt-einrichten"></a>
## Projekt einrichten

### Repository klonen

Das Klonen des Repositories ist der erste Schritt, um das Projekt lokal einzurichten.

### Virtuelle Umgebung erstellen

Erstelle eine virtuelle Umgebung, um die Abhängigkeiten des Projekts sauber zu isolieren. Dies ist besonders hilfreich, um Konflikte mit anderen Python-Projekten zu vermeiden.

- **Linux/macOS**:

  ```bash
  python3 -m venv venv
  ```

- **Windows**:

  ```bash
  python -m venv venv
  ```

### Virtuelle Umgebung aktivieren

- **Linux/macOS**:

  ```bash
  source venv/bin/activate
  ```

- **Windows**:

  ```bash
  venv\Scriptsctivate
  ```

Installiere anschließend die Abhängigkeiten mit:

```bash
pip install -r requirements.txt
```

> Hinweis: Falls du mit Proxy-Einstellungen arbeitest, überprüfe, ob `pip` korrekt konfiguriert ist.

---

<a name="projekt-ausf%C3%BChren"></a>
## Projekt ausführen

### Starten des Programms

Führe das Hauptskript aus, um das Programm zu starten:

```bash
python3 main.py
```

Das Skript startet das Hauptprogramm und gibt relevante Informationen in der Konsole aus. Optional kannst du bestimmte Parameter übergeben, z. B.:

```bash
python3 main.py --config config.yaml
```

### Ausführen über eine ausführbare Datei

- **Linux/macOS**:

  Navigiere in das Verzeichnis der ausführbaren Datei und mache sie ggf. ausführbar:

  ```bash
  chmod +x main
  ./main
  ```

  > Hinweis: Möglicherweise musst du Sicherheitswarnungen akzeptieren.

- **Windows**:

  Navigiere in den Ordner mit der ausführbaren Datei und doppelklicke darauf. Du wirst möglicherweise aufgefordert, Sicherheitswarnungen zu akzeptieren. Stelle sicher, dass du Administratorrechte hast, falls erforderlich.

---

<a name="n%C3%BCtzliche-ressourcen"></a>
## Nützliche Ressourcen

- [Python Offizielle Dokumentation](https://docs.python.org/3/)
- [GitHub Markdown Guide](https://guides.github.com/features/mastering-markdown/)
- [Homebrew für macOS](https://brew.sh/)
- [Pip Paketmanagement](https://pip.pypa.io/en/stable/)

Falls Probleme auftreten, kannst du uns über die Repository-Issues erreichen oder die Community auf Stack Overflow um Hilfe bitten.

---

<a name="english-version"></a>
## English Version

### System Requirements

- **Python Version**: At least Python 3.
- Dependencies: See `requirements.txt`.
- Supported OS: Linux, macOS, Windows.
- Internet Connection: Needed for cloning the repository and installing dependencies. An internet connection is also required for the interactive learning mode and generating flashcards, as it uses the OpenAI API.
### Setup Instructions

1. Clone the repository:


2. Create a virtual environment:

   - **Linux/macOS**:

     ```bash
     python3 -m venv venv
     ```

   - **Windows**:

     ```bash
     python -m venv venv
     ```

3. Activate the virtual environment:

   - **Linux/macOS**:

     ```bash
     source venv/bin/activate
     ```

   - **Windows**:

     ```bash
     venv\Scriptsctivate
     ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the program:

   ```bash
   python3 main.py
   ```

6. To execute a binary file, follow the OS-specific instructions above.

7. For more help, see the [Useful Resources](#n%C3%BCtzliche-ressourcen) section.

---