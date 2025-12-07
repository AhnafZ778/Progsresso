from PIL import Image
import sys
import os


def crop_transparency(path, output_path):
    try:
        img = Image.open(path)
        img = img.convert("RGBA")

        # Get bounding box of non-zero alpha pixels
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            # Optional: Add a small margin? No, user wants it LARGE.
            img.save(output_path)
            print(f"Successfully cropped {path} to {output_path}")
        else:
            print("Image is completely transparent")
    except Exception as e:
        print(f"Error processing image: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python crop_image.py input_path output_path")
    else:
        crop_transparency(sys.argv[1], sys.argv[2])
