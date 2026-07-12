import glob
import json
import random
from GameLogik.difficulty import Difficulty
from GameLogik.frage import Frage


class QuestionLoader:

    """Lädt Fragen aus JSON-Dateien."""
    SCHWIERIGKEIT_MAPPING = {"leicht": Difficulty.EINFACH, "mittel": Difficulty.MITTEL, "schwer": Difficulty.SCHWER}

    def __init__(self, ordnerpfad: str) -> None:
        """Speichert den Pfad zum Fragenordner."""
        self.dateipfad = ordnerpfad

    def lade_fragen(self) -> list[Frage]:
        """Lädt alle Fragen und wählt fünf je Schwierigkeitsgrad aus."""
        alle_fragen = []
        # Alle JSON-Dateien des Ordners einlesen.
        for pfad in glob.glob(f"{self.dateipfad}/*.json"):
            with open(pfad, encoding="utf-8") as datei:
                daten = json.load(datei)

            for eintrag in daten:
                schwierigkeit = self.SCHWIERIGKEIT_MAPPING.get(eintrag["schwierigkeit"])
                if schwierigkeit is None:
                    raise ValueError(f'Ungültige Schwierigkeit "{eintrag["schwierigkeit"]}" in {pfad}')
                alle_fragen.append(Frage(text=eintrag["frage"], antworten=eintrag["antworten"],
                                         richtige_antwort=eintrag["antworten"][eintrag["korrekt"]],
                                         schwierigkeit=schwierigkeit))

        einfache = self.fragen_nach_schwierigkeit(alle_fragen, Difficulty.EINFACH)
        mittlere = self.fragen_nach_schwierigkeit(alle_fragen, Difficulty.MITTEL)
        schwere = self.fragen_nach_schwierigkeit(alle_fragen, Difficulty.SCHWER)

        # Sicherstellen, dass genügend Fragen vorhanden sind.
        if len(einfache) < 5 or len(mittlere) < 5 or len(schwere) < 5:
            raise ValueError("Für jede Schwierigkeit müssen mindestens fünf Fragen vorhanden sein.")
        quiz = []
        quiz.extend(random.sample(einfache, 5))
        quiz.extend(random.sample(mittlere, 5))
        quiz.extend(random.sample(schwere, 5))
        return quiz

    @staticmethod
    def fragen_nach_schwierigkeit(fragen: list[Frage], stufe: Difficulty) -> list[Frage]:
        """Filtert Fragen nach der gewünschten Schwierigkeit."""
        passende = []

        # Nur Fragen der angegebenen Schwierigkeit übernehmen.
        for frage in fragen:
            if frage.schwierigkeit == stufe:
                passende.append(frage)
        return passende
