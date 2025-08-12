import os
import json
import requests
import time
import hashlib
import random
from fpdf import FPDF
from PIL import Image
from io import BytesIO
from ddgs import DDGS
from PIL import ImageChops, ImageStat

# Lade JSON-Daten
with open("fische.json", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("fisch_bilder", exist_ok=True)

# Hash zum Vergleich von Bildern
def image_hash(img):
    return hashlib.sha256(img.tobytes()).hexdigest()

# DuckDuckGo Bildsuche mit Mindestgröße und Duplikatprüfung
def image_hash(img):
    return hashlib.sha256(img.tobytes()).hexdigest()

def image_diff(img1, img2):
    diff = ImageChops.difference(img1, img2)
    stat = ImageStat.Stat(diff)
    mse = sum([v**2 for v in stat.mean]) / len(stat.mean)
    return mse

def fetch_image(query, path, force_alternate=False):
    must_replace = force_alternate

    existing_img = None
    existing_hash = None
    if os.path.exists(path):
        try:
            existing_img = Image.open(path).convert("RGB")
            existing_hash = image_hash(existing_img)
        except:
            existing_img = None
            existing_hash = None
        if not must_replace:
            return  # not in shit.txt → skip

    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.images(query + " Fisch", max_results=10))
                random.shuffle(results)  # 💡 Shuffle for variety

                for r in results:
                    try:
                        img_data = requests.get(r["image"], timeout=10).content
                        img = Image.open(BytesIO(img_data)).convert("RGB")

                        if img.width < 500 or img.height < 300:
                            continue

                        if existing_hash and image_hash(img) == existing_hash:
                            print(f"{query}: identisches Bild – übersprungen")
                            continue

                        if existing_img:
                            mse = image_diff(img, existing_img)
                            if mse < 10:
                                print(f"{query}: zu ähnlich (MSE={mse:.2f}) – übersprungen")
                                continue

                        img.save(path)
                        print(f"✅ {query}: Neues Bild gespeichert")
                        return
                    except Exception as inner:
                        continue

                raise Exception("Kein ausreichendes Bild gefunden.")
        except Exception as e:
            print(f"{query}: Fehler – Versuch {attempt+1}/3 – {e}")
            time.sleep(10 * (attempt + 1))

    print(f"⚠️ {query}: Kein neues Bild gefunden.")

# shit.txt laden
shitlist = []
if os.path.exists("shit.txt"):
    with open("shit.txt", encoding="utf-8") as f:
        shitlist = [line.strip() for line in f if line.strip()]
replaced = []

# PDF-Setup
pdf = FPDF("P", "mm", "A4")
pdf.set_auto_page_break(False)
pdf.add_font("SF", "", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
pdf.set_font("SF", size=14)

card_w, card_h = 90, 60
margin_x, margin_y = 10, 10

# Karteikarten generieren
for i in range(0, len(data), 8):
    batch = data[i:i+8]

    # Vorderseite
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

    # Rückseite (gespiegelt für doppelseitigen Druck)
    pdf.add_page()
    for idx, entry in enumerate(batch):
        row, col = divmod(idx, 2)
        # Spalte spiegeln für doppelseitigen Druck
        col = 1 - col
        x = margin_x + col * (card_w + 10)
        y = margin_y + row * (card_h + 10)
        pdf.set_xy(x + 2, y + 2)
        pdf.multi_cell(card_w - 4, 7, f"{entry['question']}\n\n{entry['answer']}")
        pdf.rect(x, y, card_w, card_h)

# PDF speichern
pdf.output("fisch_karteikarten.pdf")
print("✅ PDF erstellt: fisch_karteikarten.pdf")

# shit.txt bereinigen
if replaced:
    with open("shit.txt", "w", encoding="utf-8") as f:
        for name in shitlist:
            if name not in replaced:
                f.write(name + "\n")
    print(f"🧽 shit.txt bereinigt: {', '.join(replaced)}")