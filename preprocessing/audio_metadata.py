
import json  # Metadata ko JSON format mein save karne ke liye.

from pathlib import Path  # Project folders aur file paths handle karne ke liye.

from datetime import datetime, timezone  # Processing ka UTC time record karne ke liye.


def create_audio_metadata(audio_path, asset_id, segments):  # Audio ki final metadata create karne ke liye.

    audio_path = Path(audio_path)  # Audio file ka path convert kar rahe hain.

    project_dir = Path(__file__).resolve().parent.parent  # Project ka main folder identify kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id  # Audio ka processed folder define kar rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)  # Folder missing hone par create kar rahe hain.

    metadata = {  # Final audio metadata dictionary bana rahe hain.

        "asset_id": asset_id,  # Audio ki unique ID save kar rahe hain.

        "source_file": audio_path.name,  # Original audio filename save kar rahe hain.

        "modality": "audio",  # Asset ki modality define kar rahe hain.

        "total_segments": len(segments),  # Total transcript segments count kar rahe hain.

        "segments": segments,  # Saare transcript segments aur timestamps save kar rahe hain.

        "processing_status": "completed",  # Processing status save kar rahe hain.

        "processed_at": datetime.now(timezone.utc).isoformat()  # Processing ka UTC timestamp save kar rahe hain.

    }

    output_path = output_dir / "metadata.json"  # Metadata JSON file ka path define kar rahe hain.

    with open(output_path, "w", encoding="utf-8") as file:  # JSON file write mode mein open kar rahe hain.

        json.dump(metadata, file, indent=4, ensure_ascii=False)  # Readable JSON format mein save kar rahe hain.

    return metadata  # Final metadata return kar rahe hain.
