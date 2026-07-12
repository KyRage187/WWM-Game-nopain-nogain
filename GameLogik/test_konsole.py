import json
import glob

from difficulty import Difficulty
from frage import Frage
from spieler import Spieler
from quiz import Quiz


def mach_fragen_pool() -> list[Frage]:
    fragen = []
    for i in range(1, 6):
        fragen.append(Frage(f"Einfache Frage {i}?", ["a", "b"], "a", Difficulty.EINFACH))
    for i in range(1, 6):
        fragen.append(Frage(f"Mittlere Frage {i}?", ["a", "b"], "a", Difficulty.MITTEL))
    for i in range(1, 6):
        fragen.append(Frage(f"Schwere Frage {i}?", ["a", "b"], "a", Difficulty.SCHWER))
    return fragen


# Provisorische Lade-Funktion, NUR zum Testen mit echten Daten.
# Das eigentliche Laden aus JSON ist Aufgabe von QuestionLoader (Person B).
SCHWIERIGKEIT_MAPPING: dict[str, Difficulty] = {
    "leicht": Difficulty.EINFACH,
    "mittel": Difficulty.MITTEL,
    "schwer": Difficulty.SCHWER,
}


def lade_echte_fragen() -> list[Frage]:
    fragen = []
    for pfad in glob.glob("../fragen-datenbank/*.json"):
        with open(pfad, encoding="utf-8") as f:
            daten = json.load(f)
        for eintrag in daten:
            schwierigkeit = SCHWIERIGKEIT_MAPPING[eintrag["schwierigkeit"]]
            richtige_antwort = eintrag["antworten"][eintrag["korrekt"]]
            fragen.append(Frage(eintrag["frage"], eintrag["antworten"], richtige_antwort, schwierigkeit))
    return fragen


print("=== Testlauf 1: Spieler beantwortet alles richtig bis zur Sicherheitsstufe, dann falsch ===")
spieler = Spieler("Khalil")
quiz = Quiz(spieler, mach_fragen_pool(), [])

for nummer in range(1, 8):
    frage = quiz.naechste_frage()
    if nummer < 7:
        quiz.antwort_pruefen("a")  # richtig
        print(f"Frage {nummer} richtig -> Guthaben: {spieler.runden_guthaben}, naechste Schwierigkeit: {quiz.aktuelle_schwierigkeit}")
    else:
        quiz.antwort_pruefen("b")  # falsch
        print(f"Frage {nummer} FALSCH -> Guthaben: {spieler.runden_guthaben} (Sicherheitsstufe), laeuft: {quiz.laeuft}")

print("ist_vorbei():", quiz.ist_vorbei())

print()
print("=== Runde abschliessen und neue Runde starten ===")
quiz.neue_runde()
print("gesamt_guthaben nach Runde 1:", spieler.gesamt_guthaben)
print("frage_nummer nach neue_runde:", quiz.aktuelle_frage_nummer)
print("laeuft nach neue_runde:", quiz.laeuft)

print()
print("=== Testlauf 2: Spieler steigt freiwillig aus ===")
spieler2 = Spieler("Michel")
quiz2 = Quiz(spieler2, mach_fragen_pool(), [])
quiz2.naechste_frage()
quiz2.antwort_pruefen("a")
quiz2.naechste_frage()
quiz2.antwort_pruefen("a")
print("Guthaben vor Ausstieg:", spieler2.runden_guthaben)
quiz2.aussteigen()
print("laeuft nach aussteigen:", quiz2.laeuft, "-> Guthaben behalten:", spieler2.runden_guthaben)

print()
print("=== Testlauf 3: Joker einsetzen ===")


class DemoJoker:
    def __init__(self) -> None:
        self.benutzt = False

    def anwenden(self, frage: Frage) -> str:
        return f"Joker-Tipp zu: {frage.text}"


spieler3 = Spieler("Emil")
quiz3 = Quiz(spieler3, mach_fragen_pool(), [])
quiz3.naechste_frage()
joker = DemoJoker()
print("1. Einsatz:", quiz3.joker_einsetzen(joker))
print("2. Einsatz (schon benutzt):", quiz3.joker_einsetzen(joker))

print()
print("=== Testlauf 4: mit echten Fragen aus der Fragen-Datenbank ===")
spieler4 = Spieler("Testspieler")
quiz4 = Quiz(spieler4, lade_echte_fragen(), [])
print("Fragen insgesamt geladen:", len(quiz4.fragen))

for _ in range(3):
    frage = quiz4.naechste_frage()
    print(f"Frage: {frage}")
    richtig = frage.ist_korrekt(frage.richtige_antwort)
    quiz4.antwort_pruefen(frage.richtige_antwort)
    print(f"  -> richtig beantwortet, Guthaben: {spieler4.runden_guthaben}")
