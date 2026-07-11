# imports - alles was wir brauchen
import sys
from pathlib import Path

# der hack damit python die gamelogik findet (die liegt im nachbarordner)
# ohne das würde python meckern dass quiz, spieler usw nicht gefunden werden
BASIS_PFAD = Path(__file__).parent.parent
sys.path.append(str(BASIS_PFAD / "GameLogik"))

import streamlit as st

# jetzt die ganzen klassen von der logik importieren
from quiz import Quiz
from spieler import Spieler
from questionloader import QuestionLoader
from bestenliste import Bestenliste
from joker import FiftyFiftyJoker, TelefonJoker, PublikumsJoker

# app config - titel icon und so
st.set_page_config(page_title="Wer wird Millionär?", page_icon=":moneybag:", layout="centered")

# die pfade zu unseren dateien
FRAGEN_PFAD = str(BASIS_PFAD / "FragenDatenbank")  # ordner mit den json fragen
BESTENLISTE_PFAD = str(BASIS_PFAD / "bestenliste.json")  # wo die highscores gespeichert werden
TELEFON_PERSONEN = ["JBL", "Drabi", "Wezon"]  # die drei fürs telefon

# session state initialisieren - das ist das gedächtnis von streamlit
# ohne das würde bei jedem klick alles vergessen werden (weil skript neu startet)

if "quiz" not in st.session_state:
    st.session_state.quiz = None  # kein spiel am anfang

if "bestenliste" not in st.session_state:
    st.session_state.bestenliste = Bestenliste(BESTENLISTE_PFAD)  # bestenliste einmal laden

if "joker_ergebnis" not in st.session_state:
    st.session_state.joker_ergebnis = None  # noch kein joker benutzt

if "telefon_auswahl_aktiv" not in st.session_state:
    st.session_state.telefon_auswahl_aktiv = False  # telefon auswahl zu

if "runde_beendet" not in st.session_state:
    st.session_state.runde_beendet = False  # spiel läuft normal


# STARTBILDSCHIRM


def startbildschirm():
    st.title("Wer wird Millionär?")
    st.subheader("Kommst du durch das Semester?")
    st.write("Beantworte 15 Fragen zu unseren Vorlesung und werde zum Millionär!!!")

    # name eingeben
    name = st.text_input("Dein Name:", key="name_input")
    kein_start = name.strip() == ""  # wenn name leer ist kann man nicht starten

    if st.button("Spiel starten", disabled=kein_start):
        # fragen aus der datenbank laden
        loader = QuestionLoader(FRAGEN_PFAD)
        fragen = loader.lade_fragen()  # gibt 15 zufällige fragen zurück (5 leicht 5 mittel 5 schwer)

        # spieler anlegen und die drei joker erstellen
        spieler = Spieler(name.strip())
        joker = [
            FiftyFiftyJoker(),
            TelefonJoker("JBL"),  # der platzhalter wird später überschrieben wenn man anruft
            PublikumsJoker(),
        ]
        # quiz objekt bauen und im session state speichern
        st.session_state.quiz = Quiz(spieler, fragen, joker)
        st.rerun()  # seite neu laden damit spiel startet




# FRAGE ANZEIGEN

def hole_aktuelle_frage(quiz):
    
    if st.session_state.get("geladene_nummer") != quiz.aktuelle_frage_nummer:
        st.session_state.aktuelle_frage_obj = quiz.naechste_frage()  # neue frage ziehen
        st.session_state.geladene_nummer = quiz.aktuelle_frage_nummer  # nummer merken
    return st.session_state.aktuelle_frage_obj  # gespeicherte frage zurückgeben


def zeige_frage(quiz, frage):
    # geldbetrag für die aktuelle frage aus der gewinnleiter holen
    betrag = quiz.gewinnleiter[quiz.aktuelle_frage_nummer - 1]  # -1 weil listen bei 0 anfangen
    st.subheader(f"Frage {quiz.aktuelle_frage_nummer} um {betrag} €")
    st.write(f"### {frage.text}")  # ### macht fett

    # 50/50 joker behandlung
    # wenn der 50/50 aktiv ist kriegen wir hier die noch übrigen antworten
    # die anderen blenden wir aus
    verbleibende = None
    daten = st.session_state.joker_ergebnis
    if daten is not None and isinstance(daten["joker"], FiftyFiftyJoker):
        verbleibende = daten["ergebnis"]  # die liste mit den 2 verbleibenden antworten

    # antwort-buttons in 2 spalten (so dass sie nebeneinander sind)
    spalten = st.columns(2)
    for i, antwort in enumerate(frage.antworten):  # durch alle 4 antworten loopen
        with spalten[i % 2]:  # i % 2 macht links rechts links rechts (0 1 0 1)
            # ist diese antwort weggestrichen vom 50/50?
            weggestrichen = verbleibende is not None and antwort not in verbleibende
            # wenn weggestrichen zeig strich statt text
            label = antwort if not weggestrichen else "—"
            if st.button(
                label,
                key=f"antw_{quiz.aktuelle_frage_nummer}_{i}",  # eindeutiger key für jeden button
                disabled=weggestrichen,  # ausgegraut wenn weggestrichen
                use_container_width=True,
            ):
                # antwort an die logik geben die checkt obs richtig ist und macht guthaben usw
                quiz.antwort_pruefen(antwort)
                # joker anzeige zurücksetzen damit sie nicht in die nächste frage klebt
                st.session_state.joker_ergebnis = None
                st.rerun()  # neu laden



# JOKER BUTTONS


def zeige_joker(quiz):
    st.write("### Joker")
    # 3 spalten für die 3 joker
    spalten = st.columns(len(quiz.joker))
    for spalte, joker in zip(spalten, quiz.joker):  # jeder joker kriegt ne spalte
        with spalte:
            # button für den joker, gesperrt wenn schon benutzt
            if st.button(str(joker), disabled=joker.ist_benutzt(), key=f"joker_{str(joker)}", use_container_width=True):
                # telefon ist speziell weil man erst die person wählen muss
                if isinstance(joker, TelefonJoker):
                    st.session_state.telefon_auswahl_aktiv = True  # auswahl öffnen
                else:
                    # 50/50 oder publikum direkt anwenden
                    ergebnis = quiz.joker_einsetzen(joker)
                    st.session_state.joker_ergebnis = {"joker": joker, "ergebnis": ergebnis}
                st.rerun()


def zeige_telefon_auswahl(quiz):
    # die drei buttons für jbl drabi wezon
    # zeigt sich nur wenn telefon_auswahl_aktiv true ist
    if not st.session_state.telefon_auswahl_aktiv:
        return  # nichts tun wenn nicht aktiv

    st.info("Wen möchtest du anrufen?")
    spalten = st.columns(len(TELEFON_PERSONEN))  # 3 buttons nebeneinander
    for spalte, person in zip(spalten, TELEFON_PERSONEN):
        with spalte:
            if st.button(person, key=f"anruf_{person}", use_container_width=True):
                # telefonjoker aus der liste raussuchen
                telefon = None
                for j in quiz.joker:
                    if isinstance(j, TelefonJoker):
                        telefon = j
                        break
                # jetzt die gewählte person setzen 
                telefon.person = person
                # JETZT erst anwenden mit der richtigen person
                ergebnis = quiz.joker_einsetzen(telefon)
                st.session_state.joker_ergebnis = {"joker": telefon, "ergebnis": ergebnis, "person": person}
                st.session_state.telefon_auswahl_aktiv = False  # auswahl wieder zu
                st.rerun()


def zeige_joker_ergebnis():
    # zeigt was der joker gemacht hat (aber nur für telefon und publikum)
    # 50/50 wird direkt bei den buttons gehandhabt
    daten = st.session_state.joker_ergebnis
    if daten is None:
        return  # kein joker benutzt = nichts anzeigen
    joker = daten["joker"]  # welcher joker wars

    if isinstance(joker, PublikumsJoker):
        # publikum gibt prozente zurück für jede antwort
        st.write("#### Das Publikum stimmt ab:")
        for antwort, prozent in daten["ergebnis"].items():
            st.progress(prozent / 100, text=f"{antwort}: {prozent} %")  # balken pro antwort

    elif isinstance(joker, TelefonJoker):
        # telefon gibt nen text zurück (je nach person unterschiedlich)
        st.write(f"#### {daten.get('person', '')} sagt:")
        st.info(daten["ergebnis"])  # blauer kasten mit dem spruch



# HAUPTSTEUERUNG - DAS IST DER KERN

# hier wird entschieden welcher bildschirm angezeigt wird

if st.session_state.quiz is None:
    # kein spiel läuft -> startbildschirm
    startbildschirm()
else:
    # spiel läuft -> nur die funktionen aufrufen, die aktuell noch existieren
    quiz = st.session_state.quiz
    frage = hole_aktuelle_frage(quiz)

    if isinstance(frage, str):
        # sicherheitsnetz: wenn keine fragen mehr da sind kriegen wir nen text zurück
        st.warning(frage)
    else:
        # normales spiel
        zeige_frage(quiz, frage)
        zeige_joker_ergebnis()
        zeige_joker(quiz)
        zeige_telefon_auswahl(quiz)



