import sys 
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "GameLogik"))

import unittest
from spieler import Spieler

class TestSpieler(unittest.TestCase):

    def test_neuer_spieler_hat_kein_guthaben(self):
        spieler = Spieler("Impactrr")
        self.assertEqual(spieler.runden_guthaben, 0)

    def test_spieler_beendet_runde(self):
        spieler = Spieler("Gestern")
        spieler.runden_guthaben = 200
        spieler.gesamt_guthaben = 5000
        spieler.runde_abschliessen()
        self.assertEqual(spieler.gesamt_guthaben, 5200)
        self.assertEqual(spieler.runden_guthaben, 0)
        spieler.runden_guthaben = 100
        spieler.runde_abschliessen()
        self.assertEqual(spieler.gesamt_guthaben, 5300)
        self.assertEqual(spieler.runden_guthaben, 0)






if __name__ == "__main__":
    unittest.main()