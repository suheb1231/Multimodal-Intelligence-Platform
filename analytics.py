"""Persistence and demo data for the learning dashboard.

Everything is stored as small JSON files in the project's data/ folder:
  quiz_attempts.json  - every submitted quiz (score, wrong questions, course, topic)
  activity_log.json   - learning events (uploads, notes, questions asked, ...)
  enrollments.json    - class roster and which students are enrolled in which file
  students_info.json  - extra student details imported from a results file (email, city, batch, ...)
"""
import json
import random
from datetime import datetime, timedelta

from config import DATA_DIR

ATTEMPTS_FILE = DATA_DIR / "quiz_attempts.json"
EVENTS_FILE = DATA_DIR / "activity_log.json"
ENROLL_FILE = DATA_DIR / "enrollments.json"
INFO_FILE = DATA_DIR / "students_info.json"
DEMO_PREFIX = "Demo_"
INSTRUCTOR = "Instructor"      # identity used in the class-overview (all students) mode


# ----------------------------------------------------------------- storage
def _load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def display_name(user):
    """'Demo_Aarav' -> 'Aarav'."""
    return user[len(DEMO_PREFIX):] if user.startswith(DEMO_PREFIX) else user


# ------------------------------------------------------------ quiz attempts
def record_attempt(user, asset, correct, total, wrong_questions, course=None, topic=None):
    attempts = _load(ATTEMPTS_FILE, [])
    attempts.append({
        "user": user,
        "asset": asset,
        "course": course or "General",
        "topic": topic or asset,
        "correct": correct,
        "total": total,
        "score": round(100 * correct / total) if total else 0,
        "wrong": wrong_questions,
        "time": datetime.now().isoformat(timespec="seconds"),
    })
    _save(ATTEMPTS_FILE, attempts)


def load_attempts(user=None):
    """user=None returns the attempts of every student."""
    attempts = _load(ATTEMPTS_FILE, [])
    return [a for a in attempts if user is None or a["user"] == user]


def wrong_counts(attempts):
    counts = {}
    for a in attempts:
        for q in a["wrong"]:
            counts[q] = counts.get(q, 0) + 1
    return counts


# ------------------------------------------------------------ activity log
def log_event(user, kind, detail=""):
    """kind: upload | notes | flashcards | quiz_generated | quiz_submitted | question"""
    events = _load(EVENTS_FILE, [])
    events.append({"user": user, "kind": kind, "detail": detail,
                   "time": datetime.now().isoformat(timespec="seconds")})
    _save(EVENTS_FILE, events)


def load_events(user=None):
    events = _load(EVENTS_FILE, [])
    return [e for e in events if user is None or e["user"] == user]


# ------------------------------------------------- class roster + enrollment
def _read_enroll():
    data = _load(ENROLL_FILE, {})
    data.setdefault("roster", [])
    data.setdefault("files", {})
    return data


def parse_names(text):
    """Split names on commas / new lines (a CSV first column works too)."""
    skip = {"name", "student", "student name", "students"}
    names = []
    for line in str(text).replace(";", "\n").splitlines():
        for part in line.split(","):
            part = part.strip().strip('"')
            if part and part.lower() not in skip:
                names.append(part)
    return names


def generate_roster(n, prefix="Student_"):
    return [f"{prefix}{i:02d}" for i in range(1, int(n) + 1)]


def get_roster():
    return _read_enroll()["roster"]


def set_roster(names):
    clean = list(dict.fromkeys(n.strip() for n in names if n.strip()))
    data = _read_enroll()
    data["roster"] = clean
    _save(ENROLL_FILE, data)
    return clean


def enroll(asset_name, students=None):
    """Enroll the class roster (or the given students) in a file. Returns the enrolled count."""
    students = list(students) if students is not None else get_roster()
    if not students:
        return 0
    data = _read_enroll()
    data["files"][asset_name] = list(dict.fromkeys(data["files"].get(asset_name, []) + students))
    _save(ENROLL_FILE, data)
    return len(data["files"][asset_name])


def unenroll(asset_name):
    data = _read_enroll()
    data["files"].pop(asset_name, None)
    _save(ENROLL_FILE, data)


def enrollment_map():
    return _read_enroll()["files"]


def known_students():
    """Every student the app knows about: roster, quiz takers, activity and enrollments."""
    names = set(get_roster())
    names |= {a["user"] for a in _load(ATTEMPTS_FILE, [])}
    names |= {e["user"] for e in _load(EVENTS_FILE, [])}
    for enrolled in _read_enroll()["files"].values():
        names |= set(enrolled)
    names = {n for n in names if n.strip() and n != INSTRUCTOR and not _is_number(n)}
    return sorted(names, key=lambda n: display_name(n).lower())


# --------------------------------------------------------------- demo data
DEMO_COURSES = {
    "Machine Learning": ["Regression", "Classification", "Neural Networks", "Overfitting"],
    "Python Programming": ["Functions", "Loops", "OOP", "File Handling"],
    "SQL & Databases": ["Joins", "Aggregation", "Subqueries", "Indexes"],
    "Generative AI": ["Prompting", "RAG", "Embeddings", "Fine-tuning"],
}
TOPIC_DIFFICULTY = {   # higher = harder
    "Regression": 4, "Classification": 8, "Neural Networks": 18, "Overfitting": 14,
    "Functions": 2, "Loops": 0, "OOP": 12, "File Handling": 8,
    "Joins": 15, "Aggregation": 6, "Subqueries": 17, "Indexes": 10,
    "Prompting": 3, "RAG": 13, "Embeddings": 16, "Fine-tuning": 20,
}
DEMO_STUDENTS = [
    "Aarav", "Diya", "Rohan", "Ananya", "Kabir", "Meera", "Vihaan", "Isha", "Arjun", "Saanvi",
    "Reyansh", "Kiara", "Aditya", "Riya", "Krish", "Myra", "Yash", "Tara", "Dev", "Naina",
]


def seed_demo():
    """20 fictional students, 4 courses, 16 topics (~350 quiz attempts + activity events).
    Names start with 'Demo_' so real data is never touched. Deterministic output."""
    clear_demo()
    rng = random.Random(42)
    now = datetime.now()
    attempts = _load(ATTEMPTS_FILE, [])
    events = _load(EVENTS_FILE, [])
    course_students = {}

    for name in DEMO_STUDENTS:
        user = DEMO_PREFIX + name
        skill = rng.randint(45, 90)
        growth = rng.choice([0, 2, 4, 6])
        engagement = rng.randint(3, 14)
        n = 0
        for course in rng.sample(list(DEMO_COURSES), k=rng.choice([2, 3, 4])):
            course_students.setdefault(course, set()).add(user)
            for topic in rng.sample(DEMO_COURSES[course], k=rng.choice([2, 3, 4])):
                for _ in range(rng.choice([1, 2, 2, 3])):
                    n += 1
                    raw = skill + growth * n - TOPIC_DIFFICULTY[topic] + rng.randint(-8, 8)
                    score = max(10, min(100, int(round(raw / 10.0)) * 10))
                    correct = score // 10
                    wrong_n = min(10 - correct, 3)
                    when = now - timedelta(days=rng.randint(0, 30), hours=rng.randint(0, 23))
                    stamp = when.isoformat(timespec="seconds")
                    attempts.append({
                        "user": user, "asset": f"{course} - {topic}", "course": course,
                        "topic": topic, "correct": correct, "total": 10, "score": score,
                        "wrong": [f"{topic}: Question {j}" for j in rng.sample(range(1, 6), k=wrong_n)],
                        "time": stamp,
                    })
                    events.append({"user": user, "kind": "quiz_submitted",
                                   "detail": f"{course} - {topic}", "time": stamp})
        for _ in range(engagement):
            kind = rng.choices(["question", "notes", "flashcards"], weights=[6, 3, 1])[0]
            when = now - timedelta(days=rng.randint(0, 30), hours=rng.randint(0, 23))
            events.append({"user": user, "kind": kind, "detail": "demo",
                           "time": when.isoformat(timespec="seconds")})

    _save(ATTEMPTS_FILE, attempts)
    _save(EVENTS_FILE, events)

    data = _read_enroll()
    for course, students in course_students.items():
        for topic in DEMO_COURSES[course]:
            fname = f"{course} - {topic}"
            keep = [n for n in data["files"].get(fname, []) if not n.startswith(DEMO_PREFIX)]
            data["files"][fname] = keep + sorted(students)
    _save(ENROLL_FILE, data)


def clear_demo():
    _save(ATTEMPTS_FILE, [a for a in _load(ATTEMPTS_FILE, []) if not a["user"].startswith(DEMO_PREFIX)])
    _save(EVENTS_FILE, [e for e in _load(EVENTS_FILE, []) if not e["user"].startswith(DEMO_PREFIX)])
    data = _read_enroll()
    files = {}
    for fname, names in data["files"].items():
        keep = [n for n in names if not n.startswith(DEMO_PREFIX)]
        if keep:
            files[fname] = keep
    data["files"] = files
    _save(ENROLL_FILE, data)


# ------------------------------------------------ import student results (CSV / Excel)
_KEYS = {
    "student": ["student name", "student", "name", "learner", "candidate", "participant", "user"],
    "score": ["score", "marks", "mark", "percentage", "percent", "grade", "result", "points"],
    "course": ["course", "subject", "program", "programme", "stream", "track", "class"],
    "topic": ["topic", "module", "unit", "chapter", "test", "quiz", "exam", "assessment", "lecture"],
    "date": ["date", "time", "submitted", "timestamp"],
}
_NOT_SCORES = ("id", "roll", "phone", "mobile", "age", "year", "batch", "semester", "sem", "rank")


def read_table(uploaded):
    """Read an uploaded CSV / Excel file into a DataFrame (tidy headers, no empty rows)."""
    import io
    import pandas as pd
    name = uploaded.name.lower()
    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded)
    else:
        raw, df = uploaded.getvalue(), None
        for enc in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                df = pd.read_csv(io.BytesIO(raw), sep=None, engine="python", encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        if df is None:
            raise ValueError("The file could not be decoded.")
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df.reset_index(drop=True)


def _to_number(series):
    import pandas as pd
    return pd.to_numeric(series.astype(str).str.replace("%", "", regex=False).str.strip(), errors="coerce")


def looks_numeric(series):
    """True when (almost) every value is a number, i.e. it is a score column, not a names column."""
    return bool(len(series)) and _to_number(series).notna().mean() >= 0.8


def _is_number(text):
    try:
        float(str(text).replace("%", "").strip())
        return True
    except ValueError:
        return False


def _find(cols, words, exclude=()):
    low = {c: str(c).strip().lower() for c in cols if c not in exclude}
    for w in words:
        for c, l in low.items():
            if l == w:
                return c
    for w in words:
        for c, l in low.items():
            if w in l:
                return c
    return None


def guess_columns(df):
    """Best guess of which column is the student, score, course, topic and date."""
    cols = list(df.columns)
    numeric = [c for c in cols if _to_number(df[c]).notna().mean() >= 0.8]
    text_cols = [c for c in cols if c not in numeric]
    student = _find(text_cols, _KEYS["student"])      # only text columns can hold names
    if student is None:
        student = text_cols[0] if text_cols else None
        if student is not None and _find([student], _KEYS["course"] + _KEYS["topic"]):
            student = None          # it is a course / topic column, so the file has no names
    used = {student}
    score = _find([c for c in numeric], _KEYS["score"], used)
    used.add(score)
    course = _find(cols, _KEYS["course"], used)
    used.add(course)
    topic = _find(cols, _KEYS["topic"], used)
    used.add(topic)
    date = _find(cols, _KEYS["date"], used)
    used.add(date)

    score_cols = []
    wide = False
    if score is None:
        score_cols = [c for c in numeric if c not in used
                      and not any(k == str(c).lower() or str(c).lower().endswith(k) for k in _NOT_SCORES)]
        wide = bool(score_cols)
    value_cols = score_cols if wide else ([score] if score else [])
    peak = max([_to_number(df[c]).max() for c in value_cols], default=100)
    out_of = 10 if peak <= 10 else 100
    info = [c for c in cols if c not in used and c not in score_cols]
    return {"student": student, "score": score, "course": course, "topic": topic, "date": date,
            "wide": wide, "score_cols": score_cols, "out_of": out_of, "info_cols": info}


def _canonical(values):
    """Merge spelling variants ('data science' / 'Data Science') into one clean label."""
    from collections import Counter
    groups = {}
    for v in values:
        clean = " ".join(str(v).split())
        groups.setdefault(clean.lower(), Counter())[clean] += 1
    best = {}
    for key, counter in groups.items():
        forms = [f for f, _ in counter.most_common()]
        pick = next((f for f in forms if f != f.lower()), None)
        if pick is None:
            pick = forms[0].upper() if len(forms[0]) <= 3 else forms[0].title()
        best[key] = pick
    return lambda v: best[" ".join(str(v).split()).lower()]


def _drop_imported_enrollments(data):
    for asset, names in data.get("imported", {}).items():
        left = [n for n in data["files"].get(asset, []) if n not in names]
        if left:
            data["files"][asset] = left
        else:
            data["files"].pop(asset, None)
    data["imported"] = {}


def import_results(df, student_col=None, score_col=None, course_col=None, topic_col=None,
                   date_col=None, score_cols=None, out_of=100, info_cols=None, replace=True):
    """Turn a results table into quiz attempts so students, courses and scores show up everywhere.

    student_col=None numbers the rows Student_01, Student_02, ...
    Pass score_cols (wide format: one column per subject/test) OR score_col (one score per row).
    """
    import pandas as pd
    d = df.copy().reset_index(drop=True)
    if student_col and looks_numeric(d[student_col]):
        raise ValueError(f"The column '{student_col}' contains numbers, not student names. "
                         "Pick the column with the names, or choose the auto-generate option.")
    d["__student"] = d[student_col] if student_col else [f"Student_{i + 1:02d}" for i in range(len(d))]
    info_cols = [c for c in (info_cols or []) if c in d.columns]
    keep = ["__student"] + [c for c in (course_col, date_col) if c] + info_cols
    keep = list(dict.fromkeys(keep))

    if score_cols:
        d = d.melt(id_vars=keep, value_vars=list(score_cols), var_name="__topic", value_name="__score")
        topic_col, score_col = "__topic", "__score"
    elif not score_col:
        raise ValueError("Choose the score column (or the subject columns).")

    d["__pct"] = _to_number(d[score_col]) / float(out_of or 100) * 100
    d = d[d["__student"].astype(str).str.strip().ne("") & d["__pct"].notna()].copy()
    d["__pct"] = d["__pct"].clip(0, 100).round(1)
    if d.empty:
        raise ValueError("No valid rows were found (check the student and score columns).")

    stu = _canonical(d["__student"])
    d["__student"] = d["__student"].map(stu)
    if course_col:
        cour = _canonical(d[course_col].fillna("General"))
        d["__course"] = d[course_col].fillna("General").map(cour)
    else:
        d["__course"] = "General"
    if topic_col:
        top = _canonical(d[topic_col].fillna("General"))
        d["__topic"] = d[topic_col].fillna("General").map(top)
    else:
        d["__topic"] = d["__course"]

    now = datetime.now()
    if date_col:
        when = pd.to_datetime(d[date_col], errors="coerce")
    else:
        when = pd.Series([pd.NaT] * len(d), index=d.index)
    fallback = [now - timedelta(minutes=len(d) - i) for i in range(len(d))]
    d["__time"] = [(w if pd.notna(w) else f).isoformat(timespec="seconds") for w, f in zip(when, fallback)]

    attempts = _load(ATTEMPTS_FILE, [])
    data = _read_enroll()
    if replace:
        attempts = [a for a in attempts if a.get("source") != "import"]
        _drop_imported_enrollments(data)
    enroll_by_file = {}
    for _, r in d.iterrows():
        course, topic = r["__course"], r["__topic"]
        asset = course if topic == course else f"{course} - {topic}"
        attempts.append({
            "user": r["__student"], "asset": asset, "course": course, "topic": topic,
            "correct": float(r["__pct"]), "total": 100, "score": float(r["__pct"]),
            "wrong": [], "time": r["__time"], "source": "import",
        })
        enroll_by_file.setdefault(asset, set()).add(r["__student"])
    _save(ATTEMPTS_FILE, attempts)

    data.setdefault("imported", {})
    for asset, students in enroll_by_file.items():
        added = sorted(students)
        data["files"][asset] = list(dict.fromkeys(data["files"].get(asset, []) + added))
        data["imported"][asset] = list(dict.fromkeys(data["imported"].get(asset, []) + added))
    _save(ENROLL_FILE, data)

    if info_cols:
        info = _load(INFO_FILE, {})
        for _, r in d.iterrows():
            card = info.setdefault(r["__student"], {})
            for c in info_cols:
                val = r.get(c)
                if pd.notna(val) and str(val).strip() and c not in card:
                    card[str(c)] = str(val).strip()
        _save(INFO_FILE, info)

    return {"rows": len(d), "students": int(d["__student"].nunique()),
            "courses": sorted(d["__course"].unique()), "topics": int(d["__topic"].nunique())}


def clear_imported():
    attempts = _load(ATTEMPTS_FILE, [])
    imported = {a["user"] for a in attempts if a.get("source") == "import"}
    _save(ATTEMPTS_FILE, [a for a in attempts if a.get("source") != "import"])
    info = _load(INFO_FILE, {})
    _save(INFO_FILE, {k: v for k, v in info.items() if k not in imported})
    data = _read_enroll()
    _drop_imported_enrollments(data)
    _save(ENROLL_FILE, data)


def get_student_info(user):
    return _load(INFO_FILE, {}).get(user, {})


SAMPLE_CSV = """Student,Course,Topic,Score,Date,Email,City
Aarav,Data Science,Python,78,2026-11-02,aarav@example.com,Delhi
Aarav,Data Science,Statistics,85,2026-11-09,aarav@example.com,Delhi
Aarav,DA,Excel,72,2026-11-12,aarav@example.com,Delhi
Diya,Data Science,Python,92,2026-11-02,diya@example.com,Mumbai
Diya,Data Science,Statistics,88,2026-11-09,diya@example.com,Mumbai
Diya,DA,Excel,95,2026-11-12,diya@example.com,Mumbai
Rohan,Data Science,Python,66,2026-11-02,rohan@example.com,Pune
Rohan,DA,Excel,74,2026-11-12,rohan@example.com,Pune
"""


def reset_all():
    """Delete every saved student record (attempts, activity, enrollments, roster, details).
    Uploaded course files and their transcripts are NOT touched."""
    for f in (ATTEMPTS_FILE, EVENTS_FILE, ENROLL_FILE, INFO_FILE):
        try:
            f.unlink()
        except FileNotFoundError:
            pass