
import json  # Metadata ko JSON format mein save karne ke liye.
from pathlib import Path  # Project folders aur file paths handle karne ke liye.
from datetime import datetime, timezone  # Processing ka UTC time record karne ke liye.

def create_text_metadata(asset_id, segments):  # Text processing ki metadata create kar rahe hain.

    project_dir = Path(__file__).resolve().parent.parent  # Main project folder identify kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id  # Current text asset ka output folder select kar rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)  # Folder missing hone par create kar rahe hain.

    metadata = {  # Text asset ki complete metadata dictionary bana rahe hain.

        "asset_id": asset_id,  # Original text asset ki unique ID.

        "modality": "text",  # Asset ka type text define kar rahe hain.

        "total_segments": len(segments),  # Total processed segments count kar rahe hain.

        "source_file": segments[0]["source_file"] if segments else None,  # Original filename record kar rahe hain.

        "status": "preprocessed" if segments else "empty",  # Processing status record kar rahe hain.

        "segment_ids": [item["segment_id"] for item in segments],  # Sabhi segment IDs collect kar rahe hain.

        "processed_at": datetime.now(timezone.utc).isoformat()  # Processing ka UTC timestamp save kar rahe hain.
    }

    output_path = output_dir / "metadata.json"  # Metadata JSON file ka location define kar rahe hain.

    output_path.write_text(json.dumps(metadata, indent=4), encoding="utf-8")  # Metadata JSON file mein save kar rahe hain.

    return metadata  # Created metadata return kar rahe hain.
