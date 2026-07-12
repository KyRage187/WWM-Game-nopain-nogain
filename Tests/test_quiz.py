import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "GameLogik"))

import unittest
from frage import Frage
from joker import Joker
from spieler import Spieler
from quiz import Quiz
from difficulty import Difficulty

class TestQuiz(unittest.TestCase):
    def test_schwierigkeit_grenze_5_zu_6(self):
        quiz = Quiz(Spieler("Test"), [], [])
        quiz.aktuelle_frage_nummer = 5
        self.assertEqual(quiz.berechne_schwierigkeit(), Difficulty.EINFACH)
        quiz.aktuelle_frage_nummer = 6
        self.assertEqual(quiz.berechne_schwierigkeit(), Difficulty.MITTEL)

    def test_richtige_antwort_gibt_geld(self):
        frage = Frage("Testfrage?", ["A", "B"], "A", Difficulty.EINFACH)
        quiz = Quiz(Spieler("Test"), [frage], [])
        quiz.naechste_frage()
        quiz.antwort_pruefen("A")
        self.assertEqual(quiz.spieler.runden_guthaben, 50)
        self.assertEqual(quiz.aktuelle_frage_nummer, 2)

    def test_naechste_frage_ohne_frage(self):
        quiz = Quiz(Spieler("Test"), [], [])
        ergebnis = quiz.naechste_frage()
        self.assertIsNone(ergebnis)
        self.assertTrue(quiz.ist_vorbei(), True)

    def test_falsch_auf_erster_sicherheitsstufe(self):
        frage = Frage("?", ["A", "B"], "A", Difficulty.MITTEL)
        quiz = Quiz(Spieler("Test"), [frage], [])
        quiz.aktuelle_frage_nummer = 6
        quiz.aktuelle_frage = frage
        quiz.antwort_pruefen("B")
        self.assertEqual(quiz.spieler.runden_guthaben, 500)

    def test_antwort_pruefen_nach_der_letzten_frage(self):
        frage = Frage("?", ["A", "B"], "A", Difficulty.MITTEL)
        quiz = Quiz(Spieler("Test"), [frage], [])
        quiz.aktuelle_frage_nummer = 16
        quiz.laeuft = False
        quiz.antwort_pruefen("A")
        self.assertEqual(quiz.spieler.runden_guthaben, 0)



    

if __name__ == "__main__":
    unittest.main()