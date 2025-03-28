Tennis Turnier Manager
Ein Python-basiertes Tennis-Turnier-Management-System, das es ermöglicht, ein Round-Robin-Turnier zu organisieren, Spielergebnisse zu erfassen, Spielerstatistiken zu überwachen und vieles mehr. Ideal für die Verwaltung von kleinen bis mittleren Tennis-Turnieren!

Funktionen
Spieler hinzufügen: Füge Spieler zum Turnier hinzu, mit einer maximalen Spieleranzahl von 10.

Paarungen erstellen: Erstelle automatische Round-Robin-Paarungen basierend auf der Spieleranzahl.

Spielplan anzeigen: Zeigt alle Paarungen und Runden des Turniers an.

Ergebnisse eintragen: Erfasst die Ergebnisse von Spielen, wobei nur gültige Tennis-Ergebnisse (z.B. "6:4", "7:5") akzeptiert werden.

Statistiken anzeigen: Zeigt die Gesamtstatistik eines Spielers (Siege, Niederlagen, gewonnene und verlorene Sätze).

Fairness-Check: Überprüft, ob alle Spieler fair verteilt spielen und eine angemessene Pausenzeit zwischen den Spielen haben.

Installation
Python installieren: Stellen Sie sicher, dass Python 3 auf Ihrem System installiert ist. Falls nicht, laden Sie es von python.org herunter.

Projekt herunterladen: Klonen oder laden Sie das Repository herunter:

bash
Kopieren
Bearbeiten
git clone https://github.com/dein-github-benutzername/tennis-turnier-manager.git
Abhängigkeiten installieren: Installieren Sie die benötigten Python-Bibliotheken:

bash
Kopieren
Bearbeiten
pip install -r requirements.txt
Nutzung
Programm starten: Starten Sie das Programm mit:

bash
Kopieren
Bearbeiten
python tennis_turnier_manager.py
Spieler hinzufügen:
Fügen Sie Spieler zum Turnier hinzu. Sie können maximal 10 Spieler hinzufügen.

Paarungen erstellen und Spielplan anzeigen:
Erstellen Sie automatisch den Spielplan für das Turnier und überprüfen Sie die Fairness der Spiele.

Ergebnisse eintragen:
Geben Sie das Ergebnis eines Spiels ein, indem Sie die Sätze (z.B. "6:4, 6:3") für beide Spieler eingeben.

Statistiken abrufen:
Überprüfen Sie die Statistiken eines bestimmten Spielers, einschließlich Siege, Niederlagen und gewonnene/verlorene Sätze.

Fairness überprüfen:
Überprüfen Sie, ob die Pausen zwischen den Spielen für alle Spieler gerecht verteilt sind.

Beispiel: Ergebnis eintragen
Gültige Formate:

6:4 (normaler Satz)

6:3 (gültig)

Ungültige Formate:

6-4 (ungültig, falsches Trennzeichen)

abc (ungültig, keine Zahl)

Tests
Das Projekt enthält Unit-Tests, um sicherzustellen, dass alle Funktionen korrekt arbeiten. Du kannst die Tests mit pytest ausführen:

Installiere pytest:

bash
Kopieren
Bearbeiten
pip install pytest
Führe die Tests aus:

bash
Kopieren
Bearbeiten
pytest
Mitwirken
Wenn du zu diesem Projekt beitragen möchtest:

Forke das Repository.

Erstelle einen Branch für deine Änderungen.

Stelle einen Pull Request mit einer Beschreibung der Änderungen.

Lizenz
Dieses Projekt steht unter der MIT Lizenz. Siehe die LICENSE-Datei für weitere Informationen.

Viel Spaß beim Organisieren deines Tennis-Turniers! 🎾🏆
