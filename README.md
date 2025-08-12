# Schonzeiten - Fish Learning Flashcards

A Python application that generates study flashcards for learning fish species, their closed seasons (Schonzeiten), and minimum sizes according to Bavarian fishing regulations.

## Features

- **PDF Flashcard Generation**: Creates printable flashcards with fish images on front and regulation details on back
- **Automatic Image Fetching**: Downloads fish images from DuckDuckGo with quality validation
- **Smart Image Management**: Prevents duplicates and allows replacement of poor-quality images
- **Multiple Export Formats**: Supports PDF and CSV export for different learning platforms
- **Double-sided Print Optimization**: Cards are positioned correctly for double-sided printing and cutting

## Requirements

- Python 3.7+
- Internet connection (for image fetching)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd schonzeiten
   ```

2. **Install required packages:**
   ```bash
   pip install fpdf2 pillow duckduckgo_search requests openai pygame PyMuPDF numpy
   ```

## Usage

### Generate PDF Flashcards

```bash
python fetch.py
```

This will:
- Load fish data from `fische.json`
- Fetch fish images from DuckDuckGo (if not already downloaded)
- Generate `fisch_karteikarten.pdf` with flashcards optimized for double-sided printing

### Convert Data to CSV

```bash
python convert_json_to_csv.py input.json output.csv
```

Converts JSON fish data to CSV format for import into flashcard applications like Anki or Repetico.

## Data Structure

### Input Data (`fische.json`)
The main data file contains fish information in the following format:
```json
[
  {
    "question": "Aal",
    "answer": "Schonzeit: 01.12.–28.02., Mindestmaß: 50 cm, Einzugsgebiet: D/E/R/W. Description..."
  }
]
```

### Output Files
- **`fisch_karteikarten.pdf`**: 20-page PDF with 8 flashcards per page (4×2 grid)
- **`import.csv`**: CSV format with normalized German date formats
- **`fisch_bilder/`**: Directory containing downloaded fish images

## Image Quality Management

### Automatic Image Fetching
- Images are automatically downloaded with minimum size requirements (500×300px)
- Duplicate detection using SHA-256 hashing
- Similar image detection using Mean Square Error (MSE)

### Manual Quality Control
1. Add fish names with poor images to `shit.txt` (one per line)
2. Run `python fetch.py` again
3. The script will search for better alternatives
4. Successfully replaced images are automatically removed from `shit.txt`

Example `shit.txt`:
```
Aal
Barsch
Hecht
```

## Double-sided Printing

The PDF is optimized for double-sided printing:
1. Print the PDF double-sided (flip on long edge)
2. Cut along the card boundaries
3. Each card will have the fish image on one side and regulation details on the other

## Project Structure

```
schonzeiten/
├── fetch.py                 # Main flashcard generator
├── convert_json_to_csv.py   # Data conversion utility
├── fische.json             # Fish data (321 entries)
├── shit.txt                # List of fish needing better images
├── fisch_bilder/           # Downloaded fish images (auto-generated)
├── fisch_karteikarten.pdf  # Generated flashcards (auto-generated)
└── import.csv              # CSV export (auto-generated)
```

## Configuration

- **Card Size**: 90×60mm (configured in `fetch.py`)
- **Image Requirements**: Minimum 500×300px
- **Retry Logic**: 3 attempts with exponential backoff for failed downloads
- **Font**: Arial Unicode (system font)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with a small subset of data
5. Submit a pull request

## License

This project is designed for educational purposes to help learn Bavarian fishing regulations.

## Troubleshooting

- **Missing images**: Check internet connection and try running `fetch.py` again
- **PDF generation fails**: Ensure Arial Unicode font is available on your system
- **Poor image quality**: Add fish names to `shit.txt` and regenerate