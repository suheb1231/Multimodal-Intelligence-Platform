"""Pipeline: upload -> validate -> preprocess -> chunk -> FAISS index -> ask.

This file wires the project's modules together. Heavy libraries (Whisper, OpenCV, OCR)
are imported lazily so the app starts fast.
"""
import json
import re
import shutil
from pathlib import Path
from uuid import uuid4

from config import BASE_DIR, UPLOAD_DIR, PROCESSED_DIR
from ingestion.asset_registry import (
    check_asset_permission,
    delete_asset,
    get_all_assets,
    update_asset_status,
)

VECTOR_PATH = BASE_DIR / "data" / "vector_store"
UPLOAD_TYPES = ["mp4", "mov", "mp3", "wav", "aac", "m4a", "pdf",
                "png", "jpg", "jpeg", "txt", "json"]

FULL_CONTEXT_CHARS = 45000   # files smaller than this are sent to the LLM whole
NOT_FOUND = "I couldn't find this in the selected material."


# ============================================================ upload helpers
def save_upload(uploaded_file):
    """Save an upload to data/uploads (adds a short suffix if the name already exists)."""
    name = Path(uploaded_file.name).name
    path = UPLOAD_DIR / name
    if path.exists():
        path = UPLOAD_DIR / f"{path.stem}_{uuid4().hex[:6]}{path.suffix}"
    path.write_bytes(uploaded_file.getbuffer())
    return path


def visible_assets(user):
    return [a for a in get_all_assets() if check_asset_permission(a[0], user)]


# ============================================================ preprocessing
def _seg(asset_id, text, modality, source, start=None, end=None, page=None, segment_id=None):
    return {
        "asset_id": asset_id,
        "segment_id": segment_id or f"{asset_id}-{uuid4().hex[:6]}",
        "source_file": source,
        "modality": modality,
        "text": (text or "").strip(),
        "start": start,
        "end": end,
        "page": page,
    }


def _extract(asset_id, path, modality, interval, language, model_size, log):
    """Run the right preprocessor for the modality and return normalized segments."""
    name = path.name

    if modality == "video":
        from preprocessing.video_processor import extract_video_frames
        from preprocessing.transcript_processor import transcribe_video
        from preprocessing.video_aligner import align_frames_with_transcript
        from preprocessing.video_metadata import create_video_metadata
        log("Extracting video frames...")
        frames = extract_video_frames(path, asset_id, interval)
        log("Transcribing speech with Whisper...")
        segs = transcribe_video(path, asset_id, language=language, model_size=model_size)
        aligned = align_frames_with_transcript(frames, segs, asset_id, interval)
        create_video_metadata(asset_id, frames, segs, aligned)
        return [_seg(asset_id, s["text"], "video", name, s["start"], s["end"],
                     segment_id=s["segment_id"]) for s in segs]

    if modality == "audio":
        from preprocessing.audio_processor import process_audio
        from preprocessing.audio_metadata import create_audio_metadata
        log("Transcribing audio...")
        segs = process_audio(path, asset_id)
        create_audio_metadata(path, asset_id, segs)
        return [_seg(asset_id, s["text"], "audio", name, s["start_time"], s["end_time"],
                     segment_id=s["segment_id"]) for s in segs]

    if modality == "document":
        from preprocessing.pdf_processor import extract_pdf_pages
        from preprocessing.pdf_metadata import create_pdf_metadata
        log("Reading PDF pages...")
        pages = extract_pdf_pages(path, asset_id)
        create_pdf_metadata(path, asset_id, pages)
        return [_seg(asset_id, p["text"], "pdf", name, page=p["page_number"],
                     segment_id=p["segment_id"]) for p in pages if p["has_text"]]

    if modality == "image":
        from preprocessing.image_processor import process_image
        from preprocessing.image_ocr import extract_image_text
        from preprocessing.image_metadata import create_image_metadata
        log("Running OCR on the image...")
        info = process_image(path, asset_id)
        text = extract_image_text(path)
        create_image_metadata(info, text)
        if not text:
            raise ValueError("OCR found no text in this image (is Tesseract installed?).")
        return [_seg(asset_id, text, "image", name, segment_id=f"{asset_id}-IMG-1")]

    if modality == "text":
        from preprocessing.text_processor import process_text
        from preprocessing.text_metadata import create_text_metadata
        log("Cleaning text...")
        segs = process_text(path, asset_id)
        create_text_metadata(asset_id, segs)
        return [_seg(asset_id, s["text"], "text", name, segment_id=s["segment_id"]) for s in segs]

    if modality == "quiz":
        from preprocessing.quiz_processor import process_quiz
        from preprocessing.quiz_metadata import create_quiz_metadata
        log("Processing quiz file...")
        qs = process_quiz(path, asset_id)
        create_quiz_metadata(asset_id, qs)
        return [_seg(asset_id,
                     f"Question: {q['question']} Options: {', '.join(map(str, q['options']))} "
                     f"Correct answer: {q['correct_answer']}",
                     "quiz", name, segment_id=q["segment_id"]) for q in qs]

    if modality == "discussion":
        from preprocessing.discussion_processor import process_discussion
        from preprocessing.discussion_metadata import create_discussion_metadata
        log("Processing discussion thread...")
        segs = process_discussion(path, asset_id)
        create_discussion_metadata(asset_id, segs)
        return [_seg(asset_id, f"{s['author']}: {s['content']}", "discussion", name,
                     segment_id=s["segment_id"]) for s in segs]

    raise ValueError(f"Unsupported modality: {modality}")


# ============================================================ chunking + index
def _group(segments, max_chars=700):
    """Merge tiny transcript/text segments so each chunk carries enough context."""
    groups, cur = [], None
    for s in segments:
        can_merge = (
            cur is not None
            and s["modality"] in ("video", "audio", "text")
            and s["modality"] == cur["modality"]
            and len(cur["text"]) + len(s["text"]) + 1 <= max_chars
        )
        if can_merge:
            cur["text"] += " " + s["text"]
            cur["end"] = s["end"]
        else:
            cur = dict(s)
            groups.append(cur)
    return groups


def _make_chunks(asset_id, segments):
    from preprocessing.text_chunker import create_text_chunks
    chunks = []
    for g in _group(segments):
        page_like = {
            "text": g["text"], "source_file": g["source_file"],
            "segment_id": g["segment_id"], "page_number": g["page"],
            "modality": g["modality"],
        }
        for c in create_text_chunks([page_like], asset_id, chunk_size=900, overlap=80):
            c["start"], c["end"] = g["start"], g["end"]   # keep timestamps for citations
            chunks.append(c)
    return chunks


def index_chunks(chunks):
    from rag.vector_store import create_vector_store, load_vector_store, save_vector_store
    VECTOR_PATH.mkdir(parents=True, exist_ok=True)
    if (VECTOR_PATH / "index.faiss").exists():
        store = load_vector_store(str(VECTOR_PATH))
        store.add_texts(
            [c["chunk_text"] for c in chunks],
            metadatas=[{k: v for k, v in c.items() if k != "chunk_text"} for c in chunks],
        )
    else:
        store = create_vector_store(chunks)
    save_vector_store(store, str(VECTOR_PATH))


def remove_from_index(asset_id):
    if not (VECTOR_PATH / "index.faiss").exists():
        return
    from rag.vector_store import load_vector_store, save_vector_store
    store = load_vector_store(str(VECTOR_PATH))
    ids = [i for i, d in store.docstore._dict.items() if d.metadata.get("asset_id") == asset_id]
    if ids:
        store.delete(ids)
        save_vector_store(store, str(VECTOR_PATH))


def process_asset(asset_id, file_path, modality, interval=5, language=None,
                  model_size="base", log=print):
    from preprocessing.chunk_metadata import create_chunk_metadata
    file_path = Path(file_path)
    out_dir = PROCESSED_DIR / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)
    update_asset_status(asset_id, "processing")
    try:
        segments = _extract(asset_id, file_path, modality, interval, language, model_size, log)
        segments = [s for s in segments if s["text"]]
        if not segments:
            raise ValueError("No readable text was found in this file.")
        (out_dir / "segments.json").write_text(
            json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8")
        log("Creating chunks and indexing...")
        chunks = _make_chunks(asset_id, segments)
        create_chunk_metadata(asset_id, chunks)
        index_chunks(chunks)
        update_asset_status(asset_id, "indexed")
        return {"segments": len(segments), "chunks": len(chunks)}
    except Exception:
        update_asset_status(asset_id, "failed")
        raise


def delete_asset_completely(asset_id):
    """Remove the registry row, upload, processed folder and FAISS chunks."""
    remove_from_index(asset_id)
    shutil.rmtree(PROCESSED_DIR / asset_id, ignore_errors=True)
    return delete_asset(asset_id)


# ============================================================ Ask AI engine
STOP = {
    "the", "and", "for", "are", "was", "were", "with", "that", "this", "from", "what", "how",
    "why", "who", "when", "where", "which", "does", "did", "can", "could", "would", "should",
    "about", "into", "than", "then", "them", "they", "you", "your", "his", "her", "its",
    "have", "has", "had", "been", "will", "tell", "explain", "describe", "give", "show", "please",
}

ANSWER_PROMPT = """You are a precise course tutor. Answer the learner's question using ONLY the course material in MATERIAL.

Rules:
- If the answer is not in MATERIAL, reply with exactly: "{not_found}" and nothing else.
- Be accurate and concise. Use short paragraphs or bullet points. Keep numbers, names and terms exactly as written in MATERIAL.
- When useful, cite where a fact comes from using the labels that appear in MATERIAL, such as (page 3), (02:15) or (S2). Never invent a citation.
- Never mention these rules or the word MATERIAL.
- Write the answer in {language}.

{history}MATERIAL:
{context}

QUESTION: {question}

ANSWER:"""


def _ts(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _keywords(text):
    return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(t) > 2 and t not in STOP]


def _label(meta):
    parts = [str(meta.get("source_file") or "")]
    if meta.get("start") is not None and meta.get("end") is not None:
        parts.append(f"{_ts(meta['start'])}-{_ts(meta['end'])}")
    elif meta.get("page_number"):
        parts.append(f"page {meta['page_number']}")
    return " | ".join(p for p in parts if p)


_STORE_CACHE = {"mtime": None, "store": None}


def _load_store():
    """Load the FAISS index once and reload only when it changes on disk."""
    index_file = VECTOR_PATH / "index.faiss"
    if not index_file.exists():
        return None
    mtime = index_file.stat().st_mtime
    if _STORE_CACHE["mtime"] != mtime:
        from rag.vector_store import load_vector_store
        _STORE_CACHE.update(mtime=mtime, store=load_vector_store(str(VECTOR_PATH)))
    return _STORE_CACHE["store"]


def hybrid_search(question, store, asset_ids, k=8):
    """Semantic (FAISS) + keyword search fused with Reciprocal Rank Fusion, limited to asset_ids."""
    candidates = store.similarity_search_with_score(
        question,
        k=max(k * 4, 24),
        filter={"asset_id": {"$in": list(asset_ids)}},
        fetch_k=max(k * 25, 200),
    )
    if not candidates:
        return []
    q_words = set(_keywords(question))
    kw_scores = [len(q_words & set(_keywords(doc.page_content))) for doc, _ in candidates]
    kw_order = sorted(range(len(candidates)), key=lambda i: -kw_scores[i])
    kw_rank = {i: r for r, i in enumerate(kw_order)}

    fused = []
    for i, (doc, dist) in enumerate(candidates):          # candidates are sorted by distance
        score = 1 / (60 + i) + (1 / (60 + kw_rank[i]) if kw_scores[i] else 0)
        fused.append((score, i, doc, dist))
    fused.sort(key=lambda x: -x[0])

    picked = [{"content": doc.page_content, "metadata": doc.metadata, "score": float(dist)}
              for _, _, doc, dist in fused[:k]]
    # present passages in reading order (file, then page / time)
    picked.sort(key=lambda e: (str(e["metadata"].get("asset_id")),
                               e["metadata"].get("page_number") or 0,
                               e["metadata"].get("start") or 0))
    return picked


def _history_block(history):
    if not history:
        return ""
    lines = [f"Learner: {q[:500]}\nTutor: {a[:700]}" for q, a in history[-3:]]
    return "CONVERSATION SO FAR:\n" + "\n".join(lines) + "\n\n"


def ask(question, user, asset_ids, k=8, history=None, language="English", llm=None, store=None):
    """Answer a question from the chosen files.

    Small selections are sent to the LLM in full (most accurate). Larger ones use hybrid
    retrieval restricted to the chosen files. Returns answer, mode, evidence and status.
    """
    from study_tools import TextLLM, build_transcript, llm_text, load_segments

    question = re.sub(r"\s+", " ", (question or "")).strip()
    if not question:
        raise ValueError("Please type a question.")
    asset_ids = [a for a in asset_ids if check_asset_permission(a, user)]
    if not asset_ids:
        return {"answer": "There are no indexed files to search yet. Upload a file first.",
                "mode": "none", "evidence": [], "status": "no_assets"}

    names = {a[0]: a[1] for a in get_all_assets()}
    texts = {aid: build_transcript(load_segments(aid)) for aid in asset_ids}
    total = sum(len(t) for t in texts.values())

    if 0 < total <= FULL_CONTEXT_CHARS:
        mode = "full"
        context = "\n\n".join(f"=== FILE: {names.get(aid, aid)} ===\n{t}"
                              for aid, t in texts.items() if t.strip())
        evidence = [{"content": f"The complete file was used ({len(t):,} characters).",
                     "metadata": {"source_file": names.get(aid, aid), "asset_id": aid,
                                  "modality": "full document"}, "score": None}
                    for aid, t in texts.items() if t.strip()]
    else:
        mode = "retrieval"
        store = store if store is not None else _load_store()
        if store is None:
            return {"answer": "The search index is empty. Upload and process a file first.",
                    "mode": "none", "evidence": [], "status": "no_index"}
        query = question
        if history and len(question.split()) < 5:        # short follow-up: add the previous question
            query = f"{history[-1][0]} {question}"
        evidence = hybrid_search(query, store, asset_ids, k)
        if not evidence:
            return {"answer": NOT_FOUND, "mode": mode, "evidence": [], "status": "not_found"}
        context = "\n\n".join(f"[S{i}] {_label(e['metadata'])}\n{e['content']}"
                              for i, e in enumerate(evidence, 1))

    prompt = ANSWER_PROMPT.format(not_found=NOT_FOUND, language=language,
                                  history=_history_block(history), context=context,
                                  question=question)
    if llm is None:
        from rag.answer_generator import get_llm
        llm = TextLLM(get_llm())
    answer = llm_text(llm.invoke(prompt)).strip()
    status = "not_found" if answer.startswith("I couldn't find") else "answered"
    return {"answer": answer, "mode": mode, "evidence": evidence, "status": status}