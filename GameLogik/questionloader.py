import glob
import json
import random

from difficulty import Difficulty
from frage import Frage


class QuestionLoader:

    SCHWIERIGKEIT_MAPPING = {
        "leicht": Difficulty.EINFACH,
        "mittel": Difficulty.MITTEL,
        "schwer": Difficulty.SCHWER
    }

    def __init__(self, ordnerpfad):
        self.dateipfad = ordnerpfad

    def lade_fragen(self):

        alle_fragen = []

        # Alle JSON-Dateien des Ordners einlesen
        for pfad in glob.glob(f"{self.dateipfad}/*.json"):

            with open(pfad, encoding="utf-8") as datei:
                daten = json.load(datei)

            for eintrag in daten:

                schwierigkeit = self.SCHWIERIGKEIT_MAPPING.get(
                    eintrag["schwierigkeit"]
                )

                if schwierigkeit is None:
                    raise ValueError(
                        f'Ungültige Schwierigkeit "{eintrag["schwierigkeit"]}" in {pfad}'
                    )

                frage = Frage(
                    text=eintrag["frage"],
                    antworten=eintrag["antworten"],
                    richtige_antwort=eintrag["antworten"][eintrag["korrekt"]],
                    schwierigkeit=schwierigkeit
                )

                alle_fragen.append(frage)

        # Fragen nach Schwierigkeit aufteilen
        einfache_fragen = self.fragen_nach_schwierigkeit(
            alle_fragen,
            Difficulty.EINFACH
        )

        mittlere_fragen = self.fragen_nach_schwierigkeit(
            alle_fragen,
            Difficulty.MITTEL
        )

        schwere_fragen = self.fragen_nach_schwierigkeit(
            alle_fragen,
            Difficulty.SCHWER
        )

        # Prüfen, ob genügend Fragen vorhanden sind
        if len(einfache_fragen) < 5:
            raise ValueError(
                "Es müssen mindestens 5 einfache Fragen vorhanden sein."
            )

        if len(mittlere_fragen) < 5:
            raise ValueError(
                "Es müssen mindestens 5 mittlere Fragen vorhanden sein."
            )

        if len(schwere_fragen) < 5:
            raise ValueError(
                "Es müssen mindestens 5 schwere Fragen vorhanden sein."
            )

        # Jeweils zufällig fünf auswählen
        quiz_fragen = []

        quiz_fragen.extend(random.sample(einfache_fragen, 5))
        quiz_fragen.extend(random.sample(mittlere_fragen, 5))
        quiz_fragen.extend(random.sample(schwere_fragen, 5))

        return quiz_fragen

    @staticmethod
    def fragen_nach_schwierigkeit(fragen, stufe):

        passende_fragen = []

        for frage in fragen:
            if frage.schwierigkeit == stufe:
                passende_fragen.append(frage)

        return passende_fragen
