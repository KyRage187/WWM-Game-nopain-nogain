import tempfile
import os
import unittest

from GameLogik.bestenliste import Bestenliste


class TestBestenliste(unittest.TestCase):

    def setUp(self):
        self.datei = tempfile.NamedTemporaryFile(delete=False)
        self.datei.close()
        os.unlink(self.datei.name)
        self.b = Bestenliste(self.datei.name)

    def tearDown(self):
        if os.path.exists(self.datei.name):
            os.remove(self.datei.name)

    def test_datei_existiert(self):
        self.assertTrue(os.path.exists(self.datei.name))

    def test_neuer_spieler(self):
        self.b.speichere("Max", 1000)
        daten = self.b.lade_bestenliste()
        self.assertEqual(len(daten), 1)
        self.assertEqual(daten[0]["name"], "Max")

    def test_hoechstwert(self):
        self.b.speichere("Max", 1000)
        self.b.speichere("Max", 500)
        self.assertEqual(self.b.lade_bestenliste()[0]["gesamt_guthaben"], 1000)

    def test_million(self):
        self.b.speichere("Max", 1000000)
        self.assertEqual(self.b.lade_bestenliste()[0]["millionen"], 1)

    def test_sortierung(self):
        self.b.speichere("A", 100)
        self.b.speichere("B", 200)
        daten = self.b.lade_bestenliste()
        self.assertEqual(daten[0]["name"], "B")


if __name__ == "__main__":
    unittest.main()
