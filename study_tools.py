"""Study tools: transcript, notes, quiz, flashcards and recommendations.

Everything is generated from the asset's segments.json (saved by pipeline.py) with the
Gemini model from rag.answer_generator.get_llm().
"""
import json
import re
from config import PROCESSED_DIR

MAX_CHARS = 12000  # max characters per LLM call


# ---------- helpers ----------
def llm_text(response):
    """Always turn a Gemini response into a plain string."""
    content = getattr(response, "content", response)
    if isinstance(content, list):
        return "".join(
            p.get("text", "") if isinstance(p, dict) else str(p) for p in content
        )
    return str(content)


class TextLLM:
    """Wrapper whose invoke() always returns a plain string."""

    def __init__(self, llm):
        self.llm = llm

    def invoke(self, prompt):
        return llm_text(self.llm.invoke(prompt))


def _get_llm():
    from rag.answer_generator import get_llm
    return get_llm()


def _fmt_ts(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _split(text, limit=MAX_CHARS):
    parts, cur = [], ""
    for line in text.splitlines():
        if len(cur) + len(line) + 1 > limit and cur:
            parts.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        parts.append(cur)
    return parts


def _sample(text, limit=MAX_CHARS):
    """For long text, take a slice of every part so the whole file is represented."""
    if len(text) <= limit:
        return text
    parts = _split(text)
    per = max(500, limit // len(parts))
    return "\n".join(p[:per] for p in parts)


def _parse_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    match = re.search(r"\[.*\]", text, re.S)
    return json.loads(match.group(0) if match else text)


# ---------- storage ----------
def load_segments(asset_id):
    path = PROCESSED_DIR / asset_id / "segments.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_cached(asset_id, name):
    path = PROCESSED_DIR / asset_id / name
    return path.read_text(encoding="utf-8") if path.exists() else None


def save_cached(asset_id, name, text):
    path = PROCESSED_DIR / asset_id / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ---------- transcript ----------
def build_transcript(segments):
    lines = []
    for s in segments:
        if s.get("start") is not None and s.get("end") is not None:
            lines.append(f"[{_fmt_ts(s['start'])} - {_fmt_ts(s['end'])}] {s['text']}")
        elif s.get("page"):
            lines.append(f"[Page {s['page']}] {s['text']}")
        else:
            lines.append(s["text"])
    return "\n".join(lines)


# ---------- notes ----------
NOTES_PROMPT = """You are a study-notes writer for an online course.
Using ONLY the content below, write clear study notes in {language}.
Use markdown: a title, key concepts as headings, bullet points, definitions,
and a short 'Key Takeaways' section. Keep timestamps/page references when present.
Do not add facts that are not in the content.

CONTENT:
{text}
"""

MERGE_PROMPT = """Merge these partial study notes into ONE well-organized set of notes in {language}.
Remove repetition, keep markdown headings, and end with 'Key Takeaways'.

PARTIAL NOTES:
{text}
"""


def generate_notes(segments, language="English", llm=None):
    text = build_transcript(segments)
    if not text.strip():
        raise ValueError("This file has no readable text.")
    llm = llm or _get_llm()
    partial = [
        llm_text(llm.invoke(NOTES_PROMPT.format(language=language, text=p)))
        for p in _split(text)
    ]
    if len(partial) == 1:
        return partial[0]
    return llm_text(
        llm.invoke(MERGE_PROMPT.format(language=language, text="\n\n".join(partial)))
    )


# ---------- quiz ----------
QUIZ_PROMPT = """Create {n} {difficulty}-difficulty multiple-choice questions in {language} from the content below.
Easy = recall of facts, Medium = understanding, Hard = application and reasoning.
Rules: use ONLY the content; exactly 4 options per question; exactly one correct option;
'answer' must be copied exactly from 'options'; add a one-line 'explanation'.
Return ONLY a JSON array, no other text:
[{{"question": "...", "options": ["...","...","...","..."], "answer": "...", "explanation": "..."}}]

CONTENT:
{text}
"""


def generate_quiz(segments, n=5, language="English", difficulty="Medium", llm=None):
    text = _sample(build_transcript(segments))
    if not text.strip():
        raise ValueError("This file has no readable text.")
    llm = llm or _get_llm()
    raw = _parse_json(llm_text(llm.invoke(QUIZ_PROMPT.format(n=n, difficulty=difficulty.lower(), language=language, text=text))))
    quiz = []
    for item in raw:
        options = item.get("options") or []
        answer = item.get("answer")
        if answer not in options:
            match = [o for o in options if str(o).strip().lower() == str(answer).strip().lower()]
            answer = match[0] if match else None
        if item.get("question") and len(options) >= 2 and answer:
            quiz.append({
                "question": item["question"],
                "options": options,
                "answer": answer,
                "explanation": item.get("explanation", ""),
            })
    if not quiz:
        raise ValueError("Could not build a valid quiz. Please try again.")
    return quiz


# ---------- flashcards ----------
FLASH_PROMPT = """Create {n} study flashcards in {language} from the content below.
Use ONLY the content. Return ONLY a JSON array:
[{{"front": "question or term", "back": "short answer or definition"}}]

CONTENT:
{text}
"""


def generate_flashcards(segments, n=10, language="English", llm=None):
    text = _sample(build_transcript(segments))
    if not text.strip():
        raise ValueError("This file has no readable text.")
    llm = llm or _get_llm()
    cards = _parse_json(llm_text(llm.invoke(FLASH_PROMPT.format(n=n, language=language, text=text))))
    return [c for c in cards if c.get("front") and c.get("back")]


# ---------- recommendations ----------
REC_PROMPT = """A learner shows these learning difficulties: {friction}.
Questions they got wrong: {wrong}.
Write 3 short, actionable study recommendations in {language}.
Return ONLY a JSON array of strings."""


def generate_recommendations(friction, wrong_questions, language="English", llm=None):
    llm = llm or _get_llm()
    prompt = REC_PROMPT.format(
        friction=", ".join(friction) or "none",
        wrong="; ".join(wrong_questions[:10]) or "none",
        language=language,
    )
    return [str(r) for r in _parse_json(llm_text(llm.invoke(prompt)))][:5]