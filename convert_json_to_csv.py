import json
import re

def normalize_schonzeit(text):
    match = re.search(r"(\d{2}\.\d{2})[–-](\d{2}\.\d{2})", text)
    if match:
        return f"{match.group(1)} bis {match.group(2)}"
    return text.strip().rstrip(".")

def convert_to_target_csv(input_file, output_file):
    with open(input_file, encoding="utf-8") as f:
        full_data = json.load(f)

    lines = []

    for entry in full_data:
        name = entry["question"]
        answer = entry["answer"]
        schonzeit = ""
        mass = ""
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
            schonzeit = normalize_schonzeit(schonzeit)

        if "Mindestmaß:" in answer:
            parts = answer.split("Mindestmaß:")
            rest = parts[1].strip()
            if "," in rest:
                mass, _ = rest.split(",", 1)
            else:
                mass = rest.strip()

        result = ""
        if schonzeit:
            result += f"Schonzeit: {schonzeit}"
        if mass:
            if result:
                result += "<br/>"
            result += f"Mindestmaß: {mass.strip()}"
        if not result:
            result = fallback or "Keine Schonzeit oder Mindestmaß angegeben"

        line = f"{name},{result.strip()}"
        lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python convert_json_to_csv.py input.json output.csv")
    else:
        convert_to_target_csv(sys.argv[1], sys.argv[2])