# Schonzeiten - Bayerische Fischarten Lernhilfe

Eine Python-Anwendung zur Erstellung von Lernmaterialien für Fischarten, ihre Schonzeiten und Mindestmaße nach bayerischen Fischereiverordnungen.

## Features

- **Einheitliches Generierungsskript**: Einzige Benutzeroberfläche für alle Ausgabeformate
- **PDF-Karteikarten-Generierung**: Erstellt druckbare Karteikarten mit Fischbildern und Verordnungsdetails
- **Mehrere Export-Formate**: PDF-, CSV- und Repetico-JSON-Formate
- **Intelligente Filterung**: Materialien für alle Fische oder nur solche mit Schonzeiten generieren
- **Automatisches Bildladen**: Lädt hochqualitative Fischbilder mit Validierung herunter
- **Qualitätskontrollsystem**: Verwaltung und Austausch von Bildern schlechter Qualität
- **Doppelseitiger Druckoptimierung**: Karten korrekt für Drucken und Schneiden positioniert

## Schnellstart

1. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generator starten:**
   ```bash
   python generate.py
   ```

3. **Ausgabeformat wählen** aus dem interaktiven Menü

## Projektstruktur

```
schonzeiten/
├── generate.py                    # Haupt-Generierungsskript mit interaktivem Menü
├── data/
│   └── fish_data.json            # Primäre Fischdatenbank (321+ Einträge)
├── config/
│   └── poor_quality_images.txt   # Fischnamen, die bessere Bilder benötigen
├── images/
│   └── fish_images/              # Heruntergeladene Fischbilder (automatisch verwaltet)
├── output/                       # Generierte Dateien (PDFs, CSVs, JSONs)
├── requirements.txt              # Python-Abhängigkeiten
└── README.md
```

## Nutzung

### Interaktive Generierung

Das Hauptskript bietet ein interaktives Menü:

```bash
python generate.py
```

**Zweistufiger Prozess:**

1. **Fischauswahl:**
   - **Alle Fische** (80 Einträge) - Kompletter Datensatz
   - **Ganzjährig geschont** (41 Einträge) - Ganzjährig geschützte Fische
   - **Schonzeit/Mindestmaß** (23 Einträge) - Fische mit Schonzeiten oder Mindestmaßen

2. **Formatauswahl:**
   - **PDF Karteikarten** - Druckfertige Karteikarten
   - **CSV für Repetico/Anki** - Importformat für Karteikarten-Apps
   - **JSON für Repetico** - Natives Repetico-Format
   - **Alle Formate** - Alle drei Formate generieren

### Ausgabedateien

Alle generierten Dateien werden im `output/`-Verzeichnis mit beschreibenden Namen gespeichert:

- **PDF-Dateien**: `alle_fische_karteikarten.pdf`, `ganzjaehrig_geschont_karteikarten.pdf`, `schonzeit_mindestmass_karteikarten.pdf`
- **CSV-Dateien**: `alle_fische_repetico.csv`, `ganzjaehrig_geschont_repetico.csv`, `schonzeit_mindestmass_repetico.csv`
- **JSON-Dateien**: `alle_fische_repetico.json`, `ganzjaehrig_geschont_repetico.json`, `schonzeit_mindestmass_repetico.json`

## Datenmanagement

### Primäre Datenquelle

- **`data/fish_data.json`**: Einzige umfassende Datenbank mit 321+ Fischeinträgen
- **Format**: `{"question": "Fischname", "answer": "Verordnungen und Beschreibung"}`
- **Kodierung**: UTF-8 für ordnungsgemäße deutsche Zeichenunterstützung

### Bildqualitätskontrolle

1. **Problemfische hinzufügen** zu `config/poor_quality_images.txt` (ein Name pro Zeile)
2. **Generator ausführen** - er sucht automatisch nach besseren Bildern
3. **Erfolgreiche Ersetzungen** werden automatisch aus der Liste entfernt

**Bildanforderungen:**
- Mindestgröße: 500×300 Pixel
- Automatische Duplikatserkennung (SHA-256-Hashing)
- Visuelle Ähnlichkeitsfilterung (MSE < 10)
- 3-Versuch-Wiederholungslogik mit exponentieller Verzögerung

### Fischfilteroptionen

**Ganzjährig geschont (41 Fische):**
- Fische, die ganzjährig geschützt sind
- Identifiziert durch "Ganzjährig geschont" im Antworttext
- Können zu keiner Zeit gefangen werden

**Schonzeit/Mindestmaß (23 Fische):**  
- Fische mit Schonzeiten oder Mindestmaßanforderungen
- Identifiziert durch "Schonzeit:" ODER "Mindestmaß:" im Antworttext
- Schließt ganzjährig geschützte Fische aus
- Das sind die Fische mit spezifischen Verordnungen zum Lernen

## PDF-Karteikarten Details

- **Kartengröße**: 90×60mm mit 10mm Rändern
- **Layout**: 8 Karten pro Seite (4×2 Raster), ~20 Seiten insgesamt
- **Doppelseitig**: Vorderseite (Bilder) und Rückseite (Text) mit gespiegeltem Layout zum Schneiden
- **Schrift**: Arial Unicode für deutsche Zeichen
- **Druckanweisungen**: 
  1. Doppelseitig drucken (an langer Kante wenden)
  2. Entlang der Kartengrenzen schneiden
  3. Jede Karte hat Bild auf einer Seite, Verordnungen auf der anderen

## Export-Formate

### CSV-Format
- Kompatibel mit Anki, Repetico und anderen Karteikarten-Systemen
- Deutsche Datumsnormalisierung: `DD.MM. bis DD.MM.`
- HTML-Zeilenumbrüche für mehrzeilige Inhalte
- Struktur: `Fischname, Verordnungsdetails`

### Repetico JSON
- Natives Format für die Repetico-Karteikarten-Plattform
- Ordnungsgemäße Zeilenschaltungsformatierung für mehrzeilige Antworten
- Direkte Import-Kompatibilität

## Anforderungen

- **Python**: 3.7+
- **Internet**: Erforderlich für Bild-Download
- **Schrift**: Arial Unicode (Systemschrift für deutsche Zeichen)
- **Abhängigkeiten**: Siehe `requirements.txt`

## Entwicklung

### Kern-Abhängigkeiten
```bash
pip install fpdf2 pillow ddgs requests
```

### Einzelne Funktionen testen
```bash
python test_generate.py  # Kernfunktionalität testen
```

## Fehlerbehebung

- **Fehlende Bilder**: Internetverbindung prüfen, Bilder werden automatisch abgerufen
- **PDF-Generierungsfehler**: Sicherstellen, dass Arial Unicode-Schrift verfügbar ist
- **Schlechte Bildqualität**: Fischnamen zu `config/poor_quality_images.txt` hinzufügen
- **Import-Probleme**: Dateikodierung prüfen (sollte UTF-8 sein)

## Bildungskontext

Dieses Tool ist für die deutsche Fischerprüfungsvorbereitung konzipiert und konzentriert sich auf:
- Fischartenerkennung
- Einhaltung bayerischer Fischereiverordnungen
- Schonzeit-Bewusstsein
- Mindestmaßanforderungen (Mindestmaß)
- Regionale Fischereigebietsklassifizierungen (D/E/R/W)