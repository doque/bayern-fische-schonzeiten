import os
import json
import requests
import time
from fpdf import FPDF
from PIL import Image
from io import BytesIO
from duckduckgo_search import DDGS

# Lade JSON-Daten
with open("bayern_fisch_schonzeiten_alle_80.json", encoding="utf-8") as f:
    data = json.load(f)

# Bildordner
os.makedirs("fisch_bilder", exist_ok=True)

# Unicode-sichere Textbereinigung für Standard-Font
def sanitize(text):
    return (
        text.replace("–", "-")
            .replace("„", '"')
            .replace("“", '"')
            .replace("’", "'")
            .replace("…", "...")
            .replace("ß", "ss")
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
    )

# Bildabruf mit optionalem 2. Ergebnis
import hashlib

def image_hash(img):
    """Returns SHA256 hash of image bytes"""
    return hashlib.sha256(img.tobytes()).hexdigest()

def fetch_image(query, path, force_alternate=False):
    if os.path.exists(path) and not force_alternate:
        return

    existing_hash = None
    if os.path.exists(path):
        try:
            existing_img = Image.open(path).convert("RGB")
            existing_hash = image_hash(existing_img)
        except Exception:
            existing_hash = None

    base_delay = 10
    attempts = 3
    for attempt in range(attempts):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.images(query + " Fisch", max_results=10))

                for i, r in enumerate(results):
                    url = r["image"]
                    try:
                        img_data = requests.get(url, timeout=10).content
                        img = Image.open(BytesIO(img_data)).convert("RGB")

                        if img.width < 500 or img.height < 300:
                            print(f"{query} [{i+1}]: Bild zu klein ({img.width}x{img.height})")
                            continue

                        candidate_hash = image_hash(img)
                        if existing_hash and candidate_hash == existing_hash:
                            print(f"{query} [{i+1}]: Bild identisch – übersprungen")
                            continue

                        img.save(path)
                        print(f"✅ {query}: Neues Bild gespeichert [{i+1}] ({img.width}x{img.height})")
                        return
                    except Exception as inner_e:
                        print(f"{query} [{i+1}]: Fehlerhaftes Bild – {inner_e}")
                        continue

                raise Exception("Kein geeignetes/neues Bild gefunden.")

        except Exception as e:
            delay = base_delay * (attempt + 1)
            print(f"Fehler bei {query} (Versuch {attempt+1}/3): {e} – warte {delay}s")
            time.sleep(delay)

    print(f"⚠️ Bild für {query} nach 3 Versuchen übersprungen.")

# Lade shit.txt
shitlist_path = "shit.txt"
if os.path.exists(shitlist_path):
    with open(shitlist_path, encoding="utf-8") as f:
        shitlist = [line.strip() for line in f if line.strip()]
else:
    shitlist = []

replaced = []

# PDF Setup
pdf = FPDF("P", "mm", "A4")
card_w, card_h = 90, 60
margin_x, margin_y = 10, 10

# Karteikarten erzeugen (8er-Gruppen)
for i in range(0, len(data), 8):
    batch = data[i:i+8]

    # Seite: Bilder
    pdf.add_page()
    for idx, entry in enumerate(batch):
        row, col = divmod(idx, 2)
        x = margin_x + col * (card_w + 10)
        y = margin_y + row * (card_h + 10)
        img_path = f"fisch_bilder/{entry['question']}.jpg"

        force_alt = entry["question"] in shitlist
        fetch_image(entry["question"], img_path, force_alternate=force_alt)
        if force_alt and os.path.exists(img_path):
            replaced.append(entry["question"])

        if os.path.exists(img_path):
            pdf.image(img_path, x+2, y+2, w=card_w-4, h=card_h-4)
        pdf.rect(x, y, card_w, card_h)

    # Seite: Rückseiten
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for idx, entry in enumerate(batch):
        row, col = divmod(idx, 2)
        x = margin_x + col * (card_w + 10)
        y = margin_y + row * (card_h + 10)
        pdf.set_xy(x + 2, y + 2)
        pdf.multi_cell(card_w - 4, 5, sanitize(f"{entry['question']}\n\n{entry['answer']}"))
        pdf.rect(x, y, card_w, card_h)

# Speichern
pdf.output("fisch_karteikarten.pdf")
print("✅ PDF erstellt: fisch_karteikarten.pdf")

# shit.txt aktualisieren
if replaced:
    remaining = [s for s in shitlist if s not in replaced]
    with open(shitlist_path, "w", encoding="utf-8") as f:
        f.write("\n".join(remaining))
    print(f"🧽 Aktualisierte shit.txt (entfernt: {', '.join(replaced)})")
else:
    print("ℹ️ Keine Einträge aus shit.txt ersetzt.")