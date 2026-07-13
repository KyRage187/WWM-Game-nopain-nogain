# WWM-GUI: Was wurde gemacht (für Emil)

Bewusst **einfach** gehalten: Standard-Streamlit plus ein 3-Zeilen-CSS-Block.
Kein Bootstrap — Streamlit bringt sein eigenes Layout-System mit, Bootstrap
würde sich damit beißen und bräuchte einen CDN-Link (Internet-Pflicht).
Die Spiel-Logik (GameLogik/) ist unverändert.

## Lokal starten (ohne irgendwas zu veröffentlichen)

```
py -m streamlit run Streamlitt/irgendeindtname_test1.py --server.address localhost
```

Läuft nur auf `http://localhost:8501` auf dem eigenen PC. **Aus dem Repo-Root
starten**, sonst findet Streamlit die Theme-Datei nicht und die Farben fehlen.

## Die Bausteine

### 1. Farben: `.streamlit/config.toml` (5 Zeilen)
Eingebautes Theme-System: `backgroundColor` (Dunkelblau), `primaryColor` (Gold).
Streamlit färbt damit automatisch Publikums-Balken, `type="primary"`-Buttons usw.

### 2. Gewinnleiter rechts, als eigenes Kästchen
`layout="wide"` + `links, rechts = st.columns([3, 1])` in der Hauptsteuerung.
`st.container(border=True)` zeichnet den Rahmen um die Leiter — dadurch hängt
sie nicht mehr "lose" rum. Die aktuelle Stufe wird mit Streamlits eingebauten
Markdown-Farben markiert: `st.write(":orange[**→ 9. 8.000 €**]")`,
geschaffte Stufen mit `:gray[...]`. Kein CSS nötig.

### 3. Kopfzeile: `st.metric` für Spieler + aktuellen Gewinn
Wird **vor** den Spalten gerendert → immer oben sichtbar. Das Gesamtguthaben
zeigen wir absichtlich nicht mehr an: es wird erst am Rundenende verrechnet
und stand deshalb während des Spiels immer verwirrend auf 0.

### 4. Antwort-Animation (orange → grün/rot) wie im TV
Die Buttons werden **nie ausgetauscht** — sie bleiben exakt stehen und nur
ihre Farbe ändert sich. Der Trick: Streamlit gibt jedem Element mit `key`
automatisch die CSS-Klasse `st-key-<key>`. `faerbe_antwort_button()` injiziert
damit eine Farbregel für genau einen Button; die `transition`-Zeile im
`BASIC_CSS` blendet den Farbwechsel weich über.

Ablauf (Zustandsmaschine über `st.session_state.feedback_phase`):
1. Antwort-Klick speichert nur die Wahl und setzt `feedback_phase = "orange"`
   (noch keine Prüfung!)
2. Rerun: Seite wird komplett normal gezeichnet, dann färbt der Block ganz
   unten in der Hauptsteuerung den gewählten Button orange → `time.sleep(1)`
3. Rerun mit `feedback_phase = "aufloesung"`: richtige Antwort grün, falsche
   Wahl rot → `time.sleep(1.5)` (nach falscher Antwort sieht man also immer,
   was richtig gewesen wäre)
4. Erst danach geht die Antwort an `quiz.antwort_pruefen()` — die Logik merkt
   von der Animation nichts.

Zwei Details: Das Einfärben/Schlafen passiert **ganz am Ende** der
Hauptsteuerung, damit vorher die komplette Seite gezeichnet ist (nichts
verschwindet, nichts springt — Joker und Aussteigen bleiben sichtbar).
Und alle Klick-Handler prüfen `feedback_phase is None`, damit Klicks
während der Animation ignoriert werden.

### 5. Telefon-Joker als echtes Popup: `@st.dialog`
`@st.dialog("Wen möchtest du anrufen?")` über der Funktion macht ein modales
Popup-Fenster. Auswahl einer Person → Joker anwenden → `st.rerun()` schließt es.
Klickt man stattdessen auf das X, ist **nichts** passiert: der Joker ist nicht
verbraucht und nichts bleibt hängen — das fixt nebenbei den Bug, dass die
Telefon-Auswahl über die nächste Frage hinaus offen blieb (Issue #20 Rest).

### 6. Kleinigkeiten
- `st.balloons()` beim Millionengewinn
- Bestenliste auf dem Startbildschirm über `st.dataframe` (rein lesend, Issue #24)
- `eur()`-Helfer für deutsche Tausenderpunkte
- A/B/C/D-Präfixe nur im Label; an `antwort_pruefen()` geht der Original-Text

## Offene Punkte für die Team-Diskussion (nichts davon hier geändert)

- **Publikum + 50:50:** Nutzt man erst 50:50 und dann Publikum, stimmt das
  Publikum auch über die gestrichenen Antworten ab. Im TV stimmt es nur über
  die verbleibenden ab. Bewusste Entscheidung treffen! (Wäre eine Änderung an
  `PublikumsJoker.anwenden()` — Michels Modul, inkl. Unittest-Anpassung.)
- **Millionen-Zähler:** `bestenliste.py` prüft `gesamt_guthaben == 1000000`.
  Wer in Runde 1 500 € sichert und in Runde 2 die Million holt, hört mit
  1.000.500 € auf → Million wird nicht gezählt. Aus dem Gesamtguthaben kann
  man das nicht zuverlässig ablesen — die Info müsste explizit mitgegeben werden.
- **`quiz.py`:** die hartkodierte `16` in `antwort_pruefen` lieber aus der
  Gewinnleiter ableiten, sonst bricht es, wenn die Leiter mal geändert wird.
- **#23:** Gespeichert wird nur beim "Aufhören"-Button; Tab zumachen = kein Eintrag.
- **#29 / Testdaten:** `bestenliste.json` liegt im Repo und wird beim Spielen
  beschrieben → Empfehlung: in `.gitignore` aufnehmen.
