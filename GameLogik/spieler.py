class Spieler:
    def __init__(self, name: str) -> None:
        self.name = name
        self.runden_guthaben = 0
        self.gesamt_guthaben = 0

    def setze_runden_guthaben(self, betrag: int) -> None:
       self.runden_guthaben = betrag
    

    
    def runde_abschliessen(self) -> None:
        self.gesamt_guthaben += self.runden_guthaben
        self.runden_guthaben = 0
