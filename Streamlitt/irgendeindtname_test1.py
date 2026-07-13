#streamlit run Streamlitt/irgendeindtname_test1.py
# imports - alles was wir brauchen

import sys
import time  # fuer die kurzen pausen bei der antwort-animation
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
# layout="wide" statt "centered" -> wir brauchen platz fuer die gewinnleiter RECHTS
# die farben (dunkelblau + gold) kommen aus .streamlit/config.toml - dafuer braucht man KEIN css!
st.set_page_config(page_title="Wer wird Millionär?", page_icon=":moneybag:", layout="wide")

# die pfade zu unseren dateien
FRAGEN_PFAD = str(BASIS_PFAD / "FragenDatenbank")  # ordner mit den json fragen
BESTENLISTE_PFAD = str(BASIS_PFAD / "bestenliste.json")  # wo die highscores gespeichert werden
TELEFON_PERSONEN = ["JBL", "Drabi", "Wezon"]  # die drei fürs telefon

# schoenere anzeige-namen fuer die joker buttons
# NUR das label! die keys der buttons benutzen weiter str(joker) -> logik unveraendert
JOKER_LABELS = {
    "FiftyFiftyJoker": "50:50",
    "TelefonJoker": "📞 Telefon",
    "PublikumsJoker": "👥 Publikum",
}


def eur(betrag):
    # macht aus 1000000 -> "1.000.000 €"
    # f"{...:,}" setzt kommas als tausendertrenner, die tauschen wir gegen punkte
    return f"{betrag:,} €".replace(",", ".")


# session state initialisieren - das ist das gedächtnis von streamlit
# ohne das würde bei jedem klick alles vergessen werden (weil skript neu startet)

if "quiz" not in st.session_state:
    st.session_state.quiz = None  # kein spiel am anfang

if "bestenliste" not in st.session_state:
    st.session_state.bestenliste = Bestenliste(BESTENLISTE_PFAD)  # bestenliste einmal laden

if "joker_ergebnisse" not in st.session_state:
    st.session_state.joker_ergebnisse = {}  # merkt pro joker das ergebnis (mehrere gleichzeitig)

if "fifty_verbleibende" not in st.session_state:
    st.session_state.fifty_verbleibende = None  # merkt 50/50 ergebnis für aktuelle frage

if "telefon_auswahl_aktiv" not in st.session_state:
    st.session_state.telefon_auswahl_aktiv = False  # telefon auswahl zu

if "runde_beendet" not in st.session_state:
    st.session_state.runde_beendet = False  # spiel läuft normal

if "gewaehlte_antwort" not in st.session_state:
    st.session_state.gewaehlte_antwort = None  # welche antwort gerade angeklickt wurde (fuer die animation)


# RESET HELFER

def reset_runde_state():
    # setzt ALLE merker für eine runde auf anfang zurück
    # damit nach neustart/bestenliste keine alte frage oder alter joker-stand hängen bleibt
    st.session_state.geladene_nummer = None       # welche fragennummer gerade geladen ist
    st.session_state.aktuelle_frage_obj = None     # das gecachte frage-objekt
    st.session_state.joker_ergebnisse = {}         # anzeige der genutzten joker leeren
    st.session_state.fifty_verbleibende = None     # 50/50 striche weg
    st.session_state.telefon_auswahl_aktiv = False # telefon-auswahl zu
    st.session_state.runde_beendet = False         # spiel läuft wieder normal
    st.session_state.gewaehlte_antwort = None      # keine antwort ausgewaehlt


# STARTBILDSCHIRM


def zeige_bestenliste_tabelle():
    # die bestenliste aus der json anzeigen (issue #24) - wir LESEN nur,
    # gespeichert wird weiterhin nur beim "aufhören" button im rundenende
    eintraege = st.session_state.bestenliste.lade_bestenliste()
    st.write("### Bestenliste")
    if not eintraege:
        st.caption("Noch keine Einträge — spiel eine Runde und sichere dir Platz 1!")
        return

    # aus den rohen eintraegen huebsche zeilen bauen (medaillen fuer die top 3)
    medaillen = ["🥇", "🥈", "🥉"]
    anzeige = []
    for platz, eintrag in enumerate(eintraege, start=1):
        anzeige.append({
            "Platz": medaillen[platz - 1] if platz <= 3 else str(platz),
            "Name": eintrag["name"],
            "Guthaben": eur(eintrag["gesamt_guthaben"]),
            "Millionen": eintrag.get("millionen", 0),
        })
    # st.dataframe macht aus einer liste von dicts automatisch eine tabelle
    st.dataframe(anzeige, hide_index=True, use_container_width=True)


def startbildschirm():
    st.title("💰 Wer wird Millionär?")
    st.subheader("Kommst du durch das Semester?")
    st.write("Beantworte 15 Fragen zu unseren Vorlesungen und werde Millionär!")

    # die mitte schmaler machen, damit das eingabefeld nicht ueber die ganze breite geht
    # (links und rechts einfach leere spalten als abstand)
    aussen = st.columns([1, 2, 1])
    with aussen[1]:
        # name eingeben
        name = st.text_input("Dein Name:", key="name_input")
        kein_start = name.strip() == ""  # wenn name leer ist kann man nicht starten

        # type="primary" -> button bekommt die gold-farbe aus dem theme (config.toml)
        if st.button("Spiel starten", disabled=kein_start, type="primary", use_container_width=True):
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
            reset_runde_state()  # alle merker frisch machen -> keine zombie-frage aus alter runde
            st.rerun()  # seite neu laden damit spiel startet

        # bestenliste unter dem start-bereich anzeigen
        zeige_bestenliste_tabelle()


# KOPFZEILE (immer sichtbar waehrend dem spiel)

def zeige_kopfzeile(quiz):
    # loest das "man muss runterscrollen um name und guthaben zu sehen" problem:
    # titel links, daneben die drei wichtigsten infos als st.metric karten - IMMER oben
    spalten = st.columns([2, 1, 1, 1])
    with spalten[0]:
        st.write("## 💰 Wer wird Millionär?")
    with spalten[1]:
        st.metric("Spieler", quiz.spieler.name)
    with spalten[2]:
        st.metric("Runde", eur(quiz.spieler.runden_guthaben))
    with spalten[3]:
        st.metric("Gesamt", eur(quiz.spieler.gesamt_guthaben))


# FRAGE ANZEIGEN

def hole_aktuelle_frage(quiz):

    if st.session_state.get("geladene_nummer") != quiz.aktuelle_frage_nummer:
        st.session_state.aktuelle_frage_obj = quiz.naechste_frage()  # neue frage ziehen
        st.session_state.geladene_nummer = quiz.aktuelle_frage_nummer  # nummer merken
        st.session_state.fifty_verbleibende = None  # neue frage -> 50/50 zurücksetzen
    return st.session_state.aktuelle_frage_obj  # gespeicherte frage zurückgeben


def zeige_frage(quiz, frage):
    # geldbetrag für die aktuelle frage aus der gewinnleiter holen
    betrag = quiz.gewinnleiter[quiz.aktuelle_frage_nummer - 1]  # -1 weil listen bei 0 anfangen
    st.subheader(f"Frage {quiz.aktuelle_frage_nummer} um {eur(betrag)}")
    st.write(f"### {frage.text}")  # ### macht fett

    # wurde gerade eine antwort angeklickt? dann laeuft die animation statt der buttons
    if st.session_state.gewaehlte_antwort is not None:
        zeige_antwort_feedback(quiz, frage, st.session_state.gewaehlte_antwort)
        return  # keine buttons zeigen waehrend der animation

    # 50/50 joker behandlung
    # wenn der 50/50 aktiv ist kriegen wir hier die noch übrigen antworten
    # die anderen blenden wir aus
    verbleibende = st.session_state.fifty_verbleibende

    # antwort-buttons in 2 spalten (so dass sie nebeneinander sind)
    buchstaben = "ABCD"  # fuer die A/B/C/D praefixe wie im tv
    spalten = st.columns(2)
    for i, antwort in enumerate(frage.antworten):  # durch alle 4 antworten loopen
        with spalten[i % 2]:  # i % 2 macht links rechts links rechts (0 1 0 1)
            # ist diese antwort weggestrichen vom 50/50?
            weggestrichen = verbleibende is not None and antwort not in verbleibende
            # wenn weggestrichen zeig strich statt text
            label = f"{buchstaben[i]}: {antwort}" if not weggestrichen else "—"
            if st.button(
                label,
                key=f"antw_{quiz.aktuelle_frage_nummer}_{i}",  # eindeutiger key für jeden button
                disabled=weggestrichen,  # ausgegraut wenn weggestrichen
                use_container_width=True,
            ):
                # NICHT sofort pruefen - erst die antwort merken, damit beim naechsten
                # durchlauf die animation (orange -> gruen/rot) gezeigt werden kann
                st.session_state.gewaehlte_antwort = antwort
                st.rerun()


def zeige_antwort_feedback(quiz, frage, gewaehlt):
    # die mini-animation wie im tv: erst wird die gewaehlte antwort ORANGE,
    # dann wird aufgeloest: GRUEN = richtig, ROT = falsch (+ die richtige in gruen)
    # dafuer brauchen wir kein css: st.warning ist orange, st.success gruen, st.error rot!
    buchstaben = "ABCD"

    # st.empty ist ein platzhalter, den man mehrfach neu befuellen kann -
    # so koennen wir an derselben stelle erst orange und dann die aufloesung zeigen
    bereich = st.empty()

    # phase 1: die gewaehlte antwort orange markieren ("eingeloggt")
    with bereich.container():
        for i, antwort in enumerate(frage.antworten):
            if antwort == gewaehlt:
                st.warning(f"{buchstaben[i]}: {antwort}")  # oranger kasten
            else:
                st.write(f"{buchstaben[i]}: {antwort}")
    time.sleep(1.0)  # kurz zittern lassen wie im tv

    # phase 2: aufloesung an derselben stelle
    with bereich.container():
        for i, antwort in enumerate(frage.antworten):
            if antwort == frage.richtige_antwort:
                st.success(f"{buchstaben[i]}: {antwort}")  # gruen: die richtige antwort
            elif antwort == gewaehlt:
                st.error(f"{buchstaben[i]}: {antwort}")    # rot: deine falsche wahl
            else:
                st.write(f"{buchstaben[i]}: {antwort}")
    time.sleep(1.5)  # aufloesung kurz wirken lassen

    # JETZT erst an die logik uebergeben (guthaben, weiter oder verloren usw)
    quiz.antwort_pruefen(gewaehlt)
    # alle anzeige-merker fuer die naechste frage zuruecksetzen
    st.session_state.gewaehlte_antwort = None
    st.session_state.joker_ergebnisse = {}
    st.session_state.fifty_verbleibende = None
    st.rerun()



# JOKER BUTTONS


def zeige_joker(quiz):
    st.write("### Joker")
    # 3 spalten für die 3 joker
    spalten = st.columns(len(quiz.joker))
    for spalte, joker in zip(spalten, quiz.joker):  # jeder joker kriegt ne spalte
        with spalte:
            # schoenes label anzeigen, aber der KEY bleibt str(joker) -> logik unveraendert
            label = JOKER_LABELS.get(str(joker), str(joker))
            # button für den joker, gesperrt wenn schon benutzt
            if st.button(label, disabled=joker.ist_benutzt(), key=f"joker_{str(joker)}", use_container_width=True):
                # telefon ist speziell weil man erst die person wählen muss
                if isinstance(joker, TelefonJoker):
                    st.session_state.telefon_auswahl_aktiv = True  # auswahl öffnen
                else:
                    # 50/50 oder publikum direkt anwenden
                    ergebnis = quiz.joker_einsetzen(joker)
                    # ergebnis unter dem joker-namen ablegen -> so bleiben mehrere gleichzeitig sichtbar
                    st.session_state.joker_ergebnisse[type(joker).__name__] = {"joker": joker, "ergebnis": ergebnis}
                    if isinstance(joker, FiftyFiftyJoker):
                        st.session_state.fifty_verbleibende = ergebnis
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
                # telefon-ergebnis unter seinem namen ablegen -> bleibt neben anderen jokern sichtbar
                st.session_state.joker_ergebnisse[type(telefon).__name__] = {"joker": telefon, "ergebnis": ergebnis, "person": person}
                st.session_state.telefon_auswahl_aktiv = False  # auswahl wieder zu
                st.rerun()


def zeige_joker_ergebnis():
    # zeigt was ALLE bisher genutzten joker gemacht haben (telefon + publikum)
    # 50/50 wird direkt bei den buttons gehandhabt (striche an den antworten)
    # wir loopen durch alle gespeicherten ergebnisse -> mehrere gleichzeitig sichtbar
    for daten in st.session_state.joker_ergebnisse.values():
        joker = daten["joker"]  # welcher joker wars

        if isinstance(joker, PublikumsJoker):
            # publikum gibt prozente zurück für jede antwort
            # die balken faerbt streamlit automatisch in der theme-farbe (gold)
            st.write("#### Das Publikum stimmt ab:")
            for antwort, prozent in daten["ergebnis"].items():
                st.progress(prozent / 100, text=f"{antwort}: {prozent} %")  # balken pro antwort

        elif isinstance(joker, TelefonJoker):
            # telefon gibt nen text zurück (je nach person unterschiedlich)
            st.write(f"#### {daten.get('person', '')} sagt:")
            st.info(daten["ergebnis"])  # kasten mit dem spruch


# GEWINNLEITER
# frueher in der sidebar (die ist in streamlit IMMER links) - jetzt rendert die
# funktion einfach dort, wo die hauptsteuerung sie aufruft: in der RECHTEN spalte

def zeige_gewinnleiter(quiz):
    st.write("### Gewinnleiter")
    # von oben nach unten durchgehen (wie im fernsehen)
    # range rückwärts: 14, 13, ... 1, 0
    for i in range(len(quiz.gewinnleiter) - 1, -1, -1):
        betrag = quiz.gewinnleiter[i]  # der geldbetrag an position i
        # sicherheitsstufen sind bei frage 5 und 10 (index 4 und 9)
        sicher = " 🛡" if i in (4, 9) else ""
        if i + 1 == quiz.aktuelle_frage_nummer:
            # aktuelle frage mit pfeil und fett
            st.write(f"➡ **{i+1}. {eur(betrag)}{sicher}**")
        elif i + 1 < quiz.aktuelle_frage_nummer:
            # schon geschafft mit häkchen
            st.write(f"✅ {i+1}. {eur(betrag)}{sicher}")
        else:
            # kommt noch, normal anzeigen
            st.write(f"{i+1}. {eur(betrag)}{sicher}")


# AUSSTEIGEN BUTTON

def zeige_aussteigen(quiz):
    st.write("---")  # trennlinie überm button
    if st.button("Aussteigen und Guthaben sichern"):
        # aussteigen in der logik setzt laeuft = false
        # guthaben bleibt dabei erhalten (das ist ja der sinn)
        quiz.aussteigen()
        st.session_state.runde_beendet = True  # damit rundenende angezeigt wird
        st.session_state.joker_ergebnisse = {}  # joker anzeige weg
        st.rerun()


# RUNDENENDE
def zeige_rundenende(quiz):
    st.header("Runde beendet")
    # millionär check: wenn fragennummer über 15 hast du alle geschafft
    if quiz.aktuelle_frage_nummer > len(quiz.gewinnleiter):
        st.balloons()  # luftballons! eine zeile, eingebaut in streamlit
        st.success("Glückwunsch, du bist Millionär!")  # grüner kasten
    elif quiz.ist_vorbei():
        st.error("Runde vorbei – du hast leider verloren oder bist ausgestiegen.")
    st.write(f"In dieser Runde erspielt: **{eur(quiz.spieler.runden_guthaben)}**")
    # zwei buttons nebeneinander
    spalten = st.columns(2)
    with spalten[0]:
        # type="primary" -> gold, damit der "weiter" button hervorsticht
        if st.button("Neue Runde starten", type="primary", use_container_width=True):
            # rundenguthaben aufs gesamt packen und auf 0 setzen
            quiz.spieler.runde_abschliessen()
            # neue fragen laden (spieler bleibt derselbe mit seinem gesamtguthaben)
            loader = QuestionLoader(FRAGEN_PFAD)
            fragen = loader.lade_fragen()
            # neue joker machen (in neuer runde wieder frisch)
            joker = [
                FiftyFiftyJoker(),
                TelefonJoker("JBL"),
                PublikumsJoker(),
            ]
            # neues quiz objekt mit neuem zeug
            st.session_state.quiz = Quiz(quiz.spieler, fragen, joker)
            # alle anzeige flags zurücksetzen (eine funktion für alles)
            reset_runde_state()
            st.rerun()  # neue runde startet
    with spalten[1]:
        if st.button("Aufhören und in Bestenliste eintragen", use_container_width=True):
            # rundenguthaben aufs gesamt
            quiz.spieler.runde_abschliessen()
            # in die bestenliste json datei schreiben
            st.session_state.bestenliste.speichere(
                quiz.spieler.name,
                quiz.spieler.gesamt_guthaben,
            )
            # quiz auf none = zurück zum startbildschirm
            st.session_state.quiz = None
            # WICHTIG: auch hier alle merker platt machen, sonst hängt die alte frage + crash
            reset_runde_state()
            st.rerun()


# HAUPTSTEUERUNG - DAS IST DER KERN

# hier wird entschieden welcher bildschirm angezeigt wird
if st.session_state.quiz is None:
    # startscreen ohne aktives quiz (mit bestenliste statt sidebar)
    startbildschirm()
else:
    # spiel läuft
    quiz = st.session_state.quiz
    zeige_kopfzeile(quiz)  # name + guthaben IMMER oben sichtbar

    # zwei spalten: links das spiel, rechts die gewinnleiter (wie im tv)
    links, rechts = st.columns([3, 1], gap="large")

    with rechts:
        zeige_gewinnleiter(quiz)  # die leiter kommt immer

    with links:
        # ist die runde vorbei? (ausgestiegen ODER falsch ODER alle 15 geschafft)
        if st.session_state.runde_beendet or quiz.ist_vorbei() or quiz.aktuelle_frage_nummer > len(quiz.gewinnleiter):
            zeige_rundenende(quiz)  # rundenende bildschirm
        else:
            # runde läuft normal -> spiel bildschirm
            frage = hole_aktuelle_frage(quiz)
            if isinstance(frage, str):
                # sicherheitsnetz: wenn keine fragen mehr da sind kriegen wir nen text zurück
                st.warning(frage)
            else:
                # alles normal -> frage anzeigen mit allem drum und dran
                zeige_frage(quiz, frage)
                # waehrend der antwort-animation keine joker/aussteigen buttons zeigen
                # (sonst koennte man mitten in der aufloesung noch klicken)
                if st.session_state.gewaehlte_antwort is None:
                    zeige_joker_ergebnis()
                    zeige_joker(quiz)
                    zeige_telefon_auswahl(quiz)
                    zeige_aussteigen(quiz)
