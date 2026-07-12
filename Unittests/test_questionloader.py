import json
import os
import shutil
import tempfile
import unittest
import sys

from pathlib import Path
# Pfad zum Ordner "GameLogik" hinzufügen.
BASIS_PFAD = Path(__file__).parent.parent
sys.path.append(str(BASIS_PFAD / "GameLogik"))

from questionloader import QuestionLoader
from difficulty import Difficulty
from frage import Frage


class TestQuestionLoader(unittest.TestCase):

    def setUp(self):
        self.ordner = tempfile.mkdtemp()
        daten = []
        for s in ["leicht", "mittel", "schwer"]:
            for i in range(5):
                daten.append({
                    "frage": f"{s}{i}",
                    "antworten": ["A", "B", "C", "D"],
                    "korrekt": 0,
                    "schwierigkeit": s
                })
        with open(os.path.join(self.ordner, "fragen.json"), "w", encoding="utf-8") as f:
            json.dump(daten, f)

    def tearDown(self):
        shutil.rmtree(self.ordner)

    def test_lade_fragen(self):
        loader = QuestionLoader(self.ordner)
        fragen = loader.lade_fragen()
        self.assertEqual(len(fragen), 15)

    def test_filter(self):
        fragen = [
            Frage("x", ["A"], "A", Difficulty.EINFACH),
            Frage("y", ["A"], "A", Difficulty.SCHWER)
        ]
        erg = QuestionLoader.fragen_nach_schwierigkeit(fragen, Difficulty.EINFACH)
        self.assertEqual(len(erg), 1)
        self.assertEqual(erg[0].schwierigkeit, Difficulty.EINFACH)


if __name__ == "__main__":
    unittest.main()
