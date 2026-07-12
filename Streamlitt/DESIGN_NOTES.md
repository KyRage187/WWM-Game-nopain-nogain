# WWM-Design: Was wurde gemacht und warum (für Emil)

Dieser Branch (`streamlit-gui-schoener-machen-test`) macht **nur Optik**.
Alle Handler, `st.session_state`-Zugriffe und Aufrufe in die GameLogik sind
1:1 wie auf `main` — vergleiche selbst mit `git diff main -- Streamlitt/`.

## So startest du es lokal (ohne irgendwas zu veröffentlichen)

```
py -m streamlit run Streamlitt/irgendeindtname_test1.py --server.address localhost
```

- Läuft nur auf `http://localhost:8501` auf deinem eigenen PC.
- **Wichtig: aus dem Repo-Root starten**, sonst findet Streamlit die Theme-Datei
  `.streamlit/config.toml` nicht.
- "Öffentlich" wäre erst ein Deployment (z.B. Streamlit Community Cloud) — machen wir nicht.

## Die Design-Bausteine (fürs Erklären in der Präsentation)

### 1. Theme: `.streamlit/config.toml`
Streamlit hat ein eingebautes Theme-System. Die Datei setzt vier Farben
(Nachtblau als Hintergrund, Gold als `primaryColor`) und Streamlit färbt damit
automatisch alles Eingebaute: Fokus-Rahmen, Progress-Balken (Publikumsjoker!),
Eingabefelder. Deshalb sind die Publikums-Balken gold, ohne dass wir sie anfassen.

### 2. Eigenes CSS: der `WWM_CSS`-Block + `lade_design()`
Streamlit kann man mit `st.markdown(css, unsafe_allow_html=True)` eigenes CSS
unterjubeln. `lade_design()` wird als erstes in der Hauptsteuerung aufgerufen —
bei **jedem** Rerun, weil Streamlit die Seite ja jedes Mal neu aufbaut.
Streamlit-Elemente erkennt man im CSS an ihren `data-testid`-Attributen
(z.B. `button[data-testid="stBaseButton-primary"]`) — die findest du, wenn du
im Browser F12 drückst und ein Element inspizierst.

### 3. Layout: `layout="wide"` + Spalten statt Sidebar
Die Streamlit-Sidebar ist IMMER links — deshalb war die Gewinnleiter links.
Lösung: `st.set_page_config(layout="wide")` und in der Hauptsteuerung
`links, rechts = st.columns([2.6, 1.1])`. `zeige_gewinnleiter()` ist dieselbe
Funktion wie vorher, sie wird nur per `with rechts:` in die rechte Spalte gesetzt.

### 4. Kopfzeile: `zeige_kopfzeile()` mit `st.metric`
Löst das "man muss scrollen um Name und Guthaben zu sehen"-Problem: Logo links,
daneben drei `st.metric`-Karten (Spieler / Runde / Gesamt). Steht über den
Spalten und ist damit immer oben sichtbar.

### 5. Antwort-Kapseln im TV-Stil
Die Antwort-Buttons bekommen `type="primary"` (reiner Anzeige-Parameter) und
das CSS macht daraus die Kapseln: `border-radius: 999px` = Pillenform, dunkler
Blau-Verlauf, beim Hover goldener Rand + Glow. Die A/B/C/D-Präfixe stehen im
Label; `p::first-letter` färbt den ersten Buchstaben gold — reines CSS, an
`antwort_pruefen()` geht weiterhin der Original-Antworttext.

### 6. Gewinnleiter als HTML-Karte
`zeige_gewinnleiter()` baut die 15 Stufen als eigenen HTML-Block mit drei
CSS-Klassen: `aktuell` (goldener Balken, pulsiert per `@keyframes`),
`gemacht` (blass + grüner Haken per `::after`), `offen` (normal).
Sicherheitsstufen (Frage 5/10) kriegen ein goldenes Schild. `position: sticky`
lässt die Karte beim Scrollen oben kleben.

### 7. Animationen
Bewusst nur drei, damit es edel bleibt statt überladen: Frage-Box blendet per
`@keyframes einblenden` ein, die aktuelle Gewinnstufe pulsiert, und beim
Millionengewinn gibt es `st.balloons()`. Wer im Betriebssystem "weniger
Animationen" eingestellt hat, bekommt sie per `prefers-reduced-motion` abgeschaltet.

### 8. Bestenliste auf dem Startbildschirm (Issue #24)
`zeige_bestenliste_tabelle()` **liest nur** über die vorhandene
`Bestenliste.lade_bestenliste()` und rendert eine HTML-Tabelle mit 🥇🥈🥉.
Gespeichert wird weiterhin ausschließlich im "Aufhören"-Button — an der
Speicher-Logik wurde nichts geändert. Wichtig: `html.escape()` um Spielernamen,
damit ein Name wie `<h1>lol` nicht das Layout sprengt.

### 9. Schrift
"Cinzel" (Google Fonts) für Titel und Beträge — der Gold-Gravur-Look. Ohne
Internet fällt sie automatisch auf Georgia zurück. Der große Schriftzug nutzt
einen Gold-Verlauf, der per `background-clip: text` auf den Text zugeschnitten wird.

## Testergebnisse (headless durchgeklickt am 13.07.)

- Komplettlauf bis zur Million (15 richtige Antworten): ✅ Ballons + Eintrag in Bestenliste
- Alle 3 Joker gleichzeitig auf einer Frage: ✅ bleiben alle sichtbar (#21-Fix bestätigt)
- Aussteigen → Neue Runde → Gesamtguthaben stimmt im Header: ✅
- Issue-#25-Szenario (mit 0 € eintragen → neues Spiel): ✅ kein Crash, keine alte Frage
  → **#25 kann nach eurem Gegencheck geschlossen werden** (gefixt durch PR #28)

## Noch offene Befunde (NICHT auf diesem Branch gefixt — nur Doku)

- **#20 Rest:** `telefon_auswahl_aktiv` wird beim Beantworten einer Frage nicht
  zurückgesetzt → offene Telefon-Auswahl kann in die nächste Frage "kleben".
  Fix-Idee: im Antwort-Handler zusätzlich `st.session_state.telefon_auswahl_aktiv = False`.
- **#23:** Gespeichert wird nur beim "Aufhören"-Button. Wer den Tab einfach
  schließt, landet nie in der Bestenliste.
- **#29 / Testdaten:** `bestenliste.json` liegt im Repo und wird bei jedem
  Testlauf beschrieben. Empfehlung: in `.gitignore` aufnehmen, dann passiert
  das "hab ausversehen die bestenliste mitcommittet" nicht mehr.
- **Millionen-Zähler:** `bestenliste.py` zählt `millionen` nur, wenn der
  übergebene Betrag exakt 1.000.000 ist — wer vorher schon Guthaben hatte,
  bekommt die Million nicht gezählt.
- **Kein Antwort-Feedback:** Nach einer falschen Antwort landet man sofort im
  Rundenende, ohne zu sehen, was richtig gewesen wäre. Wäre ein schöner
  nächster Schritt (braucht aber eine kleine Logik-Änderung, deshalb hier nicht).
- **Merge-Achtung:** Khalils Unittest-Branch ändert `naechste_frage()` auf
  `return None` — das Frontend prüft aber `isinstance(frage, str)`. Beim Merge
  muss die Prüfung angepasst werden (z.B. `if frage is None`).
