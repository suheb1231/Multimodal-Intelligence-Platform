
import json  # Metadata JSON mein save karne ke liye.
from pathlib import Path  # Folder aur file paths handle karne ke liye.
from datetime import datetime, timezone  # UTC timestamp record karne ke liye.


def create_discussion_metadata(asset_id, segments):  # Discussion metadata function.

    project_dir = Path(__file__).resolve().parent.parent  # Main project folder identify kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id  # Discussion output folder select kar rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)  # Folder create kar rahe hain.

    metadata = {
        "asset_id": asset_id,  # Discussion asset ki unique ID.
        "modality": "discussion",  # Asset type.
        "total_segments": len(segments),  # Total unique discussions.
        "source_file": segments[0]["source_file"] if segments else None,  # Original filename.
        "status": "preprocessed" if segments else "empty",  # Processing status.
        "segment_ids": [item["segment_id"] for item in segments],  # Sabhi segment IDs.
        "processed_at": datetime.now(timezone.utc).isoformat()  # UTC processing time.
    }

    output_path = output_dir / "metadata.json"  # Metadata file location.

    output_path.write_text(json.dumps(metadata, indent=4), encoding="utf-8")  # JSON file save.

    return metadata  # Metadata return kar rahe hain.
