from difficulty import Difficulty
from frage import Frage
from spieler import Spieler
from joker import Joker

class Quiz:
    def __init__(self, spieler: Spieler, fragen: list[Frage], joker: list[Joker]) -> None:
        self.spieler = spieler
        self.fragen = fragen
        self.joker = joker
        self.gewinnleiter = [50, 100, 200, 300, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 500000, 1000000]
        self.aktuelle_frage_nummer = 1
        self.aktuelle_schwierigkeit = self.berechne_schwierigkeit()
        self.aktuelle_frage = None
        self.laeuft = True
    
    
    def berechne_schwierigkeit(self) -> Difficulty:
        if self.aktuelle_frage_nummer <=5:
            Schwierigkeit = Difficulty.EINFACH

        elif self.aktuelle_frage_nummer >5 and self.aktuelle_frage_nummer <= 10:
            Schwierigkeit = Difficulty.MITTEL
        
        else: 
            Schwierigkeit = Difficulty.SCHWER
        
        return Schwierigkeit
    
    def naechste_frage(self) -> Frage | str:
        for frage in self.fragen:
            if  frage.schwierigkeit == self.aktuelle_schwierigkeit:
                self.aktuelle_frage = frage
                self.fragen.remove(frage)
                return frage
        
        return "Keine Fragen vorhanden"
    
    def antwort_pruefen(self, antwort: str) -> None:
        if self.aktuelle_frage.ist_korrekt(antwort):
            self.spieler.setze_runden_guthaben(self.gewinnleiter[self.aktuelle_frage_nummer - 1])
            self.aktuelle_frage_nummer += 1
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
        self.laeuft = False

    def ist_vorbei(self) -> bool:
        if self.laeuft == True:
            return False
        else:
            return True
        
    def neue_runde(self) -> None:
        self.spieler.runde_abschliessen()
        self.aktuelle_frage_nummer = 1
        self.aktuelle_schwierigkeit = self.berechne_schwierigkeit()
        self.laeuft = True

    def joker_einsetzen(self, joker: Joker) -> list[str] | str | dict[str, int] | None:
        if joker.benutzt:
            return None

        joker.markieren_als_benutzt()
        
        joker_antwort = joker.anwenden(self.aktuelle_frage)

        return joker_antwort
    


