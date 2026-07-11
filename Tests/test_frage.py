import sys 
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "GameLogik"))

import unittest
from frage import Frage
from difficulty import Difficulty

class TestFrage(unittest.TestCase):

    def test_ist_korrekt_bei_richtiger_antwort(self):
        frage = Frage("Wofür steht die O-Notation?",
        ["Asymptotische Laufzeit eines Algorithmus", 
         "Anzahl Programmzeilen", 
         "Speicher einer CPU", 
         "Anzahl Variablen"],
        "Asymptotische Laufzeit eines Algorithmus", 
        Difficulty.EINFACH)
        self.assertTrue(frage.ist_korrekt("Asymptotische Laufzeit eines Algorithmus"), True)

    def test_ist_korrekt_bei_falscher_antwort(self):
        frage = Frage("Wofür steht die O-Notation?",
        ["Asymptotische Laufzeit eines Algorithmus", 
            "Anzahl Programmzeilen", 
            "Speicher einer CPU", 
            "Anzahl Variablen"],
        "Asymptotische Laufzeit eines Algorithmus", 
        Difficulty.EINFACH)
        self.assertFalse( frage.ist_korrekt("Anzahl Variablen"), True)


if __name__ == "__main__":
    unittest.main()