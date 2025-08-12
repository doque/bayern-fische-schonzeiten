# Schonzeiten - Bavarian Fish Regulation Study Tool

A Python application that generates study materials for learning fish species, their closed seasons (Schonzeiten), and minimum sizes according to Bavarian fishing regulations.

## Features

- **Unified Generation Script**: Single command-line interface for all output formats
- **PDF Flashcard Generation**: Creates printable flashcards with fish images and regulation details
- **Multiple Export Formats**: PDF, CSV, and Repetico JSON formats
- **Smart Filtering**: Generate materials for all fish or only those with Schonzeiten
- **Automatic Image Fetching**: Downloads high-quality fish images with validation
- **Quality Control System**: Manage and replace poor-quality images
- **Double-sided Print Optimization**: Cards positioned correctly for printing and cutting

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the generator:**
   ```bash
   python generate.py
   ```

3. **Choose your output format** from the interactive menu

## Project Structure

```
schonzeiten/
├── generate.py                    # Main generation script with interactive menu
├── data/
│   └── fish_data.json            # Primary fish database (321+ entries)
├── config/
│   └── poor_quality_images.txt   # Fish names needing better images
├── images/
│   └── fish_images/              # Downloaded fish images (auto-managed)
├── output/                       # Generated files (PDFs, CSVs, JSONs)
├── requirements.txt              # Python dependencies
└── README.md
```

## Usage

### Interactive Generation

The main script provides an interactive menu:

```bash
python generate.py
```

**Two-Step Process:**

1. **Fish Selection:**
   - **Alle Fische** (80 entries) - Complete dataset
   - **Ganzjährig geschont** (41 entries) - Year-round protected fish
   - **Schonzeit/Mindestmaß** (23 entries) - Fish with closed seasons or minimum sizes

2. **Format Selection:**
   - **PDF Karteikarten** - Print-ready flashcards
   - **CSV für Repetico/Anki** - Import format for flashcard apps
   - **JSON für Repetico** - Native Repetico format
   - **Alle Formate** - Generate all three formats

### Output Files

All generated files are saved in the `output/` directory with descriptive names:

- **PDF Files**: `alle_fische_karteikarten.pdf`, `ganzjaehrig_geschont_karteikarten.pdf`, `schonzeit_mindestmass_karteikarten.pdf`
- **CSV Files**: `alle_fische_repetico.csv`, `ganzjaehrig_geschont_repetico.csv`, `schonzeit_mindestmass_repetico.csv`
- **JSON Files**: `alle_fische_repetico.json`, `ganzjaehrig_geschont_repetico.json`, `schonzeit_mindestmass_repetico.json`

## Data Management

### Primary Data Source

- **`data/fish_data.json`**: Single comprehensive database with 321+ fish entries
- **Format**: `{"question": "Fish Name", "answer": "Regulations and description"}`
- **Encoding**: UTF-8 for proper German character support

### Image Quality Control

1. **Add problem fish** to `config/poor_quality_images.txt` (one name per line)
2. **Run generator** - it will automatically search for better images
3. **Successful replacements** are automatically removed from the list

**Image Requirements:**
- Minimum size: 500×300 pixels
- Automatic duplicate detection (SHA-256 hashing)
- Visual similarity filtering (MSE < 10)
- 3-attempt retry logic with exponential backoff

### Fish Filtering Options

**Ganzjährig geschont (41 fish):**
- Fish that are protected year-round
- Identified by "Ganzjährig geschont" in the answer text
- Cannot be caught at any time

**Schonzeit/Mindestmaß (23 fish):**  
- Fish with closed seasons or minimum size requirements
- Identified by "Schonzeit:" OR "Mindestmaß:" in answer text
- Excludes year-round protected fish
- These are the fish with specific regulations to learn

## PDF Flashcard Details

- **Card Size**: 90×60mm with 10mm margins
- **Layout**: 8 cards per page (4×2 grid), ~20 pages total
- **Double-sided**: Front (images) and back (text) with mirrored layout for cutting
- **Font**: Arial Unicode for German characters
- **Print Instructions**: 
  1. Print double-sided (flip on long edge)
  2. Cut along card boundaries
  3. Each card has image on one side, regulations on the other

## Export Formats

### CSV Format
- Compatible with Anki, Repetico, and other flashcard systems
- German date normalization: `DD.MM. bis DD.MM.`
- HTML line breaks for multi-line content
- Structured: `Fish Name, Regulation Details`

### Repetico JSON
- Native format for Repetico flashcard platform
- Proper newline formatting for multi-line answers
- Direct import compatibility

## Requirements

- **Python**: 3.7+
- **Internet**: Required for image downloading
- **Font**: Arial Unicode (system font for German characters)
- **Dependencies**: See `requirements.txt`

## Development

### Core Dependencies
```bash
pip install fpdf2 pillow ddgs requests
```

### Testing Individual Functions
```bash
python test_generate.py  # Test core functionality
```

## Troubleshooting

- **Missing images**: Check internet connection, images will be fetched automatically
- **PDF generation errors**: Ensure Arial Unicode font is available
- **Poor image quality**: Add fish names to `config/poor_quality_images.txt`
- **Import issues**: Check file encoding (should be UTF-8)

## Educational Context

This tool is designed for German fishing license preparation, focusing on:
- Fish species identification
- Bavarian fishing regulation compliance  
- Schonzeit (closed season) awareness
- Minimum size requirements (Mindestmaß)
- Regional fishing area classifications (D/E/R/W)