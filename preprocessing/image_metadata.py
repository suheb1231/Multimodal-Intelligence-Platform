
import json  # Metadata ko JSON format mein save karne ke liye.

from pathlib import Path  # Project folders aur file paths handle karne ke liye.

from datetime import datetime, timezone  # Processing ka UTC time record karne ke liye.


def create_image_metadata(image_info, extracted_text):  # Image information aur OCR text combine karne ke liye.

    asset_id = image_info["asset_id"]  # Image ki unique ID retrieve kar rahe hain.

    project_dir = Path(__file__).resolve().parent.parent  # Project ka main folder identify kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id  # Image ka processed data folder define kar rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)  # Folder missing hone par create kar rahe hain.

    metadata = {  # Final image metadata dictionary bana rahe hain.

        **image_info,  # Image ki saari basic information include kar rahe hain.

        "extracted_text": extracted_text,  # OCR se mila text add kar rahe hain.

        "processing_status": "completed",  # Processing successful hone ka status save kar rahe hain.

        "processed_at": datetime.now(timezone.utc).isoformat()  # Processing ka UTC timestamp save kar rahe hain.

    }

    output_path = output_dir / "metadata.json"  # Metadata JSON file ka path define kar rahe hain.

    with open(output_path, "w", encoding="utf-8") as file:  # JSON file write mode mein open kar rahe hain.

        json.dump(metadata, file, indent=4, ensure_ascii=False)  # Readable JSON format mein metadata save kar rahe hain.

    return metadata  # Final metadata return kar rahe hain.
