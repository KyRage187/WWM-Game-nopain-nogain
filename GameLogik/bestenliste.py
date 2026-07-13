import json
import os


class Bestenliste:
    """Verwaltet die Bestenliste des Spiels."""
    def __init__(self, dateipfad: str = "bestenliste.json") -> None:
        """Initialisiert die Bestenliste und legt die Datei bei Bedarf an."""
        self.dateipfad = dateipfad
        if not os.path.exists(self.dateipfad):
            with open(self.dateipfad, "w", encoding="utf-8") as datei:
                json.dump([], datei, indent=4)

    def lade_bestenliste(self) -> list[dict]:
        try:    
            """Lädt alle Einträge aus der JSON-Datei."""
            with open(self.dateipfad, "r", encoding="utf-8") as datei:
                return json.load(datei)
        except json.JSONDecodeError:
            return []


    def speichere(self, name: str, gesamt_guthaben: int) -> None:
        """Speichert oder aktualisiert den Eintrag eines Spielers."""
        bestenliste = self.lade_bestenliste()
        spieler = None
        # Nach vorhandenem Spieler suchen.

        for eintrag in bestenliste:
            if eintrag["name"] == name:
                spieler = eintrag
                break

        if spieler is None:
            # Neuen Spieler anlegen.
            spieler = {"name": name, "gesamt_guthaben": gesamt_guthaben,
                       "millionen": 1 if gesamt_guthaben == 1000000 else 0}
            bestenliste.append(spieler)
        else:
            # Guthaben und Millionengewinne aktualisieren.
            spieler["gesamt_guthaben"] += gesamt_guthaben
            if gesamt_guthaben == 1000000:
                spieler["millionen"] += 1

        # Nach Guthaben absteigend sortieren und speichern.
        bestenliste.sort(key=lambda e: e["gesamt_guthaben"], reverse=True)
        with open(self.dateipfad, "w", encoding="utf-8") as datei:
            json.dump(bestenliste, datei, indent=4, ensure_ascii=False)
