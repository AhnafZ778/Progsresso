import os
from rembg import remove

ICONS_DIR = "static/icons"
BRAIN_DIR = "/home/ahnaf-bin-zakaria/.gemini/antigravity/brain/464ef7f4-ad55-400f-a5e1-5704d4edca62"

# Mapping user uploads to filenames based on sequence provided
# 0 -> Sleepy (Fix)
# 1 -> Gate 2
# 2 -> Gate 3 (Replacement)
# 3 -> Gate 4
UPLOAD_MAPPING = {
    "uploaded_image_0_1764933466739.png": "icon_rock_lee_sleepy.png",
    "uploaded_image_1_1764933466739.png": "icon_rock_lee_gate2.png",
    "uploaded_image_2_1764933466739.png": "icon_rock_lee_gate3.png",
    "uploaded_image_3_1764933466739.png": "icon_rock_lee_gate4.png",
}


def process_uploads():
    print("Starting background removal for uploaded icons...")

    for source_filename, final_name in UPLOAD_MAPPING.items():
        source_path = os.path.join(BRAIN_DIR, source_filename)
        dest_path = os.path.join(ICONS_DIR, final_name)

        if not os.path.exists(source_path):
            print(f"Skipping {final_name}: Source {source_path} not found.")
            continue

        print(f"Processing {final_name} from {source_filename}...")
        try:
            with open(source_path, "rb") as i:
                input_data = i.read()
                output_data = remove(input_data)

            with open(dest_path, "wb") as o:
                o.write(output_data)

            print(f"Successfully saved to {dest_path}")
        except Exception as e:
            print(f"Failed to process {final_name}: {e}")


if __name__ == "__main__":
    process_uploads()
