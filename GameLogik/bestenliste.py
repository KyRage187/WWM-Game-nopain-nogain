import json
import os


class Bestenliste:

    def __init__(self, dateipfad="bestenliste.json"):
        self.dateipfad = dateipfad

        if not os.path.exists(self.dateipfad):
            with open(self.dateipfad, "w", encoding="utf-8") as datei:
                json.dump([], datei, indent=4)

    def lade_bestenliste(self):

        with open(self.dateipfad, "r", encoding="utf-8") as datei:
            return json.load(datei)

    def speichere(self, name, gesamt_guthaben):

        bestenliste = self.lade_bestenliste()

        spieler = None

        for eintrag in bestenliste:
            if eintrag["name"] == name:
                spieler = eintrag
                break

        if spieler is None:

            spieler = {
                "name": name,
                "gesamt_guthaben": gesamt_guthaben,
                "millionen": 1 if gesamt_guthaben == 1000000 else 0
            }

            bestenliste.append(spieler)

        else:

            if gesamt_guthaben > spieler["gesamt_guthaben"]:
                spieler["gesamt_guthaben"] = gesamt_guthaben

            if gesamt_guthaben == 1000000:
                spieler["millionen"] += 1

        bestenliste.sort(
            key=lambda spieler_eintrag: spieler_eintrag["gesamt_guthaben"],
            reverse=True
        )

        with open(self.dateipfad, "w", encoding="utf-8") as datei:
            json.dump(
                bestenliste,
                datei,
                indent=4,
                ensure_ascii=False
            )
