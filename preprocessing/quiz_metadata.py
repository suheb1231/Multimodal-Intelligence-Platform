
import json  # Metadata ko JSON mein save karne ke liye.
from pathlib import Path  # Folder aur file paths handle karne ke liye.
from datetime import datetime, timezone  # UTC timestamp record karne ke liye.


def create_quiz_metadata(asset_id, questions):  # Quiz metadata function.

    project_dir = Path(__file__).resolve().parent.parent  # Main project folder identify kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id  # Quiz output folder select kar rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)  # Folder create kar rahe hain.

    metadata = {
        "asset_id": asset_id,  # Quiz ki unique ID.
        "modality": "quiz",  # Asset type.
        "total_questions": len(questions),  # Total unique questions.
        "source_file": questions[0]["source_file"] if questions else None,  # Original filename.
        "status": "preprocessed" if questions else "empty",  # Processing status.
        "segment_ids": [item["segment_id"] for item in questions],  # Question IDs.
        "processed_at": datetime.now(timezone.utc).isoformat()  # UTC processing time.
    }

    output_path = output_dir / "metadata.json"  # Metadata file location.

    output_path.write_text(json.dumps(metadata, indent=4), encoding="utf-8")  # JSON save kar rahe hain.

    return metadata  # Metadata return kar rahe hain.
