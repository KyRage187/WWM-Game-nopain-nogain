## **Code Konzept: Klausur-Quiz** 

Ein rundenbasiertes Lern Quiz im Stil von "Wer wird Millionär" 

Modul: Fortgeschrittene Programmierung 

Studiengang: WDSKI25A 

Team: Emil Gutschmiedt, Michel Köhler, Khalil Albert 

## **1.Unsere Idee** 

Wir bauen ein Quiz, mit dem man sich auf Klausuren vorbereiten kann. Die Idee ist an "Wer wird Millionär" angelehnt: Man bekommt nacheinander Fragen gestellt, und je weiter man kommt, desto schwerer werden sie. Die Fragen selbst kommen aus den Vorlesungsfolien und Übungen, sodass man beim Spielen tatsächlich den Stoff wiederholt. 

Wie im Fernsehen gibt es drei Joker, die man pro Spiel einmal benutzen darf: 50/50, Telefonjoker und Publikumsjoker. Jede Frage hat einen festen Geldbetrag, und je weiter man kommt, desto höher wird dieser. Es gibt zwei Gewinnstufen, ab denen, wenn man sie einmal erreicht hat, einen Mindestbetrag nicht mehr verliert, selbst wenn man danach falsch antwortet. Aussteigen kann man jederzeit und nimmt dann den Gewinn mit. Wer alle Fragen schafft ist Millionär und scheint gut gelernt zu haben. Am Ende landet das Ergebnis in einer Bestenliste. 

Bedienen kann man das Ganze über eine Oberfläche, die wir mit Streamlit umsetzen. 

## **2. Wie das Programm aufgebaut ist** 

Wir müssen die Spiellogik und die Anzeige trennen. Streamlit lädt bei jedem Klick das Skript wieder neu, also darf der Spielstand nicht in normalen Variablen stecken. Deswegen speichern wir das zentrale Quiz Object im session_state von Streamlit. 

Unsere Logikklassen haben keinen Streamlit-Code drin. Sie kümmern sich nur ums Spiel. Die Streamlit-Seite ruft sie auf und zeigt dann das Ergebnis. Das ist praktisch, weil die Logik so auch ohne Oberfläche getestet werden kann, zum Beispiel in der Konsole bevor die GUI überhaupt steht. 

Im Kern gibt es eine Klasse Quiz, die den Spielstand verwaltet und den Ablauf steuert. Sie nutzt die anderen Klassen: Frage, Spieler und Joker. Zwei weitere Klassen sorgen für unsere Daten: Eine lädt die Fragen aus einer Datei, die Andere speichert die Bestenliste. Nur die Streamlit-Datei kennt die Benutzeroberfläche. Alle anderen Klassen sind rein für die Spiellogik zuständig. 

## **3. Die Klassen** 

## **Difficulty** 

Hier geht es nur um die drei Schwierigkeitsstufen: leicht, mittel und schwer. Wir benutzen dafür ein Enum statt einfach nur einen Text wie zum Beispiel "schwer" zu übergeben. 

Im Spiel hängen die Stufen an der Fragennummer: die ersten fünf Fragen sind leicht, die nächsten fünf mittel und die letzten fünf schwer. So passt die Schwierigkeit zum Fortschritt und die beiden Sicherheitsstufen liegen genau an den Übergängen. 

Werte: LEICHT, MITTEL, SCHWER 

## **Frage** 

Diese Klasse ist dafür da, den Fragetext, die Antwortmöglichkeiten, die richtige Antwort und die Schwierigkeit zu speichern. 

|**Atribut / Methode**|**Typ**|**Beschreibung**|
|---|---|---|
|text|Atribut|Der Fragetext|
|antworten|Atribut|Liste der Antwortmöglichkeiten|
|richtge_antwort|Atribut|Die korrekte Antwort|
|schwierigkeit|Atribut|Schwierigkeitsstufe (Difculty)|
|ist_korrekt(antwort)|Methode|Prüf, ob eine Antwort richtg ist|
|__str__()|Methode|Textdarstellung für die Anzeige|



## **QuestionLoader** 

Diese Klasse liest die Fragen aus einer JSON Datei ein und macht daraus Frage Objects. Wir lagern die Fragen extra in eine Datei aus, damit man neue Fragen ergänzen kann, ohne den Code anfassen zu müssen. Die Klasse hat nur eine Aufgabe, und zwar die Fragen zu beschaffen und mehr nicht. 

|**Atribut / Methode**|**Typ**|**Beschreibung**|
|---|---|---|
|dateipfad|Atribut|Pfad zur JSON-Datei|
|lade_fragen()|Methode|Liest alle Fragen ein und gibt Frage Objects zurück|
|fragen_nach_schwierigkeit(stufe)|Methode|Gibt nur die Fragen einer Stufe zurück|



## **Joker** 

Joker ist die gemeinsame Basis für alle drei Joker. Wir bauen sie als abstrakte Basisklasse: Joker selbst legt nur fest, was ein Joker können muss, nämlich eine Methode "anwenden" anbieten, schreibt aber nicht vor, wie er das macht. Jede Unterklasse muss "anwenden" dann selbst ausfüllen. 

Der Vorteil ist, dass Quiz die Joker alle gleich behandeln kann: Sie liegen in einer gemeinsamen Liste, haben ein gemeinsames Feld für den Status "benutzt" und müssen nicht getrennt behandelt werden. Dadurch kann Quiz einfach prüfen, ob ein Joker schon eingesetzt wurde, ohne sich um die konkrete Art des Jokers kümmern zu müssen. Die Oberfläche kann die jeweiligen Ergebnisse dann jeweils passend anzeigen. 

|**Atribut / Methode**|**Typ**|**Beschreibung**|
|---|---|---|
|benutzt|Atribut|Ob der Joker schon verwendet wurde|
|anwenden(frage)|Methode|Führt den jeweiligen Joker aus (in jeder Unterklasse anders)|
|__str__()|Methode|Name des Jokers|



## **FiftyFiftyJoker, TelefonJoker, PublikumsJoker** 

Das sind die drei konkreten Joker. Jeder erbt von Joker und füllt "anwenden" auf seine eigene Art. Was wir uns überlegen mussten: die drei machen nicht nur intern etwas Anderes, sie geben auch etwas anderes zurück. Der FiftyFiftyJoker streicht zwei falsche Antworten weg, der Telefonjoker einen Satz, den die angerufene Person sagt, und der Publikumsjoker eine Prozentverteilung. Die Oberfläche zeigt jedes dieser Ergebnisse passend an, also gekürzte Buttons, eine Sprechblase oder ein kleines Balkendiagramm. Die gemeinsame Basis sorgt also dafür, dass Quiz die Joker einheitlich verwalten kann; angezeigt wird trotzdem jeder auf seine eigene Weise. 

Der FiftyFiftyJoker entfernt zwei falsche Antworten, sodass nur noch die richtige und eine falsche Antwort übrigbleiben. 

Der Telefonjoker ist ein kleiner Sonderfall: bevor er etwas tut, wählt der Spieler aus, wen er anruft. Es gibt drei Personen zur Auswahl, JBL, Wezon und Drabi und je nachdem fällt die Antwort anders aus. Deshalb braucht dieser Joker eine weitere Information und zwar die ausgewählte Person, während FiftyFiftyJoker und PublikumsJoker ohne extra Informationen funktionieren. 

   - JBL antwortet: "Das ist einfach: es ist Antwort ..." (Antwortmöglichkeit ist immer richtig) 

   - Wezon sagt: "Digga, kein Plan, nimm ..." (Antwortmöglichkeit ist nicht immer richtig) 

- Drabi gibt seine übliche Antwort: "Die Antwort ist trivial." (Hier wird keine Antwortmöglichkeit erwähnt) 

Der Publikumsjoker zeigt eine geschätzte Prozentverteilung über die Antworten an, also so, wie ein Publikum abstimmen würde, mit einer Tendenz zur richtigen Antwort. 

## **Spieler** 

Der Spieler steht für die Person, die gerade spielt, zusammen mit seinem Guthaben. Dabei unterscheiden wir zwei Beträge: das Rundenguthaben, also was in der aktuellen Runde gerade auf dem Spiel steht, und das Gesamtguthaben, also die Summe aller abgeschlossenen Runden. Nach jeder Runde wird das Rundenguthaben auf das Gesamtguthaben draufgerechnet, und die nächste Runde fängt wieder bei null an. In die Bestenliste kommt am Ende das Gesamtguthaben. 

|**Atribut / Methode**|**Typ**|**Beschreibung**|
|---|---|---|
|name|Atribut|Name des Spielers|
|runden_guthaben|Atribut|Aktuell erspielter Betrag in dieser Runde|
|gesamt_guthaben|Atribut|Summe aller abgeschlossenen Runden|
|setze_runden_guthaben(betrag)|Methode|Setzt das Rundenguthaben auf den Betrag der erreichten<br>Stufe|
|runde_abschliessen()|Methode|Addiert das Rundenguthaben auf das Gesamtguthaben<br>und setzt es zurück|



## **Quiz** 

Quiz ist unsere Hauptklasse. Hier liegt der komplette Spielstand, und von hier wird der Ablauf gesteuert. Quiz sucht die nächste Frage passend zur aktuellen Schwierigkeit heraus, prüft die Antworten, vergibt das Guthaben, verwaltet die Joker und merkt, wann das Spiel vorbei ist. 

Zum Spielstand gehört auch die Gewinnleiter, also die festen Geldbeträge der 15 Fragen. Die ist in jedem Spiel gleich und reicht von 50 Euro bei der ersten Frage bis zum Hauptpreis bei der fünfzehnten Frage. Zwei dieser Fragen nach Frage 5 und nach Frage 10, sind Sicherheitsstufen: hat man sie einmal erreicht, fällt man bei einer falschen Antwort nicht mehr darunter. Welche Schwierigkeit gerade dran ist, ergibt sich einfach aus der Fragennummer. 

|**Atribut / Methode**|**Typ**|**Beschreibung**|
|---|---|---|
|spieler|Atribut|Der aktuelle Spieler|
|fragen|Atribut|Alle geladenen Fragen|
|gewinnleiter|Atribut|Die festen Geldbeträge der 15 Stufen|
|aktuelle_frage_nummer|Atribut|Die wievielte Frage gerade dran ist|
|aktuelle_schwierigkeit|Atribut|Aktuelle Stufe (folgt aus der Fragennummer)|
|joker|Atribut|Liste der verfügbaren Joker|
|laeuf|Atribut|Ob das Spiel noch läuf|
|naechste_frage()|Methode|Liefert die nächste passende Frage|
|antwort_pruefen(antwort)|Methode|Bei richtg: Guthaben hochsetzen und weiter. Bei falsch:<br>zurück auf die letzte Sicherheitsstufe und Spielende|
|joker_einsetzen(joker)|Methode|Setzt einen Joker ein|
|aussteigen()|Methode|Beendet das Spiel; der Spieler behält das aktuelle Guthaben|
|neue_runde()|Methode|Startet eine neue Runde wieder bei der ersten Frage|
|ist_vorbei()|Methode|Sagt, ob das Spiel zu Ende ist|



## **Highscore** 

Diese Klasse speichert die Bestenliste lokal in einer JSON Datei. Wir überlegen noch, ob es sinnvoll ist, einen Server zu erstellen, um die Bestenlisten auch online zu speichern um sie von mehreren Geräten aus nutzen zu können. 

|können.|||
|---|---|---|
|**Atribut / Methode**|**Typ**|**Beschreibung**|
|dateipfad|Atribut|Pfad zur JSON Datei der Bestenliste|
|speichere(name, gesamt_guthaben)|Methode|Schreibt ein Ergebnis in die Bestenliste|
|lade_bestenliste()|Methode|Liest die gespeicherte Bestenliste|



## **Die Streamlit Oberfläche** 

Sie ist keine eigene Klasse, sondern die Datei, die die Oberfläche baut. Sie hält das Quiz-Object im session_state, zeigt die Frage mit ihren Antwort Buttons, die Joker und den Punktestand an und gibt das, was der Spieler anklickt, an Quiz weiter. 

## **4. Wie wir uns das alles in der Praxis vorstellen** 

In einem normalen Spiel lädt der QuestionLoader die Fragen, und das Quiz Object wird im session_state abgelegt. Die Oberfläche fragt das Quiz nach der nächsten Frage, zeigt sie mit ihrem aktuellen Geldbetrag an und lässt den Spieler antworten, einen Joker wählen oder aussteigen. 

Antwortet der Spieler richtig, wird sein Guthaben auf den Betrag der aktuellen Stufe gesetzt und es geht weiter zur nächsten, schwereren Frage. Antwortet er falsch, ist das Spiel vorbei, und er behält den Betrag der letzten erreichten Sicherheitsstufe. Hat er noch keine erreicht, geht er leer aus. Steigt er stattdessen freiwillig aus, behält er das Guthaben, das er gerade hat. Wer alle fünfzehn Fragen richtig beantwortet, ist Millionär. 

Wenn ein Joker eingesetzt wird, übergibt die Oberfläche diese Information an das Quiz. Der Joker merkt sich, dass er benutzt wurde, und die Oberfläche zeigt sein Ergebnis an, je nach Joker als gekürzte Antworten, als Tipp einer angerufenen Person oder als Prozentverteilung. 

Ist eine Runde vorbei, egal ob durch Aussteigen, eine falsche Antwort oder den Hauptpreis, wird das in dieser Runde erspielte Guthaben auf das Gesamtguthaben des Spielers addiert. Danach kann er eine neue Runde starten, die wieder bei der ersten Frage beginnt, oder aufhören. Hört er auf, kommt sein Gesamtguthaben über alle gespielten Runden in die Bestenliste. 

## **5. Wie wir auf sauberen Code achten** 

Beim Aufbau haben wir uns an ein paar gängige Prinzipien für sauberen Code gehalten. 

Jede Klasse hat genau eine Aufgabe. Das Laden der Fragen, die Bestenliste, der Spielablauf und die Joker sind getrennt. Wir nutzen also das Prinzip der Single Responsibility und sorgen dafür, dass der Code übersichtlich bleibt und man bei einer Änderung den Code nur an einer Stelle anpassen muss. 

Die Joker sind als eine abstrakte Oberklasse mit drei Unterklassen gebaut. Das bringt mehrere Vorteile. Erstens kann das Quiz mit allen Jokern gleich umgehen, ohne den konkreten Typ zu kennen, und man könnte einen Joker gegen einen anderen austauschen, ohne dass im Quiz etwas nicht mehr funktioniert. Das ist das Liskov Prinzip. Zweitens hängt das Quiz nur von der gemeinsamen Joker Basis ab und nicht von den einzelnen Jokern, also Dependency Inversion. Und drittens: fällt uns später ein vierter Joker ein, wird er einfach als neue Unterklasse ergänzt, ohne dass wir das Quiz selbst ändern müssen. Das ist das Open-Closed-Prinzip, offen für Erweiterungen, geschlossen für Änderungen am bestehenden Code. 

Der FiftyFiftyJoker braucht kein eigenes Feld für die falschen Antworten. Er nimmt einfach die falschen Antworten aus der Frage und entfernt zwei davon. So gibt es nur eine Stelle, die festlegt, was richtig und was falsch ist und wir speichern dieselbe Information nicht doppelt. Das ist das DRY-Prinzip. Ansonsten halten wir uns an die normalen Python Konventionen: sprechende Namen, einheitliche Schreibweise und nur dort Kommentare, wo sie wirklich nötig sind. Das sollte dafür sorgen, den Code kurz zu 

halten und später leichter zu ändern. Spezialmethoden wie __init__ und __str__ nutzen wir, wenn sie sinnvoll sind. 

## **6. Aufwandsschätzung** 

Wir sind drei Personen und stimmen uns regelmäßig in Calls ab. Der Aufwand teilt sich grob in die eigentliche Programmierung und das Drumherum auf. 

Zur Programmierung lässt sich das Projekt gut in drei Bereiche aufteilen, die kaum voneinander abhängen, sodass wir parallel arbeiten können: 

|**Person**|**Bereich**|**Was dazugehört**|
|---|---|---|
|A|Spiellogik|Quiz, Frage, Spieler, Difculty|
|B|Joker und Daten|die Joker-Klassen, das Laden der Fragen, die Bestenliste, die JSON-<br>Daten|
|C|Oberfäche und<br>Zusammenbau|die Streamlit-Oberfäche, der session_state, das Verbinden aller<br>Teile|



Dazu kommen die Dinge, die nicht direkt Programmieren sind, aber genauso zum Projekt gehören: 

|**Aufgaben**|**Aufwand (pro Person, grob)**|
|---|---|
|Ideenfndung und Festlegung des Umfangs|ca. 2 h|
|Programmierung des eigenen Bereichs|ca. 12 h|
|Abstmmung in Calls über die Laufzeit|ca. 3 h|
|Tests schreiben und durchgehen|ca. 3 h|
|Gegenseitges Durchschauen des Codes|ca. 2 h|
|Dokumentaton, README und requirements.txt|ca. 2 h|



Pro Person kommen wir damit auf rund 22 bis 24 Stunden, im Team also auf etwa 65 bis 70 Stunden. Die Aufgaben, Tests, Reviews und Dokumentation machen wir zusammen. 

Da wir Git benutzen, achten wir auf eine saubere History, gute Commit-Messages und ordentliche BranchNamen. Niemand arbeitet direkt im main-branch, sondern jeder legt für eine abgeschlossene Aufgabe seinen eigenen Branch an. Am Ende wird der Branch über einen Pull Request zusammengeführt und von jemand anderem geprüft. So entstehen viele kleine, hoffentlich nachvollziehbare Schritte, und jeder weiß, was die anderen gemacht haben. 

## **7. Was später noch denkbar wäre** 

Über den eigentlichen Umfang hinaus hatten wir noch ein paar Ideen für später: 

- Das erspielte Guthaben könnte man in kleinen Glücksspielen wie Blackjack oder Roulette einsetzen. Das wäre dann aber eher ein zweites Spiel in unserem Hauptspiel und kommt deswegen erstmal nicht mit dazu 

- Außerdem könnte man die Bestenliste auf einen Server auslagern, damit man sich auch über verschiedene Geräte hinweg vergleichen kann. 

