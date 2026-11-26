"""Unnecessary files hatane ki script.

    python cleanup.py            -> sirf list dikhata hai (kuch delete nahi karta)
    python cleanup.py --apply    -> files ko  _removed/<time>/  folder mein MOVE karta hai
                                    (permanent delete nahi, wapas laa sakte ho)
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent

TARGETS = {
    "1. Duplicate / audit dumps": [
        "complete_project_audit.txt",
        "project_source_audit.txt",
    ],
    "2. Unused code (kahin import nahi hota)": [
        "embeddings",                      # CLIP + MiniLM, FAISS pipeline mein use nahi
        "rag/embedding_generator.py",      # vector_store.py already embeddings deta hai
    ],
    "3. Purane dashboard pages (naye app.py ne replace kiye)": [
        "dashboard",
    ],
    "4. Test data (registry + index saath mein reset hote hain)": [
        "data/processed",
        "data/uploads",
        "data/asset_registry.db",
        "data/vector_store",
        "data/faiss_db",
    ],
}


def main():
    apply = "--apply" in sys.argv
    dest_root = BASE / "_removed" / datetime.now().strftime("%Y%m%d_%H%M%S")
    found = []

    for title, items in TARGETS.items():
        print(f"\n{title}")
        for rel in items:
            p = BASE / rel
            print(f"   {'FOUND  ' if p.exists() else 'missing'}  {rel}")
            if p.exists():
                found.append(p)

    caches = [p for p in BASE.rglob("__pycache__") if "_removed" not in p.parts and ".venv" not in p.parts]
    print(f"\n5. __pycache__ folders: {len(caches)}")
    found += caches

    if not apply:
        print("\n(Dry run) Kuch nahi hataya. Hatane ke liye:  python cleanup.py --apply")
        return

    for p in found:
        target = dest_root / p.relative_to(BASE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(target))
    print(f"\nDone. {len(found)} items move hue -> {dest_root}")


if __name__ == "__main__":
    main()