# Lernhilfe für den Fischereischein Bayern

Eine Python-Anwendung zur Erstellung von Lernmaterialien für Fischarten, ihre Schonzeiten und Mindestmaße nach bayerischen Fischereiverordnungen.

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

## Nutzung

Das Hauptskript bietet ein interaktives Menü mit zwei Hauptoptionen:

### 1. Karteikarten/Dateien generieren
**Fischauswahl:**
- **Alle Fische** (80+ Einträge) - Kompletter Datensatz
- **Ganzjährig geschont** (41 Einträge) - Ganzjährig geschützte Fische  
- **Schonzeit/Mindestmaß** (23 Einträge) - Fische mit Schonzeiten oder Mindestmaßen

**Formatauswahl:**
- **PDF Karteikarten** - Druckfertige Karteikarten (90×60mm)
- **CSV für Repetico/Anki** - Importformat für Karteikarten-Apps
- **JSON für Repetico** - Natives Repetico-Format
- **Alle Formate** - Alle drei Formate generieren

### 2. Fischbilder herunterladen
- **Alle Bilder herunterladen** - Lädt fehlende Bilder automatisch
- **Bilder neu herunterladen** - Überschreibt vorhandene Bilder
- **Schlechte Qualität ersetzen** - Ersetzt Bilder aus der Qualitätskontrolle-Liste
- **Selektiver Download** - Download für bestimmte Fischgruppen

## Projektstruktur

```
bayern-fische-schonzeiten/
├── generate.py                    # Haupt-Generierungsskript
├── data/
│   └── fish_data.json            # Fischdatenbank (321+ Einträge)
├── config/
│   └── poor_quality_images.txt   # Fischnamen für Bildaustausch
├── images/                        # Fischbilder (automatisch verwaltet)
├── output/                        # Generierte Dateien
└── requirements.txt               # Python-Abhängigkeiten
```

## Bildqualitätskontrolle

1. Fischnamen zu `config/poor_quality_images.txt` hinzufügen (ein Name pro Zeile)
2. Generator ausführen - sucht automatisch nach besseren Bildern
3. Erfolgreiche Ersetzungen werden automatisch aus der Liste entfernt

## Anforderungen

- **Python**: 3.7+
- **Internet**: Erforderlich für Bild-Download
- **Abhängigkeiten**: `pip install fpdf2 pillow ddgs requests`

## Ausgabedateien

Alle Dateien werden im `output/`-Verzeichnis gespeichert:
- **PDF**: `[auswahl]_karteikarten.pdf`
- **CSV**: `[auswahl]_repetico.csv` 
- **JSON**: `[auswahl]_repetico.json`

## Bildungskontext

Dieses Tool unterstützt die bayerische Fischerprüfungsvorbereitung:
- Fischartenerkennung
- Schonzeiten und Mindestmaße
- Regionale Fischereiverordnungen