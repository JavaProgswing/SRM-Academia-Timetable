import json
import os
from srmtimetable.utils import save_base64_image
from srmtimetable.timetable_generator import generate

if __name__ == "__main__":
    # Load JSON data from files
    with open("data/timetable.json", "r") as f:
        timetable_data = json.load(f)["data"]

    output = generate(timetable_data)

    os.makedirs("t_data", exist_ok=True)
    # Save combined image
    if output["combined"]:
        save_base64_image(output["combined"], "t_data/timetable_combined.png")

    # Save individual D/Os
    for entry in output["individual"]:
        do_num = entry["do"]
        save_base64_image(entry["image"], f"t_data/timetable_do{do_num}.png")

    # Save full JSON output
    with open("t_data/timetable_base64.json", "w") as f:
        json.dump(output, f, indent=2)

    print("Timetables saved to /t_data")
    # This script generates the timetable images and saves them to the t_data directory.
    # Make sure to run this after extractor_test.py to generate the necessary JSON files.
