from abc import ABC, abstractmethod
import random
from frage import Frage

class Joker(ABC):

    def __init__(self) -> None:
        self.benutzt = False

    def ist_benutzt(self) -> bool:
        return self.benutzt

    def markieren_als_benutzt(self) -> None:
        self.benutzt = True

    @abstractmethod
    def anwenden(self, frage: Frage):
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class FiftyFiftyJoker(Joker):

    def anwenden(self, frage: Frage) -> list[str]:

        self.markieren_als_benutzt()

        falsche_antworten = [
            antwort
            for antwort in frage.antworten
            if antwort != frage.richtige_antwort
        ]

        entfernte = random.sample(falsche_antworten, 2)

        verbleibend = [
            antwort
            for antwort in frage.antworten
            if antwort not in entfernte
        ]

        random.shuffle(verbleibend)

        return verbleibend


class TelefonJoker(Joker):

    def __init__(self, person: str) -> None:

        super().__init__()

        self.person = person

    def anwenden(self, frage: Frage) -> str:

        self.markieren_als_benutzt()

        if self.person == "JBL":

            return (
                f'Das ist einfach: '
                f'Es ist "{frage.richtige_antwort}".'
            )

        elif self.person == "Wezon":

            antwort = random.choice(frage.antworten)

            return (
                f'Digga, kein Plan... '
                f'Ich würde "{antwort}" nehmen.'
            )

        elif self.person == "Drabi":

            return "Die Antwort ist trivial."

        raise ValueError("Unbekannte Person.")


class PublikumsJoker(Joker):

    def anwenden(self, frage: Frage) -> dict[str, int]:

        self.markieren_als_benutzt()

        richtige_prozent = random.randint(55, 80)

        rest = 100 - richtige_prozent

        a = random.randint(0, rest)
        b = random.randint(0, rest - a)
        c = rest - a - b

        falsche = [a, b, c]
        random.shuffle(falsche)

        verteilung = {}

        index = 0

        for antwort in frage.antworten:

            if antwort == frage.richtige_antwort:

                verteilung[antwort] = richtige_prozent

            else:

                verteilung[antwort] = falsche[index]
                index += 1

        return verteilung
