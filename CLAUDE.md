# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Schonzeiten** is a Python-based fish identification training system that generates flashcards for learning fish species, their closed seasons (Schonzeiten), and minimum sizes in Bavaria, Germany.

## Development Commands

```bash
# Install dependencies
pip install fpdf2 pillow duckduckgo_search

# Generate flashcards and fetch fish images
python fetch.py

# Convert JSON data to CSV format
python convert_json_to_csv.py input.json output.csv
```

## Architecture

### Core Components

- **`fetch.py`** - Main application that generates PDF flashcards and fetches fish images from DuckDuckGo
- **`convert_json_to_csv.py`** - Converts JSON fish data to CSV format for import into other flashcard systems
- **`fische.json`** - Primary data source containing 321 fish entries with questions/answers
- **`fisch_bilder/`** - Directory containing fish images (82 images)

### Data Flow

1. Fish data is stored in JSON format with question/answer structure
2. Images are fetched from DuckDuckGo search with quality validation (500x300px minimum)
3. PDF flashcards are generated with front-side images and back-side text
4. Data can be exported to CSV for import into other platforms (Repetico/Anki)

### Image Management System

- **Quality Control**: `shit.txt` contains fish names with unsatisfactory images
- **Smart Replacement**: Running `fetch.py` after adding entries to `shit.txt` searches for better alternatives
- **Duplicate Prevention**: Uses SHA-256 hashing and MSE similarity detection
- **Retry Logic**: 3 attempts with exponential backoff for failed image downloads

### Output Formats

- **PDF**: 20-page flashcard document with 8 cards per page (4x2 grid)
- **CSV**: Import format with German date normalization (DD.MM. bis DD.MM.)
- **JSON**: Various export formats for different platforms

## Key Patterns

- German language throughout (comments, output, data)
- RegEx-based parsing of fish information with fallback handling
- Modular design separating data processing from presentation
- Comprehensive error handling for web scraping and file operations

## Development Context

This is a specialized educational tool for German fishing enthusiasts. The codebase combines web scraping, image processing, and PDF generation to create study materials for fish identification and fishing regulations in Bavaria.