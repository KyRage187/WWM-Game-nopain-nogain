#streamlit run Streamlitt/irgendeindtname_test1.py
# imports - alles was wir brauchen

import html  # zum escapen von texten die wir in eigenes html stecken (sonst koennte ein spielername mit <b> o.ae. unser layout kaputt machen)
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
# layout="wide" statt "centered" -> wir brauchen die breite fuer die gewinnleiter RECHTS
st.set_page_config(page_title="Wer wird Millionär?", page_icon=":moneybag:", layout="wide")

# die pfade zu unseren dateien
FRAGEN_PFAD = str(BASIS_PFAD / "FragenDatenbank")  # ordner mit den json fragen
BESTENLISTE_PFAD = str(BASIS_PFAD / "bestenliste.json")  # wo die highscores gespeichert werden
TELEFON_PERSONEN = ["JBL", "Drabi", "Wezon"]  # die drei fürs telefon

# schoene anzeige-namen fuer die joker buttons
# WICHTIG: das ist NUR das label! die keys der buttons benutzen weiter str(joker),
# dadurch bleibt die ganze logik unveraendert
JOKER_LABELS = {
    "FiftyFiftyJoker": "50:50",
    "TelefonJoker": "📞 Telefon",
    "PublikumsJoker": "👥 Publikum",
}


# DESIGN (CSS) - HIER PASSIERT DIE GANZE OPTIK
#
# streamlit kann man mit st.markdown + unsafe_allow_html=True eigenes css unterjubeln.
# unsafe_allow_html heisst nur: "streamlit, vertrau mir, ich weiss was ich tue" -
# deswegen escapen wir ueberall wo NUTZER-texte in unser html wandern (html.escape).
# die farben passen zum theme in .streamlit/config.toml (gold + nachtblau).

WWM_CSS = """
<style>
/* schrift fuer titel + betraege: cinzel = gold-gravur-look wie im tv.
   kommt von google fonts, ohne internet faellt sie auf georgia (serifen) zurueck */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&display=swap');

/* unsere farb-variablen, damit wir nicht 20x den hexcode tippen */
:root {
    --nachtblau: #03082B;
    --kartenblau: #0A1A4F;
    --gold: #F5B942;
    --goldhell: #FFE9B8;
    --textweiss: #F2F4FF;
    --linienblau: #22377A;
}

/* streamlits eigene kopfleiste durchsichtig machen + menue/deploy-button/footer weg -> wirkt wie eine echte app */
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stAppDeployButton"] { display: none; }

/* seite nicht endlos breit werden lassen (layout="wide" waere sonst ZU wide) */
.block-container { max-width: 1200px; padding-top: 1.2rem; }

/* studio-hintergrund: dunkelblau mit "scheinwerfer" von oben (radialer verlauf) */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 50% -10%, #12277A 0%, var(--nachtblau) 55%) fixed;
}

/* ---------- DER GROSSE GOLD-SCHRIFTZUG ---------- */
/* trick: gold-verlauf als hintergrund und dann per background-clip auf den text zuschneiden */
.wwm-logo, .wwm-hero-titel {
    font-family: 'Cinzel', Georgia, serif;
    font-weight: 800;
    letter-spacing: .06em;
    background: linear-gradient(180deg, var(--goldhell), var(--gold) 55%, #B97E14);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    filter: drop-shadow(0 2px 10px rgba(245, 185, 66, .25));
}
.wwm-logo { font-size: 1.5rem; line-height: 1.15; }
.wwm-hero { text-align: center; padding: 2rem 0 .8rem; animation: einblenden .6s ease both; }
.wwm-hero-titel { font-size: 3.2rem; line-height: 1.1; }
.wwm-hero-unter { color: #AAB8E8; margin-top: .7rem; font-size: 1.1rem; }

/* kleine goldene abschnitts-ueberschriften (z.b. "bestenliste", "joker") */
.abschnitt-titel {
    font-family: 'Cinzel', Georgia, serif;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: 1rem;
    margin: 1.4rem 0 .3rem;
}

/* ---------- FRAGE ---------- */
.frage-kopf {
    /* absichtlich NICHT cinzel: deren "1" sieht aus wie ein "I" -> "frage 1" waere verwirrend */
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: .08em;
    font-size: .95rem;
    margin-bottom: .4rem;
}
/* die blaue frage-box mit gold-kante links, blendet sich bei jeder neuen frage ein */
.frage-box {
    background: linear-gradient(180deg, #10256E, #081540);
    border: 1px solid var(--linienblau);
    border-left: 4px solid var(--gold);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: .9rem;
    animation: einblenden .45s ease both;
}
@keyframes einblenden {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: none; }
}

/* ---------- BUTTONS ---------- */
/* primary-buttons = unsere ANTWORT-kapseln im tv-stil (dunkelblauer verlauf, pillenform).
   streamlit gibt jedem button ein data-testid, darueber stylen wir gezielt */
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(180deg, #16308F 0%, #0A1A4F 55%, #071238 100%);
    border: 2px solid #33509F;
    border-radius: 999px;              /* 999px = maximale rundung = kapsel */
    color: var(--textweiss);
    font-weight: 600;
    min-height: 3rem;
    transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease;
}
/* der erste buchstabe im label ist unser A/B/C/D -> automatisch gold einfaerben */
button[data-testid="stBaseButton-primary"] p::first-letter {
    color: var(--gold);
    font-weight: 800;
}
/* hover = goldener glow, wie wenn der kandidat drueber nachdenkt */
button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
    border-color: var(--gold);
    box-shadow: 0 0 16px rgba(245, 185, 66, .55);
    transform: translateY(-1px);
}
/* disabled primary = weggestrichene antworten (50:50) ODER "spiel starten" ohne namen -> einfach stark abdunkeln */
button[data-testid="stBaseButton-primary"]:disabled {
    opacity: .3;
}

/* secondary-buttons = joker, aussteigen usw: dunkle pille mit goldschrift */
button[data-testid="stBaseButton-secondary"] {
    background: rgba(10, 26, 79, .65);
    border: 1px solid #2A407E;
    border-radius: 999px;
    color: var(--goldhell);
}
button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {
    border-color: var(--gold);
    box-shadow: 0 0 10px rgba(245, 185, 66, .4);
}
/* benutzte joker: durchgestrichen + blass */
button[data-testid="stBaseButton-secondary"]:disabled {
    opacity: .35;
    text-decoration: line-through;
}

/* ---------- GEWINNLEITER (rechte spalte) ---------- */
.gewinnleiter-karte {
    background: rgba(5, 10, 45, .75);
    border: 1px solid var(--linienblau);
    border-radius: 14px;
    padding: .9rem;
    position: sticky;                  /* bleibt beim scrollen oben kleben */
    top: .5rem;
}
.leiter-titel {
    font-family: 'Cinzel', Georgia, serif;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: .85rem;
    text-align: center;
    margin-bottom: .5rem;
}
.leiter-zeile {
    display: flex;
    gap: .5rem;
    align-items: center;
    padding: .18rem .55rem;
    border-radius: 8px;
    font-size: .92rem;
    font-variant-numeric: tabular-nums;   /* zahlen gleich breit -> betraege stehen sauber untereinander */
}
.leiter-nr { color: #8FA3E8; width: 1.6em; text-align: right; }
.leiter-geld { color: var(--textweiss); font-weight: 600; }
.leiter-schild { margin-left: auto; color: var(--gold); }  /* sicherheitsstufen-schild nach rechts schieben + gold einfaerben */
/* schon geschaffte stufen: blass + haken */
.leiter-zeile.gemacht { opacity: .45; }
.leiter-zeile.gemacht .leiter-geld::after { content: " ✓"; color: #7BD88F; }
/* die AKTUELLE stufe: goldener balken der pulsiert (die eine auffaellige animation der seite) */
.leiter-zeile.aktuell {
    background: linear-gradient(90deg, var(--gold), #C98F1B);
    animation: pulsieren 1.6s ease-in-out infinite;
}
.leiter-zeile.aktuell .leiter-nr,
.leiter-zeile.aktuell .leiter-geld { color: #1B1503; }   /* dunkle schrift auf gold */
@keyframes pulsieren {
    0%, 100% { box-shadow: 0 0 4px rgba(245, 185, 66, .5); }
    50%      { box-shadow: 0 0 18px rgba(245, 185, 66, .95); }
}

/* ---------- KOPFZEILE MIT SPIELER-INFO (st.metric) ---------- */
[data-testid="stMetric"] {
    background: rgba(10, 26, 79, .55);
    border: 1px solid var(--linienblau);
    border-radius: 12px;
    padding: .5rem .8rem;
}
[data-testid="stMetricLabel"] { color: #8FA3E8; }
[data-testid="stMetricValue"] {
    color: var(--goldhell);
    font-family: 'Cinzel', Georgia, serif;
    font-size: 1.3rem;
}

/* ---------- BESTENLISTE (startbildschirm) ---------- */
.besten-tabelle { width: 100%; border-collapse: collapse; margin-top: .4rem; }
.besten-tabelle th {
    text-align: left;
    color: #8FA3E8;
    font-size: .8rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    padding: .35rem .6rem;
    border-bottom: 1px solid var(--linienblau);
}
.besten-tabelle td { padding: .45rem .6rem; border-bottom: 1px solid rgba(34, 55, 122, .5); }
.besten-tabelle td.geld { color: var(--goldhell); font-weight: 600; font-variant-numeric: tabular-nums; }
.besten-tabelle tr:first-child td { font-size: 1.05rem; }   /* platz 1 etwas groesser */

/* infoboxen (st.info usw) etwas runder, passt besser zu den kapseln */
[data-testid="stAlert"] { border-radius: 12px; }

/* wer im betriebssystem "weniger animationen" eingestellt hat, kriegt auch keine */
@media (prefers-reduced-motion: reduce) {
    .frage-box, .wwm-hero, .leiter-zeile.aktuell { animation: none; }
    button[data-testid="stBaseButton-primary"] { transition: none; }
}
</style>
"""


def lade_design():
    # das css oben in die seite injizieren - muss bei JEDEM rerun passieren,
    # weil streamlit die seite ja jedes mal komplett neu aufbaut
    st.markdown(WWM_CSS, unsafe_allow_html=True)


def eur(betrag):
    # macht aus 1000000 -> "1.000.000 €" (deutsche tausenderpunkte)
    # f"{...:,}" macht kommas, die tauschen wir gegen punkte
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


# STARTBILDSCHIRM


def zeige_bestenliste_tabelle():
    # die bestenliste aus der json anzeigen (issue #24) - wir LESEN nur,
    # gespeichert wird weiterhin nur beim "aufhören" button im rundenende
    eintraege = st.session_state.bestenliste.lade_bestenliste()
    st.markdown('<div class="abschnitt-titel">Bestenliste</div>', unsafe_allow_html=True)
    if not eintraege:
        st.caption("Noch keine Einträge — spiel eine Runde und sichere dir Platz 1!")
        return

    medaillen = ["🥇", "🥈", "🥉"]
    zeilen = []
    for platz, eintrag in enumerate(eintraege, start=1):
        # die ersten drei kriegen medaillen, der rest nummern
        rang = medaillen[platz - 1] if platz <= 3 else f"{platz}."
        # html.escape damit ein spielername wie "<h1>lol" nicht unsere seite sprengt
        name = html.escape(str(eintrag["name"]))
        geld = eur(eintrag["gesamt_guthaben"])
        millionen = "💰" * eintrag.get("millionen", 0)  # pro million ein geldsack
        zeilen.append(
            f'<tr><td>{rang}</td><td>{name}</td><td class="geld">{geld}</td><td>{millionen}</td></tr>'
        )

    tabelle = (
        '<table class="besten-tabelle">'
        "<thead><tr><th></th><th>Name</th><th>Guthaben</th><th>Millionen</th></tr></thead>"
        "<tbody>" + "".join(zeilen) + "</tbody></table>"
    )
    st.markdown(tabelle, unsafe_allow_html=True)


def startbildschirm():
    # grosser gold-schriftzug statt st.title - der "hero" der seite
    st.markdown(
        '<div class="wwm-hero">'
        '<div class="wwm-hero-titel">WER WIRD<br>MILLIONÄR?</div>'
        '<div class="wwm-hero-unter">Kommst du durch das Semester? Beantworte 15 Fragen zu unseren Vorlesungen und werde Millionär!</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # eingabe + start mittig in einer schmaleren spalte (sieht aufgeraeumter aus als volle breite)
    aussen = st.columns([1, 2, 1])  # links luft, mitte inhalt, rechts luft
    with aussen[1]:
        # name eingeben
        name = st.text_input("Dein Name:", key="name_input")
        kein_start = name.strip() == ""  # wenn name leer ist kann man nicht starten

        # type="primary" -> kriegt unseren tv-kapsel-look aus dem css
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
    # logo links, daneben die drei wichtigsten infos als st.metric karten - IMMER oben
    spalten = st.columns([1.6, 1, 1, 1])
    with spalten[0]:
        st.markdown('<div class="wwm-logo">WER WIRD<br>MILLIONÄR?</div>', unsafe_allow_html=True)
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
    # kleine goldene zeile drueber + die frage in der blauen box (mit einblend-animation aus dem css)
    st.markdown(
        f'<div class="frage-kopf">Frage {quiz.aktuelle_frage_nummer} um {eur(betrag)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="frage-box">{html.escape(frage.text)}</div>', unsafe_allow_html=True)

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
            # sonst "A: antwort" - das css faerbt den ersten buchstaben gold (::first-letter)
            label = f"{buchstaben[i]}: {antwort}" if not weggestrichen else "—"
            if st.button(
                label,
                key=f"antw_{quiz.aktuelle_frage_nummer}_{i}",  # eindeutiger key für jeden button
                disabled=weggestrichen,  # ausgegraut wenn weggestrichen
                use_container_width=True,
                type="primary",  # primary = tv-kapsel-look (nur optik, aendert nichts am verhalten)
            ):
                # antwort an die logik geben die checkt obs richtig ist und macht guthaben usw
                # WICHTIG: wir geben die ORIGINAL-antwort weiter, nicht das label mit "A:"
                quiz.antwort_pruefen(antwort)
                # joker anzeige zurücksetzen damit sie nicht in die nächste frage klebt
                st.session_state.joker_ergebnisse = {}
                st.session_state.fifty_verbleibende = None
                st.rerun()  # neu laden



# JOKER BUTTONS


def zeige_joker(quiz):
    st.markdown('<div class="abschnitt-titel">Joker</div>', unsafe_allow_html=True)
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
            # die balken sind st.progress -> die farbe kommt automatisch vom theme (GOLD)
            st.write("#### Das Publikum stimmt ab:")
            for antwort, prozent in daten["ergebnis"].items():
                st.progress(prozent / 100, text=f"{antwort}: {prozent} %")  # balken pro antwort

        elif isinstance(joker, TelefonJoker):
            # telefon gibt nen text zurück (je nach person unterschiedlich)
            st.write(f"#### {daten.get('person', '')} sagt:")
            st.info(daten["ergebnis"])  # kasten mit dem spruch


# GEWINNLEITER (rechte spalte)
# frueher war das in der sidebar (immer links) - jetzt bauen wir die leiter als
# eigenes html-kaestchen und die hauptsteuerung setzt sie in die RECHTE spalte.
# die funktion rendert einfach dort, wo sie aufgerufen wird.

def zeige_gewinnleiter(quiz):
    zeilen = []
    # von oben nach unten durchgehen (wie im fernsehen)
    # range rückwärts: 14, 13, ... 1, 0
    for i in range(len(quiz.gewinnleiter) - 1, -1, -1):
        betrag = quiz.gewinnleiter[i]  # der geldbetrag an position i
        # sicherheitsstufen sind bei frage 5 und 10 (index 4 und 9) -> schild-symbol
        schild = '<span class="leiter-schild">🛡</span>' if i in (4, 9) else ""
        # welche css-klasse kriegt die zeile? (die klassen sind oben im css definiert)
        if i + 1 == quiz.aktuelle_frage_nummer:
            klasse = "aktuell"    # goldener pulsierender balken
        elif i + 1 < quiz.aktuelle_frage_nummer:
            klasse = "gemacht"    # blass + haken
        else:
            klasse = "offen"      # normal
        zeilen.append(
            f'<div class="leiter-zeile {klasse}">'
            f'<span class="leiter-nr">{i + 1}</span>'
            f'<span class="leiter-geld">{eur(betrag)}</span>'
            f"{schild}</div>"
        )

    karte = (
        '<div class="gewinnleiter-karte">'
        '<div class="leiter-titel">Gewinnleiter</div>' + "".join(zeilen) + "</div>"
    )
    st.markdown(karte, unsafe_allow_html=True)


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
        st.balloons()  # luftballons! reine deko, einmal pro anzeige
        st.success("Glückwunsch, du bist Millionär!")  # grüner kasten
    elif quiz.ist_vorbei():
        st.error("Runde vorbei – du hast leider verloren oder bist ausgestiegen.")
    st.write(f"In dieser Runde erspielt: **{eur(quiz.spieler.runden_guthaben)}**")
    # zwei buttons nebeneinander
    spalten = st.columns(2)
    with spalten[0]:
        # type="primary" -> der "weiter gehts" button sticht hervor (nur optik)
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

# als allererstes das design laden, damit ALLES danach schon gestylt ist
lade_design()

# hier wird entschieden welcher bildschirm angezeigt wird
if st.session_state.quiz is None:
    # startscreen ohne aktives quiz (keine sidebar mehr - die gewinnleiter
    # gibts erst im spiel, dafuer zeigen wir hier die bestenliste)
    startbildschirm()
else:
    # spiel läuft
    quiz = st.session_state.quiz
    zeige_kopfzeile(quiz)  # name + guthaben IMMER oben sichtbar

    # zwei spalten: links das spiel, rechts die gewinnleiter (wie im tv)
    links, rechts = st.columns([2.6, 1.1], gap="large")

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
                zeige_joker_ergebnis()
                zeige_joker(quiz)
                zeige_telefon_auswahl(quiz)
                zeige_aussteigen(quiz)
