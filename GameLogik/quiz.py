from difficulty import Difficulty
from frage import Frage
from spieler import Spieler
from joker import Joker

class Quiz:
    """
    Steuert den Ablauf einer WWM-Runde: aktuelle Frage, Schwierigkeit,
    Guthaben und wann die Runde vorbei ist.
    """

    def __init__(self, spieler: Spieler, fragen: list[Frage], joker: list[Joker]) -> None:
        self.spieler = spieler
        self.fragen = fragen
        self.joker = joker
        # Gewinnleiter: Index 0 = Betrag für Frage 1, Index 14 = Betrag für Frage 15 (1 Mio.)
        self.gewinnleiter = [50, 100, 200, 300, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 500000, 1000000]
        self.aktuelle_frage_nummer = 1
        self.aktuelle_schwierigkeit = self.berechne_schwierigkeit()
        self.aktuelle_frage = None
        self.laeuft = True


    def berechne_schwierigkeit(self) -> Difficulty:
        """
        Leitet den Schwierigkeitsgrad aus der Fragennummer ab
        (1-5 = EINFACH, 6-10 = MITTEL, 11-15 = SCHWER).
        """
        if self.aktuelle_frage_nummer <=5:
            Schwierigkeit = Difficulty.EINFACH

        elif self.aktuelle_frage_nummer >5 and self.aktuelle_frage_nummer <= 10:
            Schwierigkeit = Difficulty.MITTEL

        else:
            Schwierigkeit = Difficulty.SCHWER

        return Schwierigkeit

    def naechste_frage(self) -> Frage | None:
        """
        Holt die nächste passende Frage aus dem Pool und entfernt sie daraus.
        Gibt es keine mehr, wird die Runde beendet und None zurückgegeben.
        """
        for frage in self.fragen:
            if  frage.schwierigkeit == self.aktuelle_schwierigkeit:
                self.aktuelle_frage = frage
                self.fragen.remove(frage)
                return frage

        self.laeuft = False
        return None

    def antwort_pruefen(self, antwort: str) -> None:
        """
        Prüft die Antwort auf die aktuelle Frage: bei richtig steigt das
        Guthaben und es geht weiter, bei falsch fällt das Guthaben auf
        die letzte Sicherheitsstufe zurück und die Runde endet.
        """

        if not self.laeuft:
            return

        if self.aktuelle_frage.ist_korrekt(antwort):
            self.spieler.setze_runden_guthaben(self.gewinnleiter[self.aktuelle_frage_nummer - 1])
            self.aktuelle_frage_nummer += 1

            if self.aktuelle_frage_nummer == 16:
                self.laeuft = False

            self.aktuelle_schwierigkeit = self.berechne_schwierigkeit()

        else:

            if self.aktuelle_frage_nummer > 10:
               self.spieler.setze_runden_guthaben(self.gewinnleiter[10-1])
               self.laeuft = False

            elif self.aktuelle_frage_nummer > 5:
               self.spieler.setze_runden_guthaben(self.gewinnleiter[5-1])
               self.laeuft = False

            else:
               self.spieler.setze_runden_guthaben(0)
               self.laeuft = False

    def aussteigen(self) -> None:
        """
        Spieler steigt freiwillig aus, Spieler bekommt das aktuelle Runden Guthaben gutgeschrieben.
        """
        self.laeuft = False

    def ist_vorbei(self) -> bool:
        """
        Gibt True zurück, sobald die Runde nicht mehr läuft.
        """
        if self.laeuft == True:
            return False
        else:
            return True

    def neue_runde(self) -> None:
        """
        Schließt die Runde beim Spieler ab und setzt den Quiz Zustand
        für eine neue Runde zurück.
        """
        self.spieler.runde_abschliessen()
        self.aktuelle_frage_nummer = 1
        self.aktuelle_schwierigkeit = self.berechne_schwierigkeit()
        self.laeuft = True

    def joker_einsetzen(self, joker: Joker) -> list[str] | str | dict[str, int] | None:
        """
        Setzt einen Joker auf die aktuelle Frage an, sofern er noch nicht
        benutzt wurde, und gibt das Ergebnis des Jokers zurück.
        """
        if joker.benutzt:
            return None

        joker.markieren_als_benutzt()

        joker_antwort = joker.anwenden(self.aktuelle_frage)

        return joker_antwort
    


