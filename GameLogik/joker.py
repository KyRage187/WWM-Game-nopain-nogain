from abc import ABC, abstractmethod
import random
from frage import Frage


class Joker(ABC):
    """Abstrakte Basisklasse für alle Joker."""

    def __init__(self) -> None:
        """Initialisiert einen neuen Joker als unbenutzt."""
        # Speichert, ob der Joker bereits eingesetzt wurde.
        self.benutzt = False

    def ist_benutzt(self) -> bool:
        """Gibt zurück, ob der Joker bereits verwendet wurde."""
        return self.benutzt

    def markieren_als_benutzt(self) -> None:
        """Markiert den Joker als benutzt."""
        self.benutzt = True

    @abstractmethod
    def anwenden(self, frage: Frage):
        """Führt die Funktion des Jokers für die angegebene Frage aus."""
        pass

    def __str__(self) -> str:
        """Gibt den Klassennamen des Jokers zurück."""
        return self.__class__.__name__


class FiftyFiftyJoker(Joker):
    """Entfernt zufällig zwei falsche Antworten."""

    def anwenden(self, frage: Frage) -> list[str]:
        """Liefert die richtige und eine zufällige falsche Antwort."""
        # Alle falschen Antworten bestimmen.
        falsche_antworten = [a for a in frage.antworten if a != frage.richtige_antwort]
        # Zwei falsche Antworten entfernen.
        entfernte = random.sample(falsche_antworten, 2)
        # Verbleibende Antworten zusammenstellen und mischen.
        verbleibend = [a for a in frage.antworten if a not in entfernte]
        random.shuffle(verbleibend)
        return verbleibend


class TelefonJoker(Joker):
    """Simuliert den Telefonjoker."""

    def __init__(self, person: str) -> None:
        """Speichert die ausgewählte Kontaktperson."""
        super().__init__()
        self.person = person

    def anwenden(self, frage: Frage) -> str:
        """Gibt abhängig von der Person einen Hinweis zurück."""
        if self.person == "JBL":
            return f'Das ist einfach: Es ist "{frage.richtige_antwort}".'
        elif self.person == "Wezon":
            antwort = random.choice(frage.antworten)
            return f'Digga, kein Plan... Ich würde "{antwort}" nehmen.'
        elif self.person == "Drabi":
            return "Die Antwort ist trivial."
        raise ValueError("Unbekannte Person.")


class PublikumsJoker(Joker):
    """Simuliert die Stimmenverteilung des Publikums."""

    def anwenden(self, frage: Frage) -> dict[str, int]:
        """Erstellt eine zufällige prozentuale Abstimmung."""
        # Berechnet die Prozentwerte zufallsbasiert
        richtige_prozent = random.randint(55, 80)
        rest = 100 - richtige_prozent
        a = random.randint(0, rest)
        b = random.randint(0, rest - a)
        c = rest - a - b
        falsche = [a, b, c]
        random.shuffle(falsche)
        verteilung = {}
        index = 0

        # Richtige Antwort erhält die Mehrheit, die restlichen Stimmen werden verteilt.
        for antwort in frage.antworten:
            if antwort == frage.richtige_antwort:
                verteilung[antwort] = richtige_prozent
            else:
                verteilung[antwort] = falsche[index]
                index += 1
        return verteilung
