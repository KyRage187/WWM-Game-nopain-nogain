#import der klassen
#imports gamelogik

import sys
from pathlib import Path

# Die GameLogik-Module (quiz, spieler, ...) liegen in einem Nachbarordner.
# Damit Python sie findet, fuegen wir den Ordner zum Suchpfad hinzu.
BASIS_PFAD = Path(__file__).parent.parent
sys.path.append(str(BASIS_PFAD / "GameLogik"))

import streamlit as st

from quiz import Quiz
from spieler import Spieler
from questionloader import QuestionLoader
from bestenliste import Bestenliste
from joker import FiftyFiftyJoker, TelefonJoker, PublikumsJoker

# skelett der app
st.set_page_config(page_title="Wer wird Millionär?", page_icon=":moneybag:", layout="centered")

# QuestionLoader erwartet einen ORDNER mit JSON-Dateien, keine einzelne Datei.
FRAGEN_PFAD = str(BASIS_PFAD / "FragenDatenbank")
BESTENLISTE_PFAD = str(BASIS_PFAD / "bestenliste.json")
TELEFON_PERSONEN = ["JBL", "Drabi", "Wezon"]

#sessionstate
#ist bis jetz nur prototyp

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "bestenliste" not in st.session_state:
    st.session_state.bestenliste = Bestenliste(BESTENLISTE_PFAD)

if "joker_ergebnis" not in st.session_state:
    st.session_state.joker_ergebnis = None

if "telefon_auswahl_aktiv" not in st.session_state:
    st.session_state.telefon_auswahl_aktiv = False

if "runde_beendet" not in st.session_state:
    st.session_state.runde_beendet = False

#startbildschirm

def startbildschirm():
    st.title("Wer wird Millionär?")
    st.subheader("Kommst du durch das Semester?")
    st.write("Beantworte 15 Fragen zu unseren Vorlesung und werde zum Millionär!!!")

    #playername
    name = st.text_input("Dein Name:", key="name_input")
    kein_start = name.strip() == ""

    if st.button("Spiel starten", disabled=kein_start):
        loader = QuestionLoader(FRAGEN_PFAD)
        fragen = loader.lade_fragen()

        # Quiz braucht 3 Argumente: spieler, fragen UND eine Liste von Jokern
        spieler = Spieler(name.strip())
        joker = [
            FiftyFiftyJoker(),
            TelefonJoker("JBL"),
            PublikumsJoker(),
        ]
        st.session_state.quiz = Quiz(spieler, fragen, joker)
        st.rerun()


# =========================================================
# Routing / Hauptsteuerung
# Entscheidet, welcher Bildschirm gerade angezeigt wird.
# =========================================================

if st.session_state.quiz is None:
    # Noch kein Spiel gestartet -> Startbildschirm
    startbildschirm()
else:
    # Ab hier kommen spaeter: Frage anzeigen, Joker, Gewinnleiter, Rundenende ...
    quiz = st.session_state.quiz
    st.write(f"Spiel laeuft fuer: {quiz.spieler.name}")
    st.write("TODO: Frage-Anzeige einbauen")

