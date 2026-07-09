#import der klassen
#imports??? gamelogik 

import streamlit as st 
from gamelogik; import Quiz 
from gamelogik; import Spieler 
from fragen_datenbank; import QuestionLoad
from highscore import Highscore
from joker import FiftyFiftyJoker, TelefonJoker, PublikumsJoker

# skelett der app
st.set_page_config(page_title="Wer wird Millionär?", page_icon=":moneybag:", layout="centered")
Fragen_pfad="fragen_datenbank/fragen.json"
highscore_pfad="highscore/highscore.json"
TelefonJokerNamem = ["JBL", "Drabi", "Wezon"]

#sessionstate
#ist bis jetz nur prototyp 

if "quiz" not in st.session.state:
    st.session_state.quiz = None

if "highscore" not in st.session_state:
    st.session_state.highscore = Highscore(highscore_pfad)

if "joker_einsetzen" not in st.session_state:
    st.session_state.joker_einsetzen = None

if "telefon_auswahl_aktiv" not in st.session_state:#???
    st.session_state.telefon_auswahl_aktiv = False

if "ist_vorbei" not in st.session_state:
    st.session_state.ist_vorbei = False

#startbildschirm

