
import json  # Discussion data read karne ke liye.
import re  # Extra spaces clean karne ke liye.
from pathlib import Path  # File paths handle karne ke liye.


def process_discussion(discussion_path, asset_id):  # Discussion preprocessing function.

    discussion_path = Path(discussion_path)  # File path convert kar rahe hain.

    if not discussion_path.exists():  # Check kar rahe hain file available hai ya nahi.
        raise FileNotFoundError(f"File not found: {discussion_path}")  # Missing file par error.

    data = json.loads(discussion_path.read_text(encoding="utf-8"))  # Discussion JSON read kar rahe hain.

    segments = []  # Processed discussions store karne ke liye.

    seen = set()  # Duplicate discussions track karne ke liye.

    for item in data["discussions"]:  # Har discussion process kar rahe hain.

        content = re.sub(r"\s+", " ", item["content"]).strip()  # Extra spaces remove kar rahe hain.

        if content and content.lower() not in seen:  # Empty aur duplicate content skip kar rahe hain.

            seen.add(content.lower())  # Content ko duplicate tracking mein add kar rahe hain.

            segments.append({
                "asset_id": asset_id,  # Original discussion asset ID.
                "segment_id": f"{asset_id}-DISC-{len(segments) + 1}",  # Unique segment ID.
                "source_file": discussion_path.name,  # Original filename.
                "author": item.get("author"),  # Discussion author record kar rahe hain.
                "content": content,  # Clean discussion content.
                "modality": "discussion"  # Asset modality define kar rahe hain.
            })

    return segments  # Processed discussion segments return kar rahe hain.
