
from uuid import uuid4


def create_text_chunks(
    pages,
    asset_id,
    chunk_size=500,
    overlap=50
):

    chunks = []

    for page in pages:

        text = page["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({

                    "chunk_id": str(uuid4()),

                    "asset_id": asset_id,

                    "source_file": page["source_file"],

                    "segment_id": page.get("segment_id"),

                    "page_number": page.get("page_number"),

                    "modality": page.get("modality", "document"),

                    "chunk_text": chunk_text

                })

            start = end - overlap

    return chunks
