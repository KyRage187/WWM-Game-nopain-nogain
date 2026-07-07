class Spieler:
    def __init__(self, name):
        self.name = name
        self.runden_guthaben = 0
        self.gesamt_guthaben = 0

    def setze_runden_guthaben(self, betrag):
       self.runden_guthaben = betrag
    

    
    def runde_abschliessen(self):
        self.gesamt_guthaben += self.runden_guthaben
        self.runden_guthaben = 0
