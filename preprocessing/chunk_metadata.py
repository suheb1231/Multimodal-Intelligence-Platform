
import json  # Chunk metadata ko JSON mein save karne ke liye.
from pathlib import Path  # File aur folder paths handle karne ke liye.
from datetime import datetime, timezone  # UTC processing time record karne ke liye.


def create_chunk_metadata(asset_id, chunks):

    # Main project folder identify kar rahe hain.
    project_dir = Path(__file__).resolve().parent.parent

    # Current asset ka processed folder select kar rahe hain.
    output_dir = project_dir / "data" / "processed" / asset_id

    # Folder missing hone par create kar rahe hain.
    output_dir.mkdir(parents=True, exist_ok=True)

    # Chunk metadata dictionary create kar rahe hain.
    metadata = {

        "asset_id": asset_id,  # Original asset ki unique ID.

        "modality": "document",  # Chunk ka content type.

        "total_chunks": len(chunks),  # Total chunks count.

        "source_file": chunks[0]["source_file"] if chunks else None,  # Original filename.

        "chunk_ids": [item["chunk_id"] for item in chunks],  # All chunk IDs.

        "page_numbers": sorted(set(
            item["page_number"] for item in chunks
        )),  # Unique source page numbers.

        "status": "chunked" if chunks else "empty",  # Chunking status.

        "created_at": datetime.now(timezone.utc).isoformat()  # UTC timestamp.
    }

    # Metadata JSON file ka path define kar rahe hain.
    output_path = output_dir / "chunk_metadata.json"

    # Metadata ko JSON file mein save kar rahe hain.
    output_path.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8"
    )

    # Created metadata return kar rahe hain.
    return metadata
