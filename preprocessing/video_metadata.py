
import json
# Metadata ko JSON format mein save karne ke liye.

from pathlib import Path
# Project folders aur file paths handle karne ke liye.

from datetime import datetime, timezone
# Processing complete hone ka UTC time record karne ke liye.


def create_video_metadata(asset_id, frames, segments, aligned_data):
    # Video processing ke results se central metadata bana rahe hain.

    project_dir = Path(__file__).resolve().parent.parent
    # Project ka main folder identify kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id
    # Current video ke processed data ka folder select kar rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)
    # Folder missing hone par automatically create kar rahe hain.

    matched_frames = sum(
        1 for item in aligned_data if item["status"] == "matched"
    )
    # Kitne frames ke saath transcript match hua, uski counting kar rahe hain.

    unmatched_frames = len(aligned_data) - matched_frames
    # Kitne frames ke saath transcript match nahi hua, calculate kar rahe hain.

    metadata = {
        "asset_id": asset_id,
        # Original video ki unique ID save kar rahe hain.

        "modality": "video",
        # Asset ka type video identify kar rahe hain.

        "processing_status": "preprocessed",
        # Video preprocessing complete hone ka status save kar rahe hain.

        "total_frames": len(frames),
        # Total extracted frames ki counting save kar rahe hain.

        "total_transcript_segments": len(segments),
        # Total transcript segments ki counting save kar rahe hain.

        "total_aligned_frames": matched_frames,
        # Transcript se match hue frames ki counting save kar rahe hain.

        "unmatched_frames": unmatched_frames,
        # Transcript match nahi hue frames ki counting save kar rahe hain.

        "frame_interval_seconds": 5,
        # Frames extract karne ka interval record kar rahe hain.

        "source_file": frames[0]["source_file"] if frames else None,
        # Available frame metadata se original video filename le rahe hain.

        "processed_at": datetime.now(timezone.utc).isoformat()
        # Processing ka UTC date aur time save kar rahe hain.
    }
    # Video processing ki complete summary bana rahe hain.

    metadata_path = output_dir / "metadata.json"
    # Metadata JSON file ka output path bana rahe hain.

    with open(metadata_path, "w", encoding="utf-8") as file:
        # Metadata file ko writing mode mein open kar rahe hain.

        json.dump(metadata, file, indent=4, ensure_ascii=False)
        # Metadata ko readable JSON format mein save kar rahe hain.

    return metadata
    # Complete metadata dictionary return kar rahe hain.
