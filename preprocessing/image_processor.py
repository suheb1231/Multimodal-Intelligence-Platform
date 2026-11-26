

from PIL import Image  # Image open aur process karne ke liye.

from pathlib import Path  # Image file ka path handle karne ke liye.

def process_image(image_path, asset_id):  # Image processing function define kar rahe hain.

    image_path = Path(image_path)  # Image path ko Path object mein convert kar rahe hain.

    if not image_path.exists():  # Check kar rahe hain ki image file exist karti hai ya nahi.
        raise FileNotFoundError(f"Image not found: {image_path}")  # File missing hone par error denge.

    with Image.open(image_path) as image:  # Image ko safely open kar rahe hain.

        image_info = {  # Image ki basic information collect kar rahe hain.

            "asset_id": asset_id,  # Image ki unique asset ID save kar rahe hain.

            "source_file": image_path.name,  # Original image ka filename save kar rahe hain.

            "modality": "image",  # Asset ki modality image define kar rahe hain.

            "format": image.format,  # Image ka format JPEG, PNG etc. collect kar rahe hain.

            "width": image.width,  # Image ki width pixels mein collect kar rahe hain.

            "height": image.height,  # Image ki height pixels mein collect kar rahe hain.

            "mode": image.mode,  # Image ka color mode RGB, RGBA etc. collect kar rahe hain.

        }

    return image_info  # Collected image information return kar rahe hain.
