class Frage:
    def __init__(self, text, antworten, richtige_antwort, schwierigkeit):
        self.text = text
        self.antworten = antworten
        self.richtige_antwort = richtige_antwort
        self.schwierigkeit = schwierigkeit

    def ist_korrekt(self, antwort):
        return antwort == self.richtige_antwort

    def __str__(self):
        return f"{self.text} ({self.schwierigkeit.name})"
    