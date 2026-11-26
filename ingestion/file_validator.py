import json
from pathlib import Path

# Supported file formats  (.json = quiz ya discussion, content dekh kar decide hota hai)
SUPPORTED_FORMATS = {
    ".mp4": "video",
    ".mov": "video",
    ".mp3": "audio",
    ".wav": "audio",
    ".aac": "audio",
    ".m4a": "audio",
    ".pdf": "document",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".txt": "text",
    ".json": "json",
}

# Maximum file size: 200 MB
MAX_FILE_SIZE = 200 * 1024 * 1024


def _detect_json_modality(file_path):
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if isinstance(data, dict):
        if "questions" in data:
            return "quiz"
        if "discussions" in data:
            return "discussion"
    return None


def validate_file(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        return False, "File does not exist", None

    if not file_path.is_file():
        return False, "Path is not a file", None

    extension = file_path.suffix.lower()
    if extension not in SUPPORTED_FORMATS:
        return False, "Unsupported file format", None

    size = file_path.stat().st_size
    if size == 0:
        return False, "File is empty", None
    if size > MAX_FILE_SIZE:
        return False, "File exceeds 200 MB limit", None

    modality = SUPPORTED_FORMATS[extension]

    if modality == "json":
        modality = _detect_json_modality(file_path)
        if modality is None:
            return False, "JSON must contain a 'questions' (quiz) or 'discussions' list", None

    return True, "File validation successful", modality