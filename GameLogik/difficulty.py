from enum import Enum

class Difficulty(Enum):
    """
    Schwierigkeitsgrade einer Frage. Der Zahlenwert wird aktuell nicht
    für Berechnungen genutzt, nur der Name (EINFACH/MITTEL/SCHWER) zum
    Vergleichen und Filtern der Fragen.
    """
    EINFACH = 1
    MITTEL = 2
    SCHWER = 3