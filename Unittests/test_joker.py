import unittest
from GameLogik.joker import FiftyFiftyJoker, TelefonJoker, PublikumsJoker
from GameLogik.frage import Frage
from GameLogik.difficulty import Difficulty


class TestJoker(unittest.TestCase):

    def setUp(self):
        self.frage = Frage(
            text="Hauptstadt?",
            antworten=["Berlin", "Paris", "Rom", "Madrid"],
            richtige_antwort="Berlin",
            schwierigkeit=Difficulty.EINFACH
        )

    def test_joker_initial_unbenutzt(self):
        joker = FiftyFiftyJoker()
        self.assertFalse(joker.ist_benutzt())

    def test_joker_markieren(self):
        joker = FiftyFiftyJoker()
        joker.markieren_als_benutzt()
        self.assertTrue(joker.ist_benutzt())

    def test_str(self):
        self.assertEqual(str(FiftyFiftyJoker()), "FiftyFiftyJoker")

    def test_fifty_fifty(self):
        ergebnis = FiftyFiftyJoker().anwenden(self.frage)
        self.assertEqual(len(ergebnis), 2)
        self.assertIn(self.frage.richtige_antwort, ergebnis)

    def test_telefon_jbl(self):
        self.assertIn("Berlin", TelefonJoker("JBL").anwenden(self.frage))

    def test_telefon_wezon(self):
        text = TelefonJoker("Wezon").anwenden(self.frage)
        self.assertTrue(any(a in text for a in self.frage.antworten))

    def test_telefon_drabi(self):
        self.assertEqual(TelefonJoker("Drabi").anwenden(self.frage),
                         "Die Antwort ist trivial.")

    def test_telefon_fehler(self):
        with self.assertRaises(ValueError):
            TelefonJoker("XYZ").anwenden(self.frage)

    def test_publikum(self):
        verteilung = PublikumsJoker().anwenden(self.frage)
        self.assertEqual(sum(verteilung.values()), 100)
        self.assertGreaterEqual(verteilung["Berlin"], 55)
        self.assertLessEqual(verteilung["Berlin"], 80)


if __name__ == "__main__":
    unittest.main()
