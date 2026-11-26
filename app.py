import html
import inspect
import json
import os
import shutil
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from config import BASE_DIR

os.chdir(BASE_DIR)          # the vector store uses a relative path
load_dotenv()

import analytics
import pipeline as pl
import study_tools as stt
from agents.asset_profiler import profile_asset
from ingestion.asset_registry import register_asset
from ingestion.file_validator import validate_file
from recommendations.friction_detector import detect_friction
from review.review_manager import review_recommendation

def _accepts(fn, param):
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return True
    return param in params or any(p.kind == p.VAR_KEYWORD for p in params.values())


_outdated = []
if not _accepts(stt.generate_quiz, "difficulty"):
    _outdated.append("study_tools.py")
if not _accepts(pl.ask, "asset_ids"):
    _outdated.append("pipeline.py")
if not all(hasattr(analytics, n) for n in ("known_students", "import_results", "log_event", "reset_all")):
    _outdated.append("analytics.py")

st.set_page_config(page_title="Coursera Multimodal GenAI Studio", page_icon="🎓",
                   layout="wide", initial_sidebar_state="expanded")

if _outdated:
    st.error("Some project files are out of date: **" + ", ".join(_outdated) + "**.\n\n"
             "Replace them with the latest versions. `app.py`, `analytics.py`, `pipeline.py` and "
             "`study_tools.py` must all come from the same download. Then stop the app (Ctrl + C) and "
             "run `streamlit run app.py` again.")
    st.stop()

# ====================================================================== theme
PALETTE = ["#4F46E5", "#0EA5A4", "#F59E0B", "#EC4899", "#10B981", "#8B5CF6", "#EF4444", "#3B82F6"]
GOOD, BAD = "#16A34A", "#EF4444"

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; max-width: 1280px;}
#MainMenu, footer {visibility: hidden;}
.hero {background: linear-gradient(120deg, #4F46E5 0%, #7C3AED 55%, #0EA5A4 100%); color: #fff;
       padding: 28px 34px; border-radius: 18px; margin-bottom: 18px;
       box-shadow: 0 12px 32px rgba(79,70,229,.25);}
.hero-title {font-size: 2.05rem; font-weight: 800; letter-spacing: -.5px; line-height: 1.15;}
.hero-sub {opacity: .93; margin-top: 8px; font-size: 1.04rem;}
.hero-chips {margin-top: 14px;}
.hero-chips span {background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.28);
       padding: 4px 12px; border-radius: 999px; margin-right: 8px; font-size: .82rem; font-weight: 600;}
.kpi {background: #fff; border: 1px solid #E5E7EB; border-left: 5px solid var(--c, #4F46E5);
      border-radius: 14px; padding: 14px 18px; box-shadow: 0 2px 10px rgba(17,24,39,.05);}
.kpi-label {color: #6B7280; font-size: .74rem; text-transform: uppercase; letter-spacing: .07em; font-weight: 700;}
.kpi-value {font-size: 1.85rem; font-weight: 800; color: #111827; line-height: 1.25;}
.kpi-hint {color: #9CA3AF; font-size: .78rem;}
.step {background: #fff; border: 1px solid #E5E7EB; border-radius: 14px; padding: 14px 18px; height: 100%;}
.step-n {display: inline-block; width: 26px; height: 26px; line-height: 26px; text-align: center;
         border-radius: 50%; background: #4F46E5; color: #fff; font-weight: 700; margin-right: 10px;}
.muted {color: #6B7280; font-size: .9rem;}
.chip {display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: .8rem; font-weight: 600; margin: 2px 4px 2px 0;}
.chip.ok {background: #DCFCE7; color: #166534;} .chip.no {background: #FEE2E2; color: #991B1B;}
.stTabs [data-baseweb="tab-list"] {gap: 6px; background: #fff; padding: 6px; border-radius: 12px; border: 1px solid #E5E7EB;}
.stTabs [data-baseweb="tab"] {border-radius: 9px; padding: 8px 16px; font-weight: 600;}
.stTabs [aria-selected="true"] {background: #EEF2FF; color: #4F46E5;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display: none;}
div.stButton > button, div.stDownloadButton > button {border-radius: 10px; font-weight: 600;}
div.stButton > button[kind="primary"] {background: linear-gradient(90deg, #4F46E5, #7C3AED); border: none;}
h4, h5 {letter-spacing: -.2px;}
.profile {display: flex; align-items: center; gap: 16px; background: #fff; border: 1px solid #E5E7EB;
          border-radius: 16px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 2px 10px rgba(17,24,39,.05);}
.avatar {width: 54px; height: 54px; border-radius: 50%; background: linear-gradient(135deg, #4F46E5, #0EA5A4);
         color: #fff; font-weight: 800; font-size: 1.5rem; display: flex; align-items: center; justify-content: center; flex: none;}
.pname {font-size: 1.3rem; font-weight: 800; color: #111827;}
.chip.plain {background: #F3F4F6; color: #374151;} .chip.info {background: #E0E7FF; color: #3730A3;} .chip.warn {background: #FEF3C7; color: #92400E;}
</style>
""", unsafe_allow_html=True)


def kpi(col, label, value, hint="", color="#4F46E5"):
    col.markdown(f'<div class="kpi" style="--c:{color}"><div class="kpi-label">{label}</div>'
                 f'<div class="kpi-value">{value}</div><div class="kpi-hint">{hint}&nbsp;</div></div>',
                 unsafe_allow_html=True)


def show(fig, height=340):
    fig.update_layout(template="plotly_white", height=height, colorway=PALETTE,
                      margin=dict(l=10, r=10, t=55, b=10), font=dict(size=13),
                      legend=dict(orientation="h", y=-0.22))
    st.plotly_chart(fig, use_container_width=True)


def ts(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def shown(name):
    return analytics.display_name(name)


ALL = "👥 All students"


def student_labels(names):
    """{label shown in the sidebar: raw user name}. Demo duplicates get a '(demo)' tag."""
    labels = {}
    for n in names:
        label = analytics.display_name(n)
        if label in labels:
            label = f"{label} (demo)"
        labels[label] = n
    return labels


NONE_OPT = "— none —"
AUTO_NAMES = "— generate Student_01, Student_02, ... —"


def _pick(col, label, options, guess, key):
    """Selectbox preselected with the detected column; returns None for the 'none' options."""
    idx = options.index(guess) if guess in options else 0
    value = col.selectbox(label, options, index=idx, key=key)
    return None if value in (NONE_OPT, AUTO_NAMES) else value


def _reset_all():
    analytics.reset_all()
    st.session_state["sel_student"] = ALL
    st.session_state["confirm_reset"] = False
    st.session_state["import_msg"] = "All student data was deleted."


def _clear_imported():
    analytics.clear_imported()
    st.session_state["import_msg"] = "Imported results removed."


def _add_student():
    name = st.session_state.get("new_student", "").strip()
    if name:
        analytics.set_roster(analytics.get_roster() + [name])
        for label, raw in student_labels(analytics.known_students()).items():
            if raw == name:
                st.session_state["sel_student"] = label
    st.session_state["new_student"] = ""


def _retake(asset_id, qkey, rkey):
    st.session_state.quiz_results.pop(rkey, None)
    for k_ in [k_ for k_ in st.session_state.keys() if str(k_).startswith(f"q_{asset_id}_{qkey}")]:
        del st.session_state[k_]


ASSET_COLS = ["Asset ID", "File", "Type", "Owner", "Visibility", "Status", "Created"]
STATUS_LABEL = {"indexed": "✅ Ready", "processing": "⏳ Processing", "failed": "❌ Failed",
                "uploaded": "⚠️ Not processed", "processed": "⚠️ Not indexed"}

ss = st.session_state
ss.setdefault("recs", [])
ss.setdefault("reviews", {})
ss.setdefault("chat", [])
ss.setdefault("quiz_results", {})

# ===================================================================== sidebar
with st.sidebar:
    st.markdown("### 🎓 Students")
    known = analytics.known_students()
    labels = student_labels(known)
    if known:
        options = [ALL] + list(labels)
        if ss.get("sel_student") not in options:
            ss["sel_student"] = ALL
        picked = st.selectbox("Select a student", options, key="sel_student", label_visibility="collapsed",
                              help="Click and type a name to search.")
        st.caption(f"{len(known)} students · type a name to search")
        all_view = picked == ALL
        user = analytics.INSTRUCTOR if all_view else labels[picked]
    else:
        all_view = False
        user = st.text_input("Your name", value="Student_01",
                             help="Quizzes and questions are saved under this name.").strip() or "Student_01"
        st.caption("No students yet. Import a results file in the Upload tab.")

me = shown(user)

# ======================================================================== hero
st.markdown("""
<div class="hero">
  <div class="hero-title">🎓 Coursera Multimodal GenAI Studio</div>
  <div class="hero-sub">Turn lectures, PDFs and recordings into transcripts, notes, quizzes,
  grounded Q&amp;A and a live learning dashboard.</div>
  <div class="hero-chips"><span>🎬 Video &amp; audio</span><span>📄 PDF &amp; images</span>
  <span>🧠 Notes &amp; quizzes</span><span>💬 Ask AI</span><span>📊 Analytics</span></div>
</div>
""", unsafe_allow_html=True)

with st.popover("⚙️ Settings"):
    lang = st.selectbox("Output language", ["English", "Hindi", "Hinglish"],
                        help="Language of notes, quizzes, flashcards and answers.")
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    has_ocr = bool(shutil.which("tesseract") or Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe").exists())
    st.markdown(
        f'<span class="chip {"ok" if has_key else "no"}">{"✓" if has_key else "✗"} Gemini API</span>'
        f'<span class="chip {"ok" if has_ocr else "no"}">{"✓" if has_ocr else "✗"} OCR</span>',
        unsafe_allow_html=True)
    if not has_key:
        st.caption("Add GEMINI_API_KEY to your .env file.")
    st.divider()
    st.text_input("Add a student", key="new_student", placeholder="Student name")
    st.button("➕ Add student", on_click=_add_student)
    st.divider()
    st.checkbox("I understand: delete ALL student data", key="confirm_reset")
    st.button("🧨 Reset all student data", on_click=_reset_all, disabled=not ss.get("confirm_reset"),
              help="Removes quiz results, activity, rosters and imported details. Course files stay.")

tab_up, tab_lib, tab_study, tab_ask, tab_dash = st.tabs(
    ["📤 Upload", "📚 Library", "🧠 Study Studio", "💬 Ask AI", "📊 Dashboard"])

# ================================================================ 1. upload
with tab_up:
    steps = [("1", "Upload", "Video, audio, PDF, image, text or quiz JSON"),
             ("2", "Process", "Transcribe, OCR, chunk and index automatically"),
             ("3", "Learn", "Transcripts, notes, quizzes, Q&A and analytics")]
    for col, (n, title, desc) in zip(st.columns(3), steps):
        col.markdown(f'<div class="step"><span class="step-n">{n}</span><b>{title}</b>'
                     f'<br><span class="muted">{desc}</span></div>', unsafe_allow_html=True)
    st.write("")

    with st.expander("📥 Import student results (CSV / Excel) — students, courses and scores appear automatically",
                     expanded=not analytics.load_attempts(None)):
        st.caption("Upload a table with your students' scores. Every student appears in the left sidebar with "
                   "their own course, scores and details, and all dashboard charts update.")
        if ss.get("import_msg"):
            st.success(ss.pop("import_msg"))
        results_file = st.file_uploader("Results file (.csv, .xlsx)", type=["csv", "xlsx", "xls"], key="results_file")
        st.download_button("⬇️ Download a sample file", analytics.SAMPLE_CSV, "student_results_sample.csv",
                           mime="text/csv")
        if results_file is not None:
            try:
                table = analytics.read_table(results_file)
            except Exception as e:
                table = None
                st.error(f"Could not read this file: {e}")
            if table is not None:
                st.markdown("**Preview**")
                st.dataframe(table.head(8), hide_index=True, use_container_width=True)
                g = analytics.guess_columns(table)
                cols = list(table.columns)
                tag = f"{results_file.name}_{len(table)}_{len(cols)}"
                st.markdown("**Check the detected columns**")
                m1, m2, m3 = st.columns(3)
                stu_col = _pick(m1, "Student name column", [AUTO_NAMES] + cols, g["student"], f"i_stu_{tag}")
                bad_student = bool(stu_col) and analytics.looks_numeric(table[stu_col])
                if bad_student:
                    m1.warning(f"'{stu_col}' holds numbers, not names. Pick the column with student names.")
                layout = m2.radio("Layout", ["One score per row", "One column per subject / test"],
                                  index=1 if g["wide"] else 0, key=f"i_lay_{tag}")
                out_of = m3.number_input("Scores are out of", 1, 1000, int(g["out_of"]), key=f"i_out_{tag}")
                n1, n2, n3 = st.columns(3)
                course_col = _pick(n1, "Course column", [NONE_OPT] + cols, g["course"], f"i_cou_{tag}")
                score_col, topic_col, score_cols = None, None, None
                if layout == "One score per row":
                    score_col = _pick(n2, "Score column", cols, g["score"], f"i_sco_{tag}")
                    topic_col = _pick(n3, "Topic / test column", [NONE_OPT] + cols, g["topic"], f"i_top_{tag}")
                else:
                    score_cols = n2.multiselect("Subject / test columns", cols, default=g["score_cols"],
                                                key=f"i_cols_{tag}")
                d1, d2 = st.columns(2)
                date_col = _pick(d1, "Date column (optional)", [NONE_OPT] + cols, g["date"], f"i_dat_{tag}")
                used = {stu_col, course_col, score_col, topic_col, date_col, *(score_cols or [])}
                extra_opts = [c for c in cols if c not in used]
                info_cols = d2.multiselect("Extra student details to keep", extra_opts,
                                           default=[c for c in g["info_cols"] if c in extra_opts],
                                           key=f"i_inf_{tag}")
                replace = st.checkbox("Replace my previously imported results", value=True, key=f"i_rep_{tag}")
                if st.button("✅ Import results", type="primary", key=f"i_go_{tag}", disabled=bad_student):
                    try:
                        res = analytics.import_results(table, stu_col, score_col, course_col, topic_col, date_col,
                                                       score_cols, out_of, info_cols, replace)
                        ss["import_msg"] = (f"Imported {res['rows']} results for {res['students']} students "
                                            f"in {', '.join(res['courses'])}. Click a name in the left sidebar.")
                        st.rerun()
                    except Exception as e:
                        st.error(e)
        if analytics.load_attempts(None):
            st.button("🗑️ Remove imported results", on_click=_clear_imported)

    with st.expander("👥 Class roster — automatically enroll students in every new file",
                     expanded=not analytics.get_roster()):
        current = analytics.get_roster()
        st.caption("Add your students once. Every file you upload afterwards enrolls them automatically, "
                   "so they appear in the Dashboard filters and charts even before they take a quiz.")
        names_txt = st.text_area("Student names (comma or one per line)", value="\n".join(current), height=110)
        r1, r2 = st.columns(2)
        n_gen = r1.number_input("Or auto-generate (Student_01, Student_02, ...)", 0, 500, 0)
        names_file = r2.file_uploader("Or upload a names file (.txt / .csv)", type=["txt", "csv"], key="roster_file")
        b1, b2 = st.columns(2)
        if b1.button("💾 Save roster"):
            names = analytics.parse_names(names_txt)
            if names_file is not None:
                names += analytics.parse_names(names_file.getvalue().decode("utf-8", errors="ignore"))
            if n_gen:
                names += analytics.generate_roster(n_gen)
            saved = analytics.set_roster(names)
            st.success(f"Roster saved: {len(saved)} students.")
            st.rerun()
        if b2.button("➕ Enroll roster in existing files"):
            for a_ in pl.visible_assets(user):
                analytics.enroll(a_[1])
            st.success("Roster enrolled in all existing files.")
        if current:
            st.info(f"Current roster: {len(current)} students — " + ", ".join(current[:8])
                    + (" ..." if len(current) > 8 else ""))

    with st.container(border=True):
        files = st.file_uploader("Drop your course files here", type=pl.UPLOAD_TYPES,
                                 accept_multiple_files=True)
        c1, c2, c3, c4 = st.columns(4)
        permission = c1.selectbox("Visibility", ["private", "public"], index=1,
                                  help="Public files are visible to every student. Private files only to their owner.")
        interval = c2.slider("Video frame every (sec)", 2, 30, 5)
        spoken = c3.selectbox("Speech language", ["Auto-detect", "English (en)", "Hindi (hi)"],
                              help="Set this explicitly for the most accurate transcript.")
        model_size = c4.selectbox("Whisper model", ["base", "small", "tiny"],
                                  help="'small' is more accurate but slower.")
        spoken_code = {"Auto-detect": None, "English (en)": "en", "Hindi (hi)": "hi"}[spoken]
        go = st.button("🚀 Upload & process", type="primary", disabled=not files)

    if files and go:
        done = 0
        for f in files:
            with st.status(f"Processing {f.name}", expanded=True) as status:
                try:
                    path = pl.save_upload(f)
                    ok, msg, modality = validate_file(path)
                    if not ok:
                        path.unlink(missing_ok=True)
                        status.update(label=f"❌ {f.name}: {msg}", state="error")
                        continue
                    asset_id = register_asset(path.name, modality, user, permission)
                    res = pl.process_asset(asset_id, path, modality, interval,
                                           spoken_code, model_size, log=st.write)
                    n_enrolled = analytics.enroll(path.name)
                    analytics.log_event(user, "upload", path.name)
                    extra = f", {n_enrolled} students enrolled" if n_enrolled else ""
                    status.update(label=f"✅ {f.name} is ready ({res['chunks']} chunks{extra})",
                                  state="complete")
                    done += 1
                except Exception as e:
                    status.update(label=f"❌ {f.name}: {e}", state="error")
        if done:
            st.success("Processing finished. Open **Study Studio** to generate notes and quizzes, "
                       "or **Ask AI** to chat with your material.")

# ================================================================ 2. library
with tab_lib:
    assets = pl.visible_assets(user)
    if not assets:
        st.info("Your library is empty. Upload a file in the Upload tab.")
    else:
        df = pd.DataFrame(assets, columns=ASSET_COLS)
        k1, k2, k3, k4 = st.columns(4)
        kpi(k1, "Files", len(df), "in your library")
        kpi(k2, "Ready", int((df["Status"] == "indexed").sum()), "searchable & studyable", GOOD)
        kpi(k3, "Needs attention", int((df["Status"] != "indexed").sum()), "failed or not processed", "#F59E0B")
        kpi(k4, "Types", df["Type"].nunique(), ", ".join(sorted(df["Type"].unique())), "#0EA5A4")
        st.write("")
        table = df.drop(columns=["Asset ID"]).copy()
        table["Status"] = table["Status"].map(lambda s: STATUS_LABEL.get(s, s))
        st.dataframe(table, use_container_width=True, hide_index=True)

        labels = {f"{a[1]}  ({a[2]}) · {a[0][:6]}": a for a in assets}
        chosen = labels[st.selectbox("Select a file", list(labels))]
        left, right = st.columns([3, 1])
        with left:
            with st.expander("🔎 File profile"):
                st.json(profile_asset(chosen[0]))
        with right:
            if chosen[3] == user:
                if st.button("🗑️ Delete file", help="Removes the file, transcript and search index entries."):
                    if pl.delete_asset_completely(chosen[0]):
                        analytics.unenroll(chosen[1])
                        st.success("Deleted.")
                        st.rerun()
            else:
                st.caption("Only the owner can delete this file.")

# ============================================================ 3. study studio
with tab_study:
    ready = [a for a in pl.visible_assets(user) if a[5] == "indexed"]
    if not ready:
        st.info("No processed files yet. Upload a file and wait until its status is **Ready**.")
    else:
        labels = {f"{a[1]}  ({a[2]}) · {a[0][:6]}": a for a in ready}
        asset = labels[st.selectbox("Choose a file to study", list(labels), key="study_asset")]
        asset_id, asset_name = asset[0], asset[1]
        segments = stt.load_segments(asset_id)
        words = sum(len(s["text"].split()) for s in segments)
        timed_end = [s["end"] for s in segments if s.get("end") is not None]
        pages = [s["page"] for s in segments if s.get("page")]
        k1, k2, k3 = st.columns(3)
        kpi(k1, "Segments", len(segments), asset[2])
        kpi(k2, "Words", f"{words:,}", "in the transcript", "#0EA5A4")
        if timed_end:
            kpi(k3, "Duration", ts(max(timed_end)), "audio / video length", "#F59E0B")
        else:
            kpi(k3, "Pages", max(pages) if pages else "—", "document length", "#F59E0B")
        st.write("")

        t_tr, t_notes, t_quiz, t_flash = st.tabs(["📜 Transcript", "🗒️ Notes", "🧪 Quiz", "🃏 Flashcards"])

        # ---- transcript
        with t_tr:
            transcript = stt.build_transcript(segments)
            term = st.text_input("Search inside the transcript", placeholder="Type a word or phrase...")
            lines = transcript.splitlines()
            if term:
                lines = [ln for ln in lines if term.lower() in ln.lower()]
                st.caption(f"{len(lines)} matching line(s)")
            st.text_area("Transcript", "\n".join(lines), height=360, label_visibility="collapsed")
            st.download_button("⬇️ Download transcript (.txt)", transcript, f"{asset_name}_transcript.txt")

        # ---- notes
        with t_notes:
            key = f"notes_{lang}.md"
            if st.button("✨ Generate notes", key="gen_notes"):
                with st.spinner("Writing your study notes..."):
                    try:
                        stt.save_cached(asset_id, key, stt.generate_notes(segments, lang))
                        analytics.log_event(user, "notes", asset_name)
                    except Exception as e:
                        st.error(e)
            notes = stt.load_cached(asset_id, key)
            if notes:
                with st.container(border=True):
                    st.markdown(notes)
                st.download_button("⬇️ Download notes (.md)", notes, f"{asset_name}_notes.md")
            else:
                st.caption("Click **Generate notes** to create a structured summary of this file.")

        # ---- quiz
        with t_quiz:
            q1, q2, q3 = st.columns([2, 2, 1])
            n_q = q1.slider("Number of questions", 3, 15, 5)
            level = q2.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
            q3.write("")
            gen_quiz = q3.button("✨ Generate", key="gen_quiz")
            qkey = f"quiz_{lang}_{level}.json"
            rkey = f"{asset_id}|{qkey}"
            if gen_quiz:
                with st.spinner("Creating your quiz..."):
                    try:
                        stt.save_cached(asset_id, qkey, json.dumps(
                            stt.generate_quiz(segments, n=n_q, language=lang, difficulty=level), ensure_ascii=False))
                        ss.quiz_results.pop(rkey, None)
                        analytics.log_event(user, "quiz_generated", asset_name)
                        _retake(asset_id, qkey, rkey)
                    except Exception as e:
                        st.error(e)
            raw = stt.load_cached(asset_id, qkey)
            if not raw:
                st.caption("Choose how many questions and a difficulty, then click **Generate**.")
            else:
                quiz = json.loads(raw)
                picks = {}
                with st.container(border=True):
                    for i, q in enumerate(quiz):
                        picks[i] = st.radio(f"**Q{i + 1}.** {q['question']}", q["options"], index=None,
                                            key=f"q_{asset_id}_{qkey}_{i}")
                b1, b2, _ = st.columns([1, 1, 4])
                if all_view:
                    st.info("Select a student in the left sidebar to record quiz results under their name.")
                if b1.button("✅ Submit quiz", type="primary", key="submit_quiz", disabled=all_view):
                    if any(v is None for v in picks.values()):
                        st.warning("Please answer every question first.")
                    else:
                        correct, wrong, review = 0, [], []
                        for i, q in enumerate(quiz):
                            ok_ = picks[i] == q["answer"]
                            correct += int(ok_)
                            if not ok_:
                                wrong.append(q["question"])
                            review.append({"q": q["question"], "yours": picks[i], "answer": q["answer"],
                                           "ok": ok_, "why": q.get("explanation", "")})
                        analytics.record_attempt(user, asset_name, correct, len(quiz), wrong,
                                                 course="General", topic=asset_name)
                        analytics.log_event(user, "quiz_submitted", asset_name)
                        ss.quiz_results[rkey] = {"correct": correct, "total": len(quiz), "review": review}
                b2.button("🔄 Retake", key="retake_quiz", on_click=_retake, args=(asset_id, qkey, rkey))

                result = ss.quiz_results.get(rkey)
                if result:
                    pct = round(100 * result["correct"] / result["total"])
                    r1, r2, r3 = st.columns(3)
                    kpi(r1, "Score", f"{pct}%", f"{result['correct']} of {result['total']} correct",
                        GOOD if pct >= 60 else BAD)
                    kpi(r2, "Result", "Passed 🎉" if pct >= 60 else "Keep practicing 💪", "pass mark is 60%")
                    kpi(r3, "Saved", "Yes", "see it in the Dashboard", "#0EA5A4")
                    st.progress(pct / 100)
                    for i, item in enumerate(result["review"], 1):
                        icon = "✅" if item["ok"] else "❌"
                        with st.expander(f"{icon} Q{i}. {item['q']}", expanded=not item["ok"]):
                            st.write(f"**Your answer:** {item['yours']}")
                            if not item["ok"]:
                                st.write(f"**Correct answer:** {item['answer']}")
                            if item["why"]:
                                st.caption(item["why"])

        # ---- flashcards
        with t_flash:
            fkey = f"flashcards_{lang}.json"
            if st.button("✨ Generate flashcards", key="gen_cards"):
                with st.spinner("Making flashcards..."):
                    try:
                        cards = stt.generate_flashcards(segments, 10, lang)
                        stt.save_cached(asset_id, fkey, json.dumps(cards, ensure_ascii=False))
                        analytics.log_event(user, "flashcards", asset_name)
                    except Exception as e:
                        st.error(e)
            raw = stt.load_cached(asset_id, fkey)
            if raw:
                cards = json.loads(raw)
                left, right = st.columns(2)
                for i, card in enumerate(cards):
                    with (left if i % 2 == 0 else right).expander(f"🃏 {card['front']}"):
                        st.write(card["back"])
            else:
                st.caption("Click **Generate flashcards** for quick revision cards.")

# ================================================================ 4. ask AI
with tab_ask:
    ready_a = [a for a in pl.visible_assets(user) if a[5] == "indexed"]
    if not ready_a:
        st.info("Nothing to ask about yet. Upload and process a file first.")
    else:
        scope_map = {"📚 All my files": [a[0] for a in ready_a]}
        for a in ready_a:
            scope_map[f"{a[1]}  ·  {a[0][:6]}"] = [a[0]]
        s1, s2 = st.columns([4, 1])
        scope = s1.selectbox("Answer using", list(scope_map),
                             help="Pick one file for the most focused answers.")
        s2.write("")
        if s2.button("🧹 Clear chat"):
            ss.chat = []
            st.rerun()

        question = st.chat_input("Ask anything about the selected material...")
        if question:
            pairs, last_q = [], None
            for m in ss.chat:
                if m["role"] == "user":
                    last_q = m["content"]
                elif last_q is not None:
                    pairs.append((last_q, m["content"]))
                    last_q = None
            ss.chat.append({"role": "user", "content": question})
            try:
                with st.spinner("Reading the material..."):
                    res = pl.ask(question, user, scope_map[scope], k=8, history=pairs, language=lang)
                ss.chat.append({"role": "assistant", "content": res["answer"], "mode": res["mode"],
                                "status": res["status"], "evidence": res["evidence"]})
                analytics.log_event(user, "question", question[:80])
            except Exception as e:
                ss.chat.append({"role": "assistant", "content": f"⚠️ {e}", "mode": "error",
                                "status": "error", "evidence": []})

        if not ss.chat:
            st.markdown("**Try asking:**")
            for ex in ["Summarize the main ideas in simple words.",
                       "What are the key definitions I should remember?",
                       "Explain the first topic step by step."]:
                st.markdown(f"- {ex}")

        for m in ss.chat:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m["role"] == "assistant" and m.get("evidence"):
                    if m["mode"] == "full":
                        names_used = ", ".join(sorted({e["metadata"].get("source_file", "") for e in m["evidence"]}))
                        st.caption(f"📄 Answered from the complete file: {names_used}")
                    else:
                        with st.expander(f"📎 Sources ({len(m['evidence'])} passages)"):
                            for i, e in enumerate(m["evidence"], 1):
                                meta = e["metadata"]
                                where = ""
                                if meta.get("start") is not None:
                                    where = f" · {ts(meta['start'])}-{ts(meta['end'])}"
                                elif meta.get("page_number"):
                                    where = f" · page {meta['page_number']}"
                                st.markdown(f"**S{i} · {meta.get('source_file')}{where}**")
                                st.caption(e["content"])
                elif m["role"] == "assistant" and m.get("status") == "not_found":
                    st.caption("Tip: select the specific file above or rephrase your question.")

# ============================================================== 5. dashboard
def _load_demo():
    analytics.seed_demo()
    ss["sel_student"] = ALL
    ss["demo_msg"] = "✅ 20 demo students loaded — click any name in the left sidebar to see their data."


def _clear_demo():
    analytics.clear_demo()
    ss["sel_student"] = ALL
    ss["demo_msg"] = "🧹 Demo data removed."


with tab_dash:
    st.markdown("#### 📊 Learning Dashboard")
    if all_view:
        st.caption("Class overview. Click a student's name in the left sidebar to open their personal dashboard.")
    else:
        st.caption(f"Showing the dashboard of **{me}**. Choose **👥 All students** in the sidebar for the class overview.")
    if ss.get("demo_msg"):
        st.success(ss.pop("demo_msg"))
    with st.expander("🎭 Demo data — show the dashboard with sample students"):
        st.caption("Creates 20 fictional students across 4 courses and 16 topics (names start with 'Demo_'). "
                   "Your real data is never changed.")
        d1, d2 = st.columns(2)
        d1.button("➕ Load demo data", on_click=_load_demo)
        d2.button("🧹 Remove demo data", on_click=_clear_demo)

    vis = pl.visible_assets(user)
    sub_quiz, sub_content, sub_insights = st.tabs(["🧪 Quizzes & Students", "📚 Course Content", "🧭 Learning Insights"])

    # ------------------------------------------------ quizzes & students
    with sub_quiz:
        enroll_disp = {f: [shown(n) for n in names] for f, names in analytics.enrollment_map().items()}
        cols = ["user", "asset", "course", "topic", "correct", "total", "score", "wrong", "time"]

        def prep(rows):
            df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols)
            for c_ in ("course", "topic"):
                if c_ not in df:
                    df[c_] = None
            df["course"] = df["course"].fillna("General")
            df["topic"] = df["topic"].fillna(df["asset"])
            df["time"] = pd.to_datetime(df["time"])
            df["score"] = pd.to_numeric(df["score"])
            df["student"] = df["user"].map(shown)
            return df

        base_all = prep(analytics.load_attempts(None))
        base = base_all if all_view else base_all[base_all["user"] == user].reset_index(drop=True)

        if not all_view:
            mine = base_all[base_all["user"] == user]
            ranking = base_all.groupby("student")["score"].mean().sort_values(ascending=False)
            if mine.empty:
                chips = '<span class="chip warn">No quiz attempts yet</span>'
            else:
                avg_me = mine["score"].mean()
                rank_txt = f"#{list(ranking.index).index(me) + 1} of {len(ranking)}"
                if avg_me < 60:
                    status_chip = '<span class="chip no">⚠️ At risk</span>'
                elif avg_me >= 80:
                    status_chip = '<span class="chip ok">🌟 Excellent</span>'
                else:
                    status_chip = '<span class="chip info">🙂 On track</span>'
                chips = (f'<span class="chip info">Average {avg_me:.0f}%</span>'
                         f'<span class="chip info">{len(mine)} attempts</span>'
                         f'<span class="chip info">Class rank {rank_txt}</span>{status_chip}')
            course_chips = "".join(f'<span class="chip plain">📘 {html.escape(c)}</span>'
                                   for c in sorted(mine["course"].unique())[:6])
            detail_chips = "".join(
                f'<span class="chip plain">{html.escape(str(k))}: {html.escape(str(v))}</span>'
                for k, v in list(analytics.get_student_info(user).items())[:6])
            st.markdown(f'<div class="profile"><div class="avatar">{html.escape(me[:1].upper())}</div>'
                        f'<div><div class="pname">{html.escape(me)}</div><div>{chips}</div>'
                        f'<div>{course_chips}{detail_chips}</div></div></div>',
                        unsafe_allow_html=True)

        if all_view:
            enrolled_files = list(enroll_disp)
        else:
            enrolled_files = [f for f, names in enroll_disp.items() if me in names]
        files_all = sorted(set(base["asset"]) | set(enrolled_files))

        if not files_all:
            st.info("No student data yet. Import a results file (CSV / Excel) in the Upload tab, take a quiz in "
                    "Study Studio, or load the demo data above.")
        else:
            first = base.drop_duplicates("asset").set_index("asset")
            file_course = first["course"].to_dict()
            file_topic = first["topic"].to_dict()

            def course_of(f):
                return file_course.get(f, "General")

            def topic_of(f):
                return file_topic.get(f, f)

            def students_of(f):
                if not all_view:
                    return {me}
                return set(base.loc[base["asset"] == f, "student"]) | set(enroll_disp.get(f, []))

            f1, f2 = st.columns(2)
            courses_all = sorted({course_of(f) for f in files_all})
            sel_courses = f1.multiselect("Course", courses_all, default=courses_all)
            files_in_course = [f for f in files_all if course_of(f) in sel_courses]
            topic_opts = sorted({topic_of(f) for f in files_in_course})
            sel_topics = f2.multiselect("Topic", topic_opts, default=topic_opts)
            file_opts = [f for f in files_in_course if topic_of(f) in sel_topics]

            f3, f4 = st.columns(2)
            sel_files = f3.multiselect("File / Lecture", file_opts, default=file_opts)
            universe = sorted(set().union(*[students_of(f) for f in sel_files])) if sel_files else []
            if all_view:
                sel_students = f4.multiselect(f"Students ({len(universe)} available)", universe, default=universe)
            else:
                sel_students = [me] if sel_files else []
                f4.caption(f"Showing **{me}**. Switch to *All students* to compare the whole class.")

            qdf = (base[base["asset"].isin(sel_files) & base["student"].isin(sel_students)]
                   .sort_values("time").reset_index(drop=True))
            qdf["Attempt"] = range(1, len(qdf) + 1)

            n_stu, n_att = len(sel_students), qdf["student"].nunique()
            avg_txt = f"{qdf['score'].mean():.0f}%" if not qdf.empty else "—"
            pass_txt = f"{(qdf['score'] >= 60).mean() * 100:.0f}%" if not qdf.empty else "—"
            k1, k2, k3, k4, k5 = st.columns(5)
            kpi(k1, "Students", n_stu, "enrolled")
            kpi(k2, "Took a quiz", n_att, "at least one attempt", GOOD)
            kpi(k3, "Not started", n_stu - n_att, "no quiz yet", BAD)
            kpi(k4, "Average score", avg_txt, f"{len(qdf)} attempts", "#F59E0B")
            kpi(k5, "Pass rate", pass_txt, "score of 60% or more", "#0EA5A4")
            st.write("")

            part = []
            for f in sel_files:
                enrolled = students_of(f) & set(sel_students)
                done = set(qdf.loc[qdf["asset"] == f, "student"])
                part.append({"File": f, "Took a quiz": len(done), "Not started": len(enrolled - done)})
            if part:
                pdf = pd.DataFrame(part).melt(id_vars="File", var_name="Status", value_name="Students")
                show(px.bar(pdf, x="File", y="Students", color="Status", barmode="stack",
                            title="Participation per file",
                            color_discrete_map={"Took a quiz": GOOD, "Not started": BAD}))

            if all_view and sel_students:
                st.markdown("##### 👩‍🎓 Student report")
                rows = []
                for stu in sel_students:
                    sdf = qdf[qdf["student"] == stu]
                    if sdf.empty:
                        rows.append({"Student": stu, "Attempts": 0, "Avg": None, "Best": None,
                                     "Weakest topic": "—", "Status": "⏳ Not started"})
                    else:
                        avg = sdf["score"].mean()
                        if avg < 60:
                            label = "⚠️ At risk"
                        elif avg >= 80:
                            label = "🌟 Excellent"
                        else:
                            label = "🙂 On track"
                        rows.append({"Student": stu, "Attempts": len(sdf), "Avg": round(avg),
                                     "Best": int(sdf["score"].max()),
                                     "Weakest topic": sdf.groupby("topic")["score"].mean().idxmin(),
                                     "Status": label})
                rep = pd.DataFrame(rows)
                rep["Avg"] = rep["Avg"].astype("Int64")
                rep["Best"] = rep["Best"].astype("Int64")
                rep = rep.sort_values("Avg", ascending=False, na_position="last")
                st.dataframe(rep, hide_index=True, use_container_width=True)

                l1, l2, l3 = st.columns(3)
                l1.markdown("**🏆 Top 5**")
                l1.dataframe(rep[rep["Attempts"] > 0][["Student", "Avg"]].head(5),
                             hide_index=True, use_container_width=True)
                l2.markdown("**⚠️ At risk (avg below 60%)**")
                risk = rep[rep["Status"] == "⚠️ At risk"][["Student", "Avg"]]
                if len(risk):
                    l2.dataframe(risk, hide_index=True, use_container_width=True)
                else:
                    l2.success("No one is at risk")
                l3.markdown("**⏳ Not started**")
                nope = rep[rep["Attempts"] == 0][["Student"]]
                if len(nope):
                    l3.dataframe(nope, hide_index=True, use_container_width=True)
                else:
                    l3.success("Everyone has taken a quiz")

                pick_student = st.selectbox("🔍 Student detail", ["— select a student —"] + list(rep["Student"]))
                if pick_student != "— select a student —":
                    sdf = qdf[qdf["student"] == pick_student]
                    if sdf.empty:
                        st.info(f"{pick_student} has not taken a quiz yet.")
                    else:
                        s1, s2, s3 = st.columns(3)
                        kpi(s1, "Attempts", len(sdf))
                        kpi(s2, "Average", f"{sdf['score'].mean():.0f}%", "", "#F59E0B")
                        kpi(s3, "Best", f"{sdf['score'].max():.0f}%", "", GOOD)
                        e1, e2 = st.columns(2)
                        with e1:
                            show(px.line(sdf, x="time", y="score", markers=True, hover_data=["topic"],
                                         title=f"{pick_student} — score trend", range_y=[0, 100]))
                        with e2:
                            by_t = sdf.groupby("topic", as_index=False)["score"].mean().sort_values("score")
                            show(px.bar(by_t, x="score", y="topic", orientation="h",
                                        title=f"{pick_student} — by topic", range_x=[0, 100]))
                        wq = analytics.wrong_counts(sdf.to_dict("records"))
                        if wq:
                            top_wrong = sorted(wq.items(), key=lambda x: -x[1])[:5]
                            st.write("**Most missed questions:** " + "; ".join(f"{q} (x{n})" for q, n in top_wrong))

            if qdf.empty:
                st.info("Nobody in this selection has taken a quiz yet, so score charts are not available.")
            else:
                st.markdown("##### 📈 Performance")
                if all_view:
                    cs = qdf.groupby("course").agg(Students=("student", "nunique"), Attempts=("score", "size"),
                                                   Average=("score", "mean")).reset_index()
                    cs["Pass rate %"] = qdf.groupby("course")["score"].apply(lambda x: (x >= 60).mean() * 100).values
                    st.markdown("**Course summary**")
                    st.dataframe(cs.rename(columns={"course": "Course"}).round(1), hide_index=True,
                                 use_container_width=True)
                else:
                    ct = qdf.groupby("course").agg(Tests=("score", "size"), Average=("score", "mean"),
                                                   Best=("score", "max"), Latest=("score", "last")).reset_index()
                    st.markdown(f"**Courses of {me}**")
                    st.dataframe(ct.rename(columns={"course": "Course"}).round(1), hide_index=True,
                                 use_container_width=True)
                c1, c2 = st.columns(2)
                with c1:
                    by_course = qdf.groupby("course", as_index=False)["score"].mean()
                    show(px.bar(by_course, x="course", y="score", color="course",
                                title="Average score per course", range_y=[0, 100]))
                with c2:
                    by_topic = qdf.groupby("topic", as_index=False)["score"].mean().sort_values("score")
                    show(px.bar(by_topic, x="score", y="topic", orientation="h",
                                title="Average score per topic (weakest first)", range_x=[0, 100]))
                if all_view:
                    by_user = (qdf.groupby("student", as_index=False)["score"].mean()
                               .sort_values("score", ascending=False))
                    show(px.bar(by_user, x="student", y="score", title="Average score per student",
                                range_y=[0, 100]))
                    heat = qdf.pivot_table(index="student", columns="topic", values="score", aggfunc="mean")
                    show(px.imshow(heat, aspect="auto", color_continuous_scale="RdYlGn", zmin=0, zmax=100,
                                   title="Student × topic heatmap (green = strong, red = weak)"), 460)
                    show(px.histogram(qdf, x="score", nbins=10, range_x=[0, 100],
                                      title="Score distribution (all attempts)"))
                else:
                    show(px.line(qdf, x="Attempt", y="score", markers=True, hover_data=["topic"],
                                 title=f"{me} — score trend", range_y=[0, 100]))
                    class_df = base_all[base_all["asset"].isin(sel_files)]
                    stu_t = qdf.groupby("topic")["score"].mean()
                    cls_t = class_df.groupby("topic")["score"].mean().reindex(stu_t.index)
                    cmp = (pd.DataFrame({me: stu_t, "Class average": cls_t}).rename_axis("topic")
                           .reset_index().melt(id_vars="topic", var_name="Who", value_name="Score"))
                    show(px.bar(cmp, x="topic", y="Score", color="Who", barmode="group",
                                title=f"{me} vs class average (by topic)", range_y=[0, 100]))
                    show(px.bar(qdf, x="asset", y="score", color="course", range_y=[0, 100],
                                title=f"{me} — score per test (colored by course)"))
                daily = qdf.assign(Date=qdf["time"].dt.date).groupby("Date", as_index=False)["score"].mean()
                show(px.line(daily, x="Date", y="score", markers=True, title="Average score over time",
                             range_y=[0, 100]))
                missed = analytics.wrong_counts(qdf.to_dict("records"))
                if missed:
                    mdf = pd.DataFrame(sorted(missed.items(), key=lambda x: -x[1])[:8],
                                       columns=["Question", "Times missed"])
                    show(px.bar(mdf, x="Times missed", y="Question", orientation="h",
                                title="Most missed questions"))

    # ------------------------------------------------ course content
    with sub_content:
        if not vis:
            st.info("No files yet.")
        else:
            adf = pd.DataFrame(vis, columns=ASSET_COLS)
            c1, c2 = st.columns(2)
            with c1:
                mod = adf["Type"].value_counts().reset_index()
                mod.columns = ["Type", "Count"]
                show(px.pie(mod, names="Type", values="Count", title="Files by type", hole=0.45))
            with c2:
                stat = adf["Status"].map(lambda s: STATUS_LABEL.get(s, s)).value_counts().reset_index()
                stat.columns = ["Status", "Count"]
                show(px.bar(stat, x="Status", y="Count", title="Processing status", color="Status"))

            rows = []
            for a in vis:
                segs = stt.load_segments(a[0])
                if segs:
                    rows.append({"File": a[1], "Words": sum(len(x["text"].split()) for x in segs)})
            if rows:
                show(px.bar(pd.DataFrame(rows), x="File", y="Words", title="Content size (words)"))

            timed = [a for a in vis if a[2] in ("video", "audio") and a[5] == "indexed"]
            if timed:
                st.markdown("##### 🎙️ Lecture timeline")
                pick = {f"{a[1]} · {a[0][:6]}": a for a in timed}
                sel = pick[st.selectbox("Video / audio file", list(pick), key="dash_timed")]
                tl = [x for x in stt.load_segments(sel[0]) if x.get("start") is not None]
                if tl:
                    tdf = pd.DataFrame({"Minute": [int(x["start"] // 60) for x in tl],
                                        "Words": [len(x["text"].split()) for x in tl]})
                    tdf = tdf.groupby("Minute", as_index=False).sum()
                    show(px.bar(tdf, x="Minute", y="Words", title="Words spoken per minute"))

    # ------------------------------------------------ learning insights
    with sub_insights:
        if all_view:
            st.info("Select a student in the left sidebar to see their learning profile and recommendations.")
        else:
            my_attempts = analytics.load_attempts(user)
            my_wrong = analytics.wrong_counts(my_attempts)
            my_scores = [a["score"] for a in my_attempts]
            my_events = analytics.load_events(user)
            asked = sum(1 for e in my_events if e["kind"] == "question")
            activity = {
                "quiz_score": round(sum(my_scores) / len(my_scores)) if my_scores else 100,
                "repeated_mistakes": sum(1 for v in my_wrong.values() if v >= 2),
                "help_requests": asked,
            }
            st.markdown(f"##### 🧭 Learning profile — {me}")
            i1, i2, i3 = st.columns(3)
            kpi(i1, "Average quiz score", f"{activity['quiz_score']}%" if my_scores else "—", f"{len(my_scores)} attempts", "#F59E0B")
            kpi(i2, "Repeated mistakes", activity["repeated_mistakes"], "questions missed 2+ times", BAD)
            kpi(i3, "Questions asked", asked, "to the AI tutor", "#0EA5A4")
            st.write("")

            friction = detect_friction(activity)
            if friction:
                for item in friction:
                    st.warning(item)
            else:
                st.success("No learning difficulties detected right now.")

            if st.button("🤖 Generate study recommendations"):
                try:
                    with st.spinner("Thinking about your next steps..."):
                        ss.recs = stt.generate_recommendations(friction, list(my_wrong), lang)
                        ss.reviews = {}
                except Exception as e:
                    st.error(e)
            for i, rec in enumerate(ss.recs):
                with st.container(border=True):
                    st.write(f"**{i + 1}.** {rec}")
                    a_, b_, c_ = st.columns([1, 1, 6])
                    if a_.button("Approve", key=f"ap{i}"):
                        ss.reviews[i] = review_recommendation(rec, "approved")["status"]
                    if b_.button("Reject", key=f"rj{i}"):
                        ss.reviews[i] = review_recommendation(rec, "rejected")["status"]
                    c_.caption(f"Review status: {ss.reviews.get(i, 'pending')}")

        events = analytics.load_events(None if all_view else user)
        if events:
            kind_label = {"upload": "Upload", "notes": "Notes", "flashcards": "Flashcards",
                          "quiz_generated": "Quiz created", "quiz_submitted": "Quiz submitted",
                          "question": "Question asked"}
            edf = pd.DataFrame(events)
            edf["Date"] = pd.to_datetime(edf["time"]).dt.date
            edf["Activity"] = edf["kind"].map(lambda k: kind_label.get(k, k))
            grouped = edf.groupby(["Date", "Activity"], as_index=False).size().rename(columns={"size": "Count"})
            show(px.bar(grouped, x="Date", y="Count", color="Activity", barmode="stack",
                        title="Learning activity" + (" — whole class" if all_view else " — you")))
        else:
            st.caption("Learning activity will appear here as you upload, ask questions and take quizzes.")