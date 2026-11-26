
import json
# JSON file mein aligned data save karne ke liye library import kar rahe hain.

from pathlib import Path
# Output file ka location handle karne ke liye Path import kar rahe hain.


def align_frames_with_transcript(frames, transcript_segments, asset_id, interval_seconds=5):
    # Video frames aur transcript ko timestamps ke basis par connect kar rahe hain.

    aligned_data = []
    # Aligned information store karne ke liye empty list bana rahe hain.

    for frame in frames:
        # Har extracted video frame ko check kar rahe hain.

        frame_time = frame["timestamp_seconds"]
        # Frame ka timestamp already seconds mein hai, isliye conversion ki zaroorat nahi.
        

        window_end = frame_time + interval_seconds
        # Frame ke timestamp se agle 5 seconds ka time window bana rahe hain.

        matching_segments = []
        # Matching transcript segments store karne ke liye empty list bana rahe hain.

        for segment in transcript_segments:
            # Har transcript segment ko check kar rahe hain.

            if segment["start"] < window_end and segment["end"] >= frame_time:
                # Check kar rahe hain ki transcript aur video ka time overlap karta hai ya nahi.

                matching_segments.append({
                    "segment_id": segment["segment_id"],
                    # Transcript segment ki unique ID save kar rahe hain.

                    "start": segment["start"],
                    # Transcript ka starting timestamp save kar rahe hain.

                    "end": segment["end"],
                    # Transcript ka ending timestamp save kar rahe hain.

                    "text": segment["text"]
                    # Transcript ke spoken words save kar rahe hain.
                })
                # Matching transcript ki information list mein add kar rahe hain.

        aligned_data.append({
            "asset_id": asset_id,
            # Original video ki asset ID save kar rahe hain.

            "frame_id": frame["frame_id"],
            # Extracted frame ki unique ID save kar rahe hain.

            "timestamp": frame["timestamp_seconds"],
            # Frame ka timestamp seconds mein JSON mein save kar rahe hain.,
            # Video frame ka timestamp save kar rahe hain.

            "frame_path": frame["frame_path"],
            # Frame image ka location save kar rahe hain.

            "modality": "video_frame_transcript",
            # Aligned data ka modality type identify kar rahe hain.

            "transcript_segments": matching_segments,
            # Frame se related transcript segments save kar rahe hain.

            "status": "matched" if matching_segments else "no_transcript_match"
            # Match mila ya nahi, uska status save kar rahe hain.
        })
        # Current frame aur transcript ki combined information save kar rahe hain.

    project_dir = Path(__file__).resolve().parent.parent
    # Project ka main folder identify kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id
    # Aligned data save karne ka folder path bana rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)
    # Output folder nahi hai to automatically create kar rahe hain.

    output_file = output_dir / "alignment.json"
    # Alignment JSON file ka path bana rahe hain.

    with open(output_file, "w", encoding="utf-8") as file:
        # JSON file ko writing mode mein open kar rahe hain.

        json.dump(aligned_data, file, indent=4, ensure_ascii=False)
        # Aligned frames aur transcript ko readable JSON format mein save kar rahe hain.

    return aligned_data
    # Complete aligned data return kar rahe hain.
