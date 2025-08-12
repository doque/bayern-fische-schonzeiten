# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Schonzeiten** is a Python-based fish identification training system that generates flashcards for learning fish species, their closed seasons (Schonzeiten), and minimum sizes in Bavaria, Germany. The project has been reorganized with a unified generation system and clean folder structure.

## Development Commands

```bash
# Install all dependencies
pip install -r requirements.txt

# Install core dependencies only (minimal setup)
pip install fpdf2 pillow ddgs requests

# Run the main interactive generator
python generate.py

# Test functionality with sample data
python test_generate.py
```

## Architecture

### Reorganized File Structure

- **`generate.py`** - Unified generation script with interactive menu system
- **`data/fish_data.json`** - Single comprehensive data source (321+ fish entries)
- **`config/poor_quality_images.txt`** - Quality control file (renamed from shit.txt)
- **`images/fish_images/`** - Auto-managed directory for downloaded fish images
- **`output/`** - All generated files (PDFs, CSVs, JSONs) organized by type
- **`test_generate.py`** - Development testing script for core functionality

### Unified Generation System

The new `FishGenerator` class provides a single interface for all output formats:

1. **Interactive Menu**: Command-line interface with 7 generation options
2. **Smart Filtering**: Automatic Schonzeit filtering based on answer text analysis
3. **Multi-format Output**: PDF, CSV, and Repetico JSON generation from single codebase
4. **Quality Control Integration**: Seamless image replacement workflow

### Data Processing Pipeline

**Three-stage architecture maintained with improvements:**

1. **Data Loading**: Single JSON source with UTF-8 encoding for German characters
2. **Optional Filtering**: Schonzeit detection logic (`"Schonzeit:" in answer AND "Ganzjährig geschont" not in answer`)
3. **Format Generation**: Multi-format output with proper path management

### Image Management System

**Enhanced quality control system:**

- **Centralized Configuration**: `config/poor_quality_images.txt` replaces previous naming
- **Automated Workflow**: Add fish names → run generator → auto-removal on success
- **Quality Validation**: 500x300px minimum, SHA-256 deduplication, MSE similarity (<10)
- **Resilient Fetching**: 3-attempt retry with exponential backoff, random shuffling

### Output Management

**Organized output structure:**
- **PDF Files**: `alle_fische_karteikarten.pdf`, `schonzeit_fische_karteikarten.pdf`
- **CSV Files**: `alle_fische.csv`, `schonzeit_fische.csv`
- **JSON Files**: `alle_fische_repetico.json`, `schonzeit_fische_repetico.json`

## Generation Options

### Interactive Menu System

The `generate.py` script uses a **two-step interactive process**:

**Step 1 - Fish Selection:**
1. **All Fish (80)**: Complete dataset  
2. **Ganzjährig geschont (41)**: Year-round protected fish
3. **Schonzeit/Mindestmaß (23)**: Fish with specific regulations

**Step 2 - Format Selection:**
1. **PDF Karteikarten**: Print-ready flashcards
2. **CSV für Repetico/Anki**: Import-ready format 
3. **JSON für Repetico**: Native Repetico format
4. **Alle Formate**: Generate all three formats

### Fish Filtering System

**Three-tier filtering approach:**

1. **All Fish (80 entries)** - Complete dataset
2. **Ganzjährig geschont (41 entries)** - Year-round protected fish
3. **Schonzeit/Mindestmaß (23 entries)** - Fish with regulations

**Filtering Algorithms:**
```python
def filter_fish_ganzjaehrig_geschont(self):
    # Fish protected year-round
    return [fish for fish in self.fish_data 
            if "Ganzjährig geschont" in fish["answer"]]

def filter_fish_with_schonzeit(self):
    # Fish with closed seasons or minimum sizes (excludes year-round protected)
    return [fish for fish in self.fish_data 
            if ("Schonzeit:" in fish["answer"] or "Mindestmaß:" in fish["answer"]) 
            and "Ganzjährig geschont" not in fish["answer"]]
```

## Key Implementation Patterns

### Class-based Architecture
- **Single Responsibility**: `FishGenerator` class handles all generation logic
- **Path Management**: Centralized directory and file path handling
- **Error Recovery**: Graceful handling of missing files, network issues

### German Text Processing
- **Date Normalization**: RegEx patterns for `(\d{2}\.\d{2})[–-](\d{2}\.\d{2})` → `DD.MM. bis DD.MM.`
- **Special Cases**: "Ganzjährig geschont" detection and handling
- **UTF-8 Throughout**: Proper German character support in all formats

### Multi-format Export
- **PDF**: Double-sided flashcard layout with image/text separation
- **CSV**: Platform-compatible with HTML line breaks (`<br/>`) 
- **JSON**: Repetico-native format with proper newline conversion

### Quality Control Integration
- **Automated List Management**: Poor quality entries auto-removed on successful replacement
- **Status Reporting**: Clear feedback on image fetch success/failure
- **Batch Processing**: Continue processing when individual items fail

## Development Context

This is a specialized educational tool for German fishing license preparation. The reorganized structure provides:

- **Single Entry Point**: `generate.py` for all generation needs
- **Clean Organization**: Logical separation of data, config, images, and output
- **Development Friendly**: Easy testing and debugging with `test_generate.py`
- **User Focused**: Interactive menu system for non-technical users

The codebase combines web scraping, image processing, and multi-format document generation optimized for Bavarian fishing regulation study materials.