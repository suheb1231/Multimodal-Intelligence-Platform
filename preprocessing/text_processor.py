
import re  # Text cleaning ke liye.

from pathlib import Path  # Text file ka path handle karne ke liye.


def process_text(text_path, asset_id):  # Text preprocessing function define kar rahe hain.

    text_path = Path(text_path)  # File path ko Path object mein convert kar rahe hain.

    if not text_path.exists():  # Check kar rahe hain ki text file available hai ya nahi.
        raise FileNotFoundError(f"Text file not found: {text_path}")  # Missing file par error denge.

    content = text_path.read_text(encoding="utf-8")  # Text file ka content read kar rahe hain.

    content = re.sub(r"\s+", " ", content).strip()  # Extra spaces aur line breaks clean kar rahe hain.

    paragraphs = re.split(r"(?<=[.!?])\s+", content)  # Sentences ko separate segments mein divide kar rahe hain.

    segments = []  # Clean text segments store karne ke liye list bana rahe hain.

    seen = set()  # Duplicate sentences track karne ke liye set bana rahe hain.

    for sentence in paragraphs:  # Har sentence ko process kar rahe hain.

        sentence = sentence.strip()  # Sentence ke extra spaces remove kar rahe hain.

        if sentence and sentence.lower() not in seen:  # Empty aur duplicate sentences skip kar rahe hain.

            seen.add(sentence.lower())  # Sentence ko duplicate tracking mein add kar rahe hain.

            segments.append({  # Structured text segment bana rahe hain.

                "asset_id": asset_id,  # Original asset ki unique ID.

                "source_file": text_path.name,  # Original text filename.

                "modality": "text",  # Asset ki modality define kar rahe hain.

                "segment_id": f"{asset_id}-SEG-{len(segments) + 1}",  # Unique segment ID bana rahe hain.

                "text": sentence  # Clean sentence save kar rahe hain.

            })

    return segments  # Saare clean segments return kar rahe hain.
