# Wer wird Millionär?

Ein Quizspiel nach dem Vorbild von **„Wer wird Millionär?“**, entwickelt in Python mit **Streamlit**. Das Spiel bietet eine grafische Weboberfläche, verschiedene Schwierigkeitsstufen, Joker sowie eine Bestenliste.

## Features

* 🎮 Quizspiel im Stil von *Wer wird Millionär?*
* ❓ Fragen mit unterschiedlichen Schwierigkeitsgraden
* 🃏 Drei Joker:

  * 50:50-Joker
  * Publikumsjoker
  * Telefonjoker
* 🏆 Bestenliste zur Speicherung der Spielergebnisse
* 🌐 Benutzeroberfläche mit Streamlit
* 🧪 Unit-Tests für die wichtigsten Klassen

## Projektstruktur

```text
WWM-Game-nopain-nogain/
│
├── GameLogik/
│   ├── bestenliste.py
│   ├── difficulty.py
│   ├── frage.py
│   ├── joker.py
│   ├── questionloader.py
│   ├── quiz.py
│   └── spieler.py
│
├── Streamlitt/
│   └── streamlit.py
│
├── Unittests/
│   ├── test_bestenliste.py
│   ├── test_frage.py
│   ├── test_joker.py
│   ├── test_questionloader.py
│   ├── test_quiz.py
│   └── test_spieler.py
│
├── requirements.txt
└── README.md
```

## Voraussetzungen

* Python **3.12** oder neuer
* pip

## Installation

Repository klonen:

```bash
git clone https://github.com/KyRage187/WWM-Game-nopain-nogain.git
cd WWM-Game-nopain-nogain
```

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

## Anwendung starten

Das Spiel wird über Streamlit gestartet:

```bash
streamlit run Streamlitt/streamlit.py
```

Anschließend öffnet sich die Anwendung automatisch im Browser. Falls dies nicht geschieht, kann die angezeigte lokale URL (meist `http://localhost:8501`) im Browser geöffnet werden.

## Tests ausführen

Alle Unit-Tests können mit folgendem Befehl gestartet werden:

```bash
python -m unittest discover Unittests
```

## Verwendete Technologien

* Python 3
* Streamlit
* unittest

## Mitwirkende

Khalil Albert, Emil Gutschmidt, Michel Köhler\
Projekt im Rahmen von "Fortgeschrittene Programmierung" des Kurses WDSKI25A

## Lizenz

Dieses Projekt dient ausschließlich Lehr- und Lernzwecken.

