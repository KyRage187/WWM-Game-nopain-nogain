# WWM-GUI: Was wurde gemacht (für Emil)

Version 2 — bewusst **einfach** gehalten: kein eigenes CSS, kein HTML, nur
Standard-Streamlit. Jeder Baustein ist in 1–2 Minuten erklärbar.
Die Spiel-Logik (GameLogik/) ist unverändert.

## Lokal starten (ohne irgendwas zu veröffentlichen)

```
py -m streamlit run Streamlitt/irgendeindtname_test1.py --server.address localhost
```

Läuft nur auf `http://localhost:8501` auf dem eigenen PC. **Aus dem Repo-Root
starten**, sonst findet Streamlit die Theme-Datei nicht.

## Die 6 Bausteine

### 1. Farben: `.streamlit/config.toml` (5 Zeilen, kein CSS!)
Streamlit hat ein eingebautes Theme-System: `backgroundColor` (Dunkelblau),
`primaryColor` (Gold) usw. Streamlit färbt damit automatisch alles Eingebaute —
deshalb sind die Publikums-Balken und die `type="primary"`-Buttons gold,
ohne dass wir irgendwo Farben in den Code schreiben.

### 2. Gewinnleiter rechts: `st.columns` statt Sidebar
Die Sidebar ist in Streamlit immer links. Deshalb: `layout="wide"` in
`st.set_page_config` und in der Hauptsteuerung
`links, rechts = st.columns([3, 1])`. `zeige_gewinnleiter()` ist die gleiche
Funktion wie vorher (gleiche Schleife, gleiche ➡/✅-Logik) — sie wird nur mit
`with rechts:` in die rechte Spalte gesetzt.

### 3. Kopfzeile: `zeige_kopfzeile()` mit `st.metric`
Drei `st.metric`-Karten (Spieler / Runde / Gesamt) neben dem Titel, gerendert
**vor** den Spalten → immer oben sichtbar, kein Scrollen mehr nötig.

### 4. Antwort-Animation (orange → grün/rot) wie im TV
Der Trick: **kein CSS, sondern die eingebauten farbigen Boxen** —
`st.warning` = orange, `st.success` = grün, `st.error` = rot.

Ablauf in `zeige_antwort_feedback()`:
1. Antwort-Klick speichert nur `st.session_state.gewaehlte_antwort` (noch keine Prüfung!)
2. `st.empty()` ist ein Platzhalter, den man mehrfach neu befüllen kann
3. Phase 1: gewählte Antwort als `st.warning` (orange) → `time.sleep(1)`
4. Phase 2: gleiche Stelle neu befüllt — richtige Antwort `st.success` (grün),
   falsche Wahl `st.error` (rot) → `time.sleep(1.5)`
5. Erst **danach** geht die Antwort an `quiz.antwort_pruefen()` — die Logik
   merkt von der ganzen Animation nichts.

Während der Animation werden Joker-/Aussteigen-Buttons nicht gerendert
(ein `if` in der Hauptsteuerung), damit niemand mitten in der Auflösung klickt.

### 5. Bestenliste auf dem Startbildschirm (Issue #24)
`zeige_bestenliste_tabelle()` liest über die vorhandene
`Bestenliste.lade_bestenliste()` und baut eine Liste von Dicts
(Platz/Name/Guthaben/Millionen) — `st.dataframe` macht daraus automatisch
eine Tabelle. Rein lesend, gespeichert wird weiter nur beim "Aufhören"-Button.

### 6. Kleinigkeiten
- `st.balloons()` beim Millionengewinn (eine Zeile, eingebaut)
- Joker-Labels "50:50 / 📞 Telefon / 👥 Publikum" über das `JOKER_LABELS`-Dict —
  nur die Anzeige, die Button-Keys nutzen weiter `str(joker)`
- `eur()`-Helfer: `f"{betrag:,}"` + Komma→Punkt = deutsche Tausenderpunkte
- A/B/C/D-Präfixe in den Antwort-Labels; an `antwort_pruefen()` geht der Original-Text

## Noch offene Befunde (nicht auf diesem Branch gefixt — nur Doku)

- **#20 Rest:** `telefon_auswahl_aktiv` wird beim Beantworten nicht zurückgesetzt →
  offene Telefon-Auswahl kann in die nächste Frage "kleben".
- **#23:** Gespeichert wird nur beim "Aufhören"-Button; Tab zumachen = kein Eintrag.
- **#25:** Nach unserem Test gefixt (durch PR #28) → Issue kann zu.
- **#29 / Testdaten:** `bestenliste.json` liegt im Repo und wird beim Spielen
  beschrieben → Empfehlung: in `.gitignore` aufnehmen.
- **Millionen-Zähler:** zählt nur bei exakt 1.000.000 im übergebenen Betrag.
- **Merge-Achtung:** Khalils Unittest-Branch ändert `naechste_frage()` auf
  `return None` — das Frontend prüft `isinstance(frage, str)`. Beim Merge anpassen.
