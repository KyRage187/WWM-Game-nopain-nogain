class Spieler:
    """
    Repräsentiert den Spieler mit seinem Namen und Guthaben.

    Es gibt zwei Guthaben-Werte:
    - runden_guthaben: was in der aktuellen Quiz Runde gewonnen wurde
    - gesamt_guthaben: die Summe über alle bereits abgeschlossenen Runden.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.runden_guthaben = 0
        self.gesamt_guthaben = 0

    def setze_runden_guthaben(self, betrag: int) -> None:
        """
        Setzt das Guthaben der aktuellen Runde auf den gewonnenen Betrag
        """
        self.runden_guthaben = betrag

    def runde_abschliessen(self) -> None:
        """
        Übernimmt das Runden Guthaben ins Gesamt Guthaben und setzt
        das Runden Guthaben danach auf 0 zurück.
        """
        self.gesamt_guthaben += self.runden_guthaben
        self.runden_guthaben = 0
