from GameLogik.difficulty import Difficulty


class Frage:
    def __init__(self, text: str, antworten: list[str], richtige_antwort: str, schwierigkeit: Difficulty) -> None:
        self.text = text
        self.antworten = antworten
        self.richtige_antwort = richtige_antwort
        self.schwierigkeit = schwierigkeit

    def ist_korrekt(self, antwort: str) -> bool:
        return antwort == self.richtige_antwort

    def __str__(self) -> str:
        return f"{self.text} ({self.schwierigkeit.name})"
    