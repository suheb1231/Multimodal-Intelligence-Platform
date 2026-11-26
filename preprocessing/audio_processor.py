
from faster_whisper import WhisperModel
# Faster-Whisper se speech-to-text generate karne ke liye.

from pathlib import Path
# Audio file ka path handle karne ke liye.


model = WhisperModel("base", device="cpu", compute_type="int8")
# Base model CPU par load kar rahe hain.


def process_audio(audio_path, asset_id):
    # Audio processing function define kar rahe hain.

    audio_path = Path(audio_path)
    # Audio path ko Path object mein convert kar rahe hain.

    if not audio_path.exists():
        # Check kar rahe hain ki audio file available hai ya nahi.
        raise FileNotFoundError(f"Audio not found: {audio_path}")
        # File missing hone par error denge.

    segments, info = model.transcribe(str(audio_path), language="en")
    # Audio ko transcript segments mein convert kar rahe hain.

    segments_data = []
    # Transcript segments store karne ke liye list.

    for index, segment in enumerate(segments, start=1):
        # Har transcript segment read kar rahe hain.

        segments_data.append({
            # Segment ki structured information save kar rahe hain.

            "asset_id": asset_id,
            # Original audio ki unique ID.

            "source_file": audio_path.name,
            # Original audio filename.

            "modality": "audio",
            # Asset ki modality define kar rahe hain.

            "segment_id": f"{asset_id}-SEG-{index}",
            # Unique segment ID bana rahe hain.

            "start_time": segment.start,
            # Segment ka starting timestamp.

            "end_time": segment.end,
            # Segment ka ending timestamp.

            "text": segment.text.strip()
            # Recognized speech text save kar rahe hain.
        })

    return segments_data
    # Saare transcript segments return kar rahe hain.
