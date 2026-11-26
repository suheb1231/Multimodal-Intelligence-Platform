from faster_whisper import WhisperModel
from pathlib import Path
from uuid import uuid4

_MODELS = {}  # Model ek hi baar load hoga (pehle har video par dobara load hota tha)


def _get_model(size):
    if size not in _MODELS:
        _MODELS[size] = WhisperModel(size, device="cpu", compute_type="int8")
    return _MODELS[size]


def transcribe_video(video_path, asset_id, language=None, model_size="base"):
    """language: 'en' / 'hi' ... (None = auto-detect). model_size: tiny/base/small/medium."""
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError("Video file not found")

    project_dir = Path(__file__).resolve().parent.parent
    output_dir = project_dir / "data" / "processed" / asset_id / "transcripts"
    output_dir.mkdir(parents=True, exist_ok=True)

    segments, info = _get_model(model_size).transcribe(
        str(video_path),
        beam_size=5,
        vad_filter=True,
        language=language,
    )

    transcript_segments = []
    for segment in segments:
        transcript_segments.append({
            "segment_id": f"SEG-{uuid4().hex[:8]}",
            "asset_id": asset_id,
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
            "modality": "video_transcript",
        })

    with open(output_dir / "transcript.txt", "w", encoding="utf-8") as file:
        for segment in transcript_segments:
            file.write(f"[{segment['start']} - {segment['end']}] {segment['text']}\n")

    return transcript_segments