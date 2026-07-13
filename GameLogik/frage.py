from difficulty import Difficulty


class Frage:
    """
    Eine einzelne Quiz Frage mit Text, den vier Antwortmöglichkeiten,
    der richtigen Antwort und dem Schwierigkeitsgrad.
    """

    def __init__(self, text: str, antworten: list[str], richtige_antwort: str, schwierigkeit: Difficulty) -> None:
        self.text = text
        self.antworten = antworten
        self.richtige_antwort = richtige_antwort
        self.schwierigkeit = schwierigkeit

    def ist_korrekt(self, antwort: str) -> bool:
        """Prüft, ob die übergebene Antwort mit der richtigen Antwort übereinstimmt."""
        return antwort == self.richtige_antwort

    def __str__(self) -> str:
        """Text-Darstellung der Frage inkl. Schwierigkeitsgrad, z. B. für Debug-Ausgaben."""
        return f"{self.text} ({self.schwierigkeit.name})"
    