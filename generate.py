#!/usr/bin/env python3
"""
Schonzeiten Fish Flashcard Generator
Generates various formats (PDF, CSV, JSON) for Bavarian fish regulation study materials
"""

import os
import json
import requests
import time
import hashlib
import random
import re
from fpdf import FPDF
from PIL import Image
from io import BytesIO
from ddgs import DDGS
from PIL import ImageChops, ImageStat


class FishGenerator:
    def __init__(self):
        self.data_file = "data/fish_data.json"
        self.images_dir = "images/fish_images"
        self.output_dir = "output"
        self.config_dir = "config"
        self.poor_quality_file = f"{self.config_dir}/poor_quality_images.txt"
        
        # Ensure directories exist
        for dir_path in [self.images_dir, self.output_dir, self.config_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Load fish data
        with open(self.data_file, encoding="utf-8") as f:
            self.fish_data = json.load(f)
    
    def filter_fish_with_schonzeit(self):
        """Filter fish that have a Schonzeit (closed season) or Mindestmaß"""
        filtered = []
        for fish in self.fish_data:
            answer = fish["answer"]
            if ("Schonzeit:" in answer or "Mindestmaß:" in answer) and "Ganzjährig geschont" not in answer:
                filtered.append(fish)
        return filtered
    
    def filter_fish_ganzjaehrig_geschont(self):
        """Filter fish that are protected year-round (ganzjährig geschont)"""
        filtered = []
        for fish in self.fish_data:
            answer = fish["answer"]
            if "Ganzjährig geschont" in answer:
                filtered.append(fish)
        return filtered
    
    def load_poor_quality_list(self):
        """Load list of fish names that need image replacement"""
        if not os.path.exists(self.poor_quality_file):
            return []
        
        with open(self.poor_quality_file, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    
    def save_poor_quality_list(self, fish_list):
        """Save updated list of fish names that need image replacement"""
        with open(self.poor_quality_file, "w", encoding="utf-8") as f:
            for fish_name in fish_list:
                f.write(fish_name + "\n")
    
    def image_hash(self, img):
        """Generate SHA-256 hash of image for duplicate detection"""
        return hashlib.sha256(img.tobytes()).hexdigest()
    
    def image_diff(self, img1, img2):
        """Calculate Mean Square Error between two images"""
        diff = ImageChops.difference(img1, img2)
        stat = ImageStat.Stat(diff)
        mse = sum([v**2 for v in stat.mean]) / len(stat.mean)
        return mse
    
    def fetch_image(self, query, path, force_alternate=False):
        """Fetch fish image from DuckDuckGo with quality validation"""
        existing_img = None
        existing_hash = None
        
        if os.path.exists(path):
            try:
                existing_img = Image.open(path).convert("RGB")
                existing_hash = self.image_hash(existing_img)
            except:
                existing_img = None
                existing_hash = None
            if not force_alternate:
                return  # Image exists and not marked for replacement
        
        for attempt in range(3):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.images(query + " Fisch", max_results=10))
                    random.shuffle(results)  # Shuffle for variety
                    
                    for r in results:
                        try:
                            img_data = requests.get(r["image"], timeout=10).content
                            img = Image.open(BytesIO(img_data)).convert("RGB")
                            
                            # Quality check: minimum size requirement
                            if img.width < 500 or img.height < 300:
                                continue
                            
                            # Skip identical images
                            if existing_hash and self.image_hash(img) == existing_hash:
                                print(f"{query}: Identisches Bild – übersprungen")
                                continue
                            
                            # Skip very similar images
                            if existing_img:
                                mse = self.image_diff(img, existing_img)
                                if mse < 10:
                                    print(f"{query}: Zu ähnlich (MSE={mse:.2f}) – übersprungen")
                                    continue
                            
                            img.save(path)
                            print(f"✅ {query}: Neues Bild gespeichert")
                            return
                        except Exception:
                            continue
                
                raise Exception("Kein ausreichendes Bild gefunden.")
            except Exception as e:
                print(f"{query}: Fehler – Versuch {attempt+1}/3 – {e}")
                time.sleep(10 * (attempt + 1))
        
        print(f"⚠️ {query}: Kein neues Bild gefunden.")
    
    def generate_pdf(self, fish_data=None, filename="fish_flashcards.pdf"):
        """Generate PDF flashcards"""
        if fish_data is None:
            fish_data = self.fish_data
        
        print(f"Generiere PDF mit {len(fish_data)} Fischen...")
        
        # Load poor quality list
        poor_quality_list = self.load_poor_quality_list()
        replaced = []
        
        # PDF setup
        pdf = FPDF("P", "mm", "A4")
        pdf.set_auto_page_break(False)
        pdf.add_font("SF", "", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
        pdf.set_font("SF", size=14)
        
        card_w, card_h = 90, 60
        margin_x, margin_y = 10, 10
        
        # Generate flashcards
        for i in range(0, len(fish_data), 8):
            batch = fish_data[i:i+8]
            
            # Front side (images)
            pdf.add_page()
            for idx, entry in enumerate(batch):
                row, col = divmod(idx, 2)
                x = margin_x + col * (card_w + 10)
                y = margin_y + row * (card_h + 10)
                
                img_path = f"{self.images_dir}/{entry['question']}.jpg"
                force_alt = entry["question"] in poor_quality_list
                
                self.fetch_image(entry["question"], img_path, force_alternate=force_alt)
                
                if force_alt and os.path.exists(img_path):
                    replaced.append(entry["question"])
                
                if os.path.exists(img_path):
                    pdf.image(img_path, x+2, y+2, w=card_w-4, h=card_h-4)
                
                pdf.rect(x, y, card_w, card_h)
            
            # Back side (text, mirrored for double-sided printing)
            pdf.add_page()
            for idx, entry in enumerate(batch):
                row, col = divmod(idx, 2)
                col = 1 - col  # Mirror columns for double-sided printing
                x = margin_x + col * (card_w + 10)
                y = margin_y + row * (card_h + 10)
                
                pdf.set_xy(x + 2, y + 2)
                pdf.multi_cell(card_w - 4, 7, f"{entry['question']}\n\n{entry['answer']}")
                pdf.rect(x, y, card_w, card_h)
        
        # Save PDF
        output_path = f"{self.output_dir}/{filename}"
        pdf.output(output_path)
        print(f"✅ PDF erstellt: {output_path}")
        
        # Clean up poor quality list
        if replaced:
            updated_list = [name for name in poor_quality_list if name not in replaced]
            self.save_poor_quality_list(updated_list)
            print(f"🧽 Qualitätskontrolle bereinigt: {', '.join(replaced)}")
    
    def normalize_schonzeit(self, text):
        """Normalize German date format for Schonzeit"""
        match = re.search(r"(\d{2}\.\d{2})[–-](\d{2}\.\d{2})", text)
        if match:
            return f"{match.group(1)} bis {match.group(2)}"
        return text.strip().rstrip(".")
    
    def generate_csv(self, fish_data=None, filename="fish_data.csv"):
        """Generate CSV for import into flashcard systems"""
        if fish_data is None:
            fish_data = self.fish_data
        
        print(f"Generiere CSV mit {len(fish_data)} Fischen...")
        
        lines = []
        
        for entry in fish_data:
            name = entry["question"]
            answer = entry["answer"]
            schonzeit = ""
            mindestmass = ""
            fallback = ""
            
            if "Ganzjährig geschont" in answer:
                fallback = "Ganzjährig geschont"
            
            if "Schonzeit:" in answer:
                parts = answer.split("Schonzeit:")
                rest = parts[1].strip()
                if "," in rest:
                    schonzeit, _ = rest.split(",", 1)
                else:
                    schonzeit = rest.strip()
                schonzeit = self.normalize_schonzeit(schonzeit)
            
            if "Mindestmaß:" in answer:
                parts = answer.split("Mindestmaß:")
                rest = parts[1].strip()
                if "," in rest:
                    mindestmass, _ = rest.split(",", 1)
                else:
                    mindestmass = rest.strip()
            
            result = ""
            if schonzeit:
                result += f"Schonzeit: {schonzeit}"
            if mindestmass:
                if result:
                    result += "<br/>"
                result += f"Mindestmaß: {mindestmass.strip()}"
            if not result:
                result = fallback or "Keine Schonzeit oder Mindestmaß angegeben"
            
            line = f"{name},{result.strip()}"
            lines.append(line)
        
        output_path = f"{self.output_dir}/{filename}"
        with open(output_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        
        print(f"✅ CSV erstellt: {output_path}")
    
    def generate_repetico_json(self, fish_data=None, filename="repetico_export.json"):
        """Generate JSON format for Repetico flashcard system"""
        if fish_data is None:
            fish_data = self.fish_data
        
        print(f"Generiere Repetico JSON mit {len(fish_data)} Fischen...")
        
        repetico_data = []
        for entry in fish_data:
            # Convert newlines to proper format for Repetico
            answer = entry["answer"].replace(", ", "\n")
            repetico_entry = {
                "question": entry["question"],
                "answer": answer
            }
            repetico_data.append(repetico_entry)
        
        output_path = f"{self.output_dir}/{filename}"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(repetico_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Repetico JSON erstellt: {output_path}")
    
    def download_images_for_fish(self, fish_data, force_redownload=False):
        """Download images for a list of fish, standalone from PDF generation"""
        print(f"Lade Bilder für {len(fish_data)} Fische herunter...")
        
        poor_quality_list = self.load_poor_quality_list()
        replaced = []
        downloaded = 0
        skipped = 0
        
        for entry in fish_data:
            fish_name = entry["question"]
            img_path = f"{self.images_dir}/{fish_name}.jpg"
            
            # Determine if we should force alternate (better) image
            force_alt = fish_name in poor_quality_list or force_redownload
            
            # Check if image already exists and we're not forcing redownload
            if os.path.exists(img_path) and not force_alt:
                print(f"⏭️ {fish_name}: Bild bereits vorhanden")
                skipped += 1
                continue
            
            print(f"🔄 Lade Bild für {fish_name}...")
            self.fetch_image(fish_name, img_path, force_alternate=force_alt)
            
            # Track successful replacements for cleanup
            if force_alt and os.path.exists(img_path) and fish_name in poor_quality_list:
                replaced.append(fish_name)
            
            if os.path.exists(img_path):
                downloaded += 1
        
        # Clean up poor quality list for successfully replaced images
        if replaced:
            updated_list = [name for name in poor_quality_list if name not in replaced]
            self.save_poor_quality_list(updated_list)
            print(f"🧽 Qualitätskontrolle bereinigt: {', '.join(replaced)}")
        
        print(f"📊 Ergebnis: {downloaded} heruntergeladen, {skipped} übersprungen")
    
    def download_all_images(self, force_redownload=False):
        """Download images for all fish in the dataset"""
        self.download_images_for_fish(self.fish_data, force_redownload)
    
    def download_poor_quality_images(self):
        """Re-download only images marked as poor quality"""
        poor_quality_list = self.load_poor_quality_list()
        if not poor_quality_list:
            print("📂 Keine Bilder in der Qualitätskontrolle-Liste gefunden.")
            return
        
        print(f"Lade {len(poor_quality_list)} Bilder aus der Qualitätskontrolle-Liste neu...")
        
        # Filter fish data to only include those in poor quality list
        fish_to_redownload = [fish for fish in self.fish_data if fish["question"] in poor_quality_list]
        
        if fish_to_redownload:
            self.download_images_for_fish(fish_to_redownload, force_redownload=True)
        else:
            print("⚠️ Keine passenden Fische in der Datenbank gefunden.")


def handle_image_downloads(generator):
    """Handle image download submenu"""
    while True:
        print("\n🖼️ Bild-Download Optionen:")
        print("1. Alle Bilder herunterladen (nur fehlende)")
        print("2. Alle Bilder neu herunterladen (überschreibt vorhandene)")
        print("3. Nur schlechte Qualität ersetzen")
        print("4. Bilder für bestimmte Fischauswahl herunterladen")
        print("9. Zurück zum Hauptmenü")
        
        choice = input("\nBitte wählen (1-4, 9): ").strip()
        
        if choice == "9":
            break
        elif choice == "1":
            print("\n🔄 Lade fehlende Bilder für alle Fische...")
            generator.download_all_images(force_redownload=False)
        elif choice == "2":
            confirm = input("\n⚠️ Alle vorhandenen Bilder überschreiben? (j/N): ").strip().lower()
            if confirm in ["j", "ja", "y", "yes"]:
                print("\n🔄 Lade alle Bilder neu...")
                generator.download_all_images(force_redownload=True)
            else:
                print("Abgebrochen.")
        elif choice == "3":
            print("\n🔄 Ersetze Bilder schlechter Qualität...")
            generator.download_poor_quality_images()
        elif choice == "4":
            handle_selective_image_download(generator)
        else:
            print("❌ Ungültige Auswahl. Bitte versuchen Sie es erneut.")


def handle_selective_image_download(generator):
    """Handle selective image download for specific fish groups"""
    print("\nFür welche Fischgruppe sollen Bilder heruntergeladen werden?")
    print("1. Alle Fische")
    print("2. Nur ganzjährig geschont")
    print("3. Nur mit Schonzeit oder Mindestmaß")
    
    choice = input("\nBitte wählen (1-3): ").strip()
    
    selected_fish = None
    description = ""
    
    if choice == "1":
        selected_fish = generator.fish_data
        description = "alle Fische"
    elif choice == "2":
        selected_fish = generator.filter_fish_ganzjaehrig_geschont()
        description = "ganzjährig geschützte Fische"
    elif choice == "3":
        selected_fish = generator.filter_fish_with_schonzeit()
        description = "Fische mit Schonzeit/Mindestmaß"
    else:
        print("❌ Ungültige Auswahl.")
        return
    
    print(f"\nSollen vorhandene Bilder für {description} ({len(selected_fish)} Fische) überschrieben werden?")
    force = input("Bilder überschreiben? (j/N): ").strip().lower() in ["j", "ja", "y", "yes"]
    
    print(f"\n🔄 Lade Bilder für {description}...")
    generator.download_images_for_fish(selected_fish, force_redownload=force)


def main():
    generator = FishGenerator()
    
    print("🐟 Bayerische Fischarten - Schonzeiten Generator")
    print("=" * 50)
    
    while True:
        # Main menu
        print("\nHauptmenü:")
        print("1. Karteikarten/Dateien generieren")
        print("2. Fischbilder herunterladen")
        print("0. Beenden")
        
        main_choice = input("\nBitte wählen (0-2): ").strip()
        
        if main_choice == "0":
            print("Auf Wiedersehen!")
            break
        elif main_choice == "1":
            handle_content_generation(generator)
        elif main_choice == "2":
            handle_image_downloads(generator)
        else:
            print("❌ Ungültige Auswahl. Bitte versuchen Sie es erneut.")


def handle_content_generation(generator):
    """Handle content generation submenu (original functionality)"""
    while True:
        # First: Choose fish selection
        print("\nWelche Fische sollen berücksichtigt werden?")
        print("1. Alle Fische")
        print("2. Nur ganzjährig geschont")
        print("3. Nur mit Schonzeit oder Mindestmaß")
        print("9. Zurück zum Hauptmenü")
        
        fish_choice = input("\nBitte wählen (1-3, 9): ").strip()
        
        if fish_choice == "9":
            break
        
        # Determine fish dataset
        selected_fish = None
        fish_description = ""
        
        if fish_choice == "1":
            selected_fish = generator.fish_data
            fish_description = "alle Fische"
        elif fish_choice == "2":
            selected_fish = generator.filter_fish_ganzjaehrig_geschont()
            fish_description = "ganzjährig geschützte Fische"
            print(f"Gefiltert: {len(selected_fish)} ganzjährig geschützte Fische")
        elif fish_choice == "3":
            selected_fish = generator.filter_fish_with_schonzeit()
            fish_description = "Fische mit Schonzeit/Mindestmaß"
            print(f"Gefiltert: {len(selected_fish)} Fische mit Schonzeit oder Mindestmaß")
        else:
            print("❌ Ungültige Auswahl. Bitte versuchen Sie es erneut.")
            continue
        
        # Second: Choose output format
        print(f"\nWas möchten Sie für {fish_description} ({len(selected_fish)} Fische) generieren?")
        print("1. PDF Karteikarten")
        print("2. CSV für Repetico/Anki")
        print("3. JSON für Repetico")
        print("4. Alle Formate")
        print("9. Zurück zur Fischauswahl")
        
        format_choice = input("\nBitte wählen (1-4, 9): ").strip()
        
        if format_choice == "9":
            continue
        
        # Generate filename suffix
        if fish_choice == "1":
            suffix = "alle_fische"
        elif fish_choice == "2":
            suffix = "ganzjaehrig_geschont"
        elif fish_choice == "3":
            suffix = "schonzeit_mindestmass"
        
        if format_choice == "1":
            generator.generate_pdf(selected_fish, f"{suffix}_karteikarten.pdf")
        
        elif format_choice == "2":
            generator.generate_csv(selected_fish, f"{suffix}_repetico.csv")
        
        elif format_choice == "3":
            generator.generate_repetico_json(selected_fish, f"{suffix}_repetico.json")
        
        elif format_choice == "4":
            print("Generiere alle Formate...")
            generator.generate_pdf(selected_fish, f"{suffix}_karteikarten.pdf")
            generator.generate_csv(selected_fish, f"{suffix}_repetico.csv")
            generator.generate_repetico_json(selected_fish, f"{suffix}_repetico.json")
            print("✅ Alle Formate wurden generiert!")
        
        else:
            print("❌ Ungültige Auswahl. Bitte versuchen Sie es erneut.")


if __name__ == "__main__":
    main()