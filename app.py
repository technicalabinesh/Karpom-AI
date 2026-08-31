"""
Karpom AI - Next-Gen Apple VisionOS & Creatie Glass Design
Run:
    streamlit run app.py
"""

import os
import uuid
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from chatbot import stream_answer, is_ai_mode_available as chat_ai_available
from utils import extract_text

from study_tools import (
    transcribe_audio,
    solve_image_question,
    ask_document,
    generate_cornell_notes,
    generate_quiz,
    generate_study_plan,
    translate_and_simplify,
)

# ============================================================
# INITIAL CONFIGURATION & DATABASE CONNECTIVITY
# ============================================================
load_dotenv()

st.set_page_config(
    page_title="Karpom AI | Creatie VisionOS",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase_client = None

def save_chat_message(session_id: str, role: str, content: str):
    if supabase_client:
        try:
            supabase_client.table("chat_history").insert({
                "session_id": session_id,
                "role": role,
                "content": content
            }).execute()
        except Exception:
            pass

def load_chat_history(session_id: str):
    if supabase_client:
        try:
            res = supabase_client.table("chat_history")\
                .select("role, content")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .execute()
            return res.data or []
        except Exception:
            pass
    return []

# ============================================================
# CREATIE VISIONOS GLASS & MEADOW CSS
# ============================================================
CREATIE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,600;0,700;0,800;0,900;1,700;1,800&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --glass-bg: rgba(255, 255, 255, 0.42);
    --glass-card: rgba(255, 255, 255, 0.72);
    --glass-border: rgba(255, 255, 255, 0.65);
    --glass-shadow: 0 20px 50px rgba(0, 0, 0, 0.12), 0 0 1px 1px rgba(255, 255, 255, 0.8) inset;
    --text-dark: #0F172A;
}

/* Landscape Meadow Wallpaper */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-dark) !important;
}

.stApp {
    background: 
        radial-gradient(circle at 50% 25%, rgba(255, 255, 255, 0.7) 0%, rgba(255, 255, 255, 0) 45%),
        url("https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?q=80&w=2070&auto=format&fit=crop") no-repeat center center fixed !important;
    background-size: cover !important;
}

.main .block-container {
    max-width: 1220px;
    padding: 1.5rem 1.5rem 5rem;
}

/* Top Mini Header */
.creatie-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.creatie-brand {
    font-size: 1.15rem;
    font-weight: 900;
    letter-spacing: 0.18em;
    color: #FFFFFF !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    text-transform: uppercase;
}

/* Profile Glass Badge */
.profile-glass {
    background: rgba(255, 255, 255, 0.28);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    padding: 12px 18px;
    box-shadow: var(--glass-shadow);
    color: #FFFFFF !important;
    max-width: 320px;
}

.profile-glass * { color: #FFFFFF !important; }

/* Giant Creatie Hero Title */
.hero-giant-title {
    font-size: 4.2rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1.02;
    color: #FFFFFF !important;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    text-transform: uppercase;
    margin: 20px 0 24px;
    position: relative;
    display: inline-block;
}

/* Floating Sticker Badges */
.sticker {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 10px;
    font-weight: 800;
    font-size: 0.85rem;
    box-shadow: 0 10px 20px rgba(0,0,0,0.18);
    position: relative;
    z-index: 10;
    vertical-align: middle;
    margin: 0 6px;
}

.sticker-pink {
    background: #F472B6;
    color: #FFFFFF !important;
    transform: rotate(3deg);
}

.sticker-blue {
    background: #38BDF8;
    color: #FFFFFF !important;
    transform: rotate(-4deg);
}

.sticker-purple {
    background: #A78BFA;
    color: #FFFFFF !important;
    transform: rotate(-2deg);
}

.sticker-yellow {
    background: #FBBF24;
    color: #0F172A !important;
    transform: rotate(4deg);
}

/* Floating macOS / visionOS App Dock */
.vision-dock {
    background: rgba(255, 255, 255, 0.35);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 26px;
    padding: 10px 18px;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.15), 0 0 1px 1px rgba(255, 255, 255, 0.9) inset;
    margin: 10px 0 26px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}

/* Dock Icon Button */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    color: #0F172A !important;
    border-radius: 16px !important;
    font-weight: 800 !important;
    font-size: 0.86rem !important;
    min-height: 48px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {
    background: #FFFFFF !important;
    transform: translateY(-4px) scale(1.04) !important;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15) !important;
}

/* Active Workbench Window */
.workbench-window {
    background: rgba(255, 255, 255, 0.82) !important;
    backdrop-filter: blur(32px) saturate(180%);
    -webkit-backdrop-filter: blur(32px) saturate(180%);
    border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 28px;
    padding: 32px;
    box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.18), 0 0 1px 1px rgba(255, 255, 255, 1) inset;
    margin-top: 14px;
}

.window-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
}

.dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.dot-red { background: #FF5F56; }
.dot-yellow { background: #FFBD2E; }
.dot-green { background: #27C93F; }

.window-title {
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    color: #0F172A;
    margin: 0;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] { background: transparent !important; }
div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 18px !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08) !important;
}

div[data-testid="stChatInput"] textarea {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}

/* Chat Bubbles */
.chat-user {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 12px 0 12px auto;
    max-width: 80%;
    font-size: 0.95rem;
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.25);
}
.chat-user * { color: #FFFFFF !important; }

.chat-ai {
    background: #FFFFFF !important;
    color: #0F172A !important;
    padding: 20px 24px;
    border-radius: 20px 20px 20px 4px;
    margin: 12px 0;
    max-width: 88%;
    border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.06);
    font-size: 0.96rem;
    line-height: 1.7;
}

/* Primary Action Button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    padding: 12px 26px !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.25) !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(CREATIE_CSS, unsafe_allow_html=True)

# ============================================================
# STATE INITIALIZATION
# ============================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "active_tool" not in st.session_state:
    st.session_state.active_tool = "1"

if "chat_history" not in st.session_state:
    db_history = load_chat_history(st.session_state.session_id)
    st.session_state.chat_history = db_history if db_history else []

def set_tool(num: str):
    st.session_state.active_tool = num
    st.rerun()

# ============================================================
# TOP CREATIE HEADER & FLOATING GLASS PROFILE BADGE
# ============================================================
ai_connected = chat_ai_available()
status_label = "⚡ Cloud AI Engine Active" if ai_connected else "● Offline Fallback Active"

st.markdown(
    f"""
    <div class="creatie-top">
        <div class="creatie-brand">✦ KARPOM AI</div>
        <div class="profile-glass">
            <div style="font-size:0.75rem; font-weight:800; opacity:0.9; margin-bottom:2px;">🟢 {status_label}</div>
            <div style="font-size:0.88rem; font-weight:800;">ACADEMIC VISION WORKBENCH</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# GIANT HERO TITLE WITH FLOATING STICKERS (CREATIE STYLE)
# ============================================================
st.markdown(
    """
    <div style="text-align: center; padding: 10px 0 20px;">
        <div class="hero-giant-title">
            STUDY THAT MAKES <span class="sticker sticker-blue">⚡ Vision AI</span><br>
            MINDS <span class="sticker sticker-pink">🧠 MCQ Quiz</span> LOOK TWICE
            <span class="sticker sticker-yellow">📝 Cornell Notes</span>
        </div>
        <p style="color:#FFFFFF; font-size:1.15rem; font-weight:700; text-shadow:0 2px 10px rgba(0,0,0,0.3); margin:0 auto; max-width:700px;">
            — Not just answers. We make complex learning alive, intuitive, and unforgettable.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# MACOS / VISIONOS 8-FEATURE APP DOCK (CENTERED & INTERACTIVE)
# ============================================================
st.markdown("<div style='text-align:center; font-size:0.82rem; font-weight:800; color:#FFFFFF; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:8px; text-shadow:0 2px 6px rgba(0,0,0,0.3);'>🍎 SELECT TOOL FROM DOCK</div>", unsafe_allow_html=True)

d1, d2, d3, d4 = st.columns(4)
with d1:
    if st.button("🤖 1. AI Chatbot", use_container_width=True, type="primary" if st.session_state.active_tool == "1" else "secondary"):
        set_tool("1")
with d2:
    if st.button("🎤 2. Voice Q&A", use_container_width=True, type="primary" if st.session_state.active_tool == "2" else "secondary"):
        set_tool("2")
with d3:
    if st.button("📷 3. Vision Solver", use_container_width=True, type="primary" if st.session_state.active_tool == "3" else "secondary"):
        set_tool("3")
with d4:
    if st.button("📄 4. PDF / Notes Q&A", use_container_width=True, type="primary" if st.session_state.active_tool == "4" else "secondary"):
        set_tool("4")

d5, d6, d7, d8 = st.columns(4)
with d5:
    if st.button("📝 5. Cornell Notes", use_container_width=True, type="primary" if st.session_state.active_tool == "5" else "secondary"):
        set_tool("5")
with d6:
    if st.button("🧠 6. MCQ Practice Exam", use_container_width=True, type="primary" if st.session_state.active_tool == "6" else "secondary"):
        set_tool("6")
with d7:
    if st.button("📅 7. Study Planner", use_container_width=True, type="primary" if st.session_state.active_tool == "7" else "secondary"):
        set_tool("7")
with d8:
    if st.button("🌐 8. Translator & ELI5", use_container_width=True, type="primary" if st.session_state.active_tool == "8" else "secondary"):
        set_tool("8")

# ============================================================
# ACTIVE FROSTED GLASS WORKBENCH WINDOW
# ============================================================
st.markdown('<div class="workbench-window">', unsafe_allow_html=True)

# ------------------------------------------------------------
# 1. AI CHATBOT
# ------------------------------------------------------------
if st.session_state.active_tool == "1":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">🤖 01. Offline & Cloud AI Copilot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.chat_history:
        st.markdown(
            """
            <div class="chat-ai">
                👋 <b>Hello! I am your AI Copilot.</b><br>
                Ask me anything — solve math derivations, write code, analyze essay logic, or review study concepts.
            </div>
            """,
            unsafe_allow_html=True,
        )

    for turn in st.session_state.chat_history:
        css = "chat-user" if turn["role"] == "user" else "chat-ai"
        sender = "👤 You" if turn["role"] == "user" else "✦ Karpom AI"
        st.markdown(f'<div class="{css}"><div style="font-size:0.75rem; font-weight:700; opacity:0.85; margin-bottom:4px;">{sender}</div><div>{turn["content"]}</div></div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask a question, enter code, or paste formulas...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        save_chat_message(st.session_state.session_id, "user", user_input)

        st.markdown(f'<div class="chat-user"><div style="font-size:0.75rem; font-weight:700; opacity:0.85; margin-bottom:4px;">👤 You</div><div>{user_input}</div></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div style="font-size:0.75rem; color:#4F46E5; font-weight:800; margin:10px 0 4px;">✦ Karpom AI</div>', unsafe_allow_html=True)
            stream_gen = stream_answer(user_input, st.session_state.chat_history[:-1])
            full_ai = st.write_stream(stream_gen)

        st.session_state.chat_history.append({"role": "assistant", "content": full_ai})
        save_chat_message(st.session_state.session_id, "assistant", full_ai)
        st.rerun()

    if st.session_state.chat_history:
        st.write("")
        if st.button("🗑 Clear Session History"):
            st.session_state.chat_history = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

# ------------------------------------------------------------
# 2. VOICE QUESTION ASKING
# ------------------------------------------------------------
elif st.session_state.active_tool == "2":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">🎤 02. Voice Question Asking (Whisper AI)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    audio_val = st.audio_input("Record Audio Question (Click microphone to speak)")
    if audio_val:
        with st.spinner("🎙️ Transcribing voice query with Whisper AI..."):
            transcribed_text = transcribe_audio(audio_val.getvalue())
            st.info(f"📝 **Transcribed Question:** {transcribed_text}")
            
            if st.button("🚀 Answer Voice Question", type="primary"):
                with st.spinner("Formulating step-by-step solution..."):
                    stream_gen = stream_answer(transcribed_text, [])
                    full_res = ""
                    for token in stream_gen:
                        full_res += token
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;">{full_res}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 3. IMAGE QUESTION SOLVING
# ------------------------------------------------------------
elif st.session_state.active_tool == "3":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">📷 03. Vision Homework & Diagram Solver</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t1, t2 = st.tabs(["📁 Upload Image File", "📸 Live Webcam Capture"])
    img_data = None

    with t1:
        u_file = st.file_uploader("Upload Question Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if u_file:
            img_data = u_file.getvalue()
            st.image(u_file, width=420)
    with t2:
        c_file = st.camera_input("Snap photo of question")
        if c_file:
            img_data = c_file.getvalue()

    custom_instr = st.text_input("Additional instructions (Optional):", placeholder="e.g. Solve step-by-step and show the final numerical result")

    if st.button("✨ Solve with Vision AI", type="primary"):
        if not img_data:
            st.warning("Please upload an image or capture a photo first.")
        else:
            with st.spinner("🔮 Neural Vision analyzing image & computing solution..."):
                sol = solve_image_question(img_data, custom_instr)
                st.markdown(f'<div class="chat-ai" style="max-width:100%;"><h4 style="color:#F43F5E; margin:0 0 10px;">📝 Step-by-Step Solution</h4><div style="line-height:1.7;">{sol}</div></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 4. PDF / NOTES Q&A
# ------------------------------------------------------------
elif st.session_state.active_tool == "4":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">📄 04. Document Q&A & Research RAG</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    doc_f = st.file_uploader("Upload PDF or Word Document", type=["pdf", "docx", "txt", "md"])
    if doc_f:
        doc_raw = extract_text(doc_f)
        st.success(f"✓ Document Loaded: **{doc_f.name}** (~{len(doc_raw.split()):,} words)")

        q_input = st.text_input("Ask a specific question grounded strictly in this document:")
        if st.button("🔍 Search Document & Answer", type="primary"):
            if q_input.strip():
                with st.spinner("Analyzing document context..."):
                    ans = ask_document(doc_raw, q_input)
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;"><h4 style="color:#10B981; margin:0 0 10px;">💡 Document Answer</h4><p style="line-height:1.7; font-size:0.98rem; margin:0;">{ans}</p></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 5. AI CORNELL NOTES GENERATOR
# ------------------------------------------------------------
elif st.session_state.active_tool == "5":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">📝 05. AI Cornell Notes Generator</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    source_mode = st.radio("Input Method:", ["Paste Text / Transcript", "Upload Document File"], horizontal=True)
    raw_study_text = ""

    if source_mode == "Paste Text / Transcript":
        raw_study_text = st.text_area("Paste lecture text or transcript here:", height=200)
    else:
        n_file = st.file_uploader("Upload lecture file", type=["pdf", "docx", "txt"])
        if n_file:
            raw_study_text = extract_text(n_file)

    if st.button("✨ Generate Cornell Notes", type="primary"):
        if not raw_study_text.strip():
            st.warning("Please provide study text first.")
        else:
            with st.spinner("Structuring Cornell notes & recall flashcard cues..."):
                c_notes = generate_cornell_notes(raw_study_text)
                st.markdown(f'<div class="chat-ai" style="max-width:100%;">{c_notes}</div>', unsafe_allow_html=True)
                st.download_button("⬇ Download Cornell Notes (.txt)", data=c_notes, file_name="cornell_notes.txt", mime="text/plain")

# ------------------------------------------------------------
# 6. MCQ & QUIZ GENERATOR
# ------------------------------------------------------------
elif st.session_state.active_tool == "6":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">🧠 06. MCQ & Practice Exam Generator</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        q_topic = st.text_input("Quiz Topic or Subject:", placeholder="e.g. Graph Algorithms & Binary Trees")
    with c2:
        num_q = st.number_input("Number of MCQs:", min_value=3, max_value=20, value=5)
    with c3:
        diff_level = st.selectbox("Difficulty Level:", ["Easy", "Medium", "Hard", "Competitive Finals Level"])

    if st.button("🚀 Generate Practice Test", type="primary"):
        if not q_topic.strip():
            st.warning("Please enter a topic or syllabus subject.")
        else:
            with st.spinner("Generating multiple-choice questions & answer key..."):
                quiz_output = generate_quiz(q_topic, num_q, diff_level)
                st.markdown(f'<div class="chat-ai" style="max-width:100%;">{quiz_output}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 7. PERSONALIZED STUDY PLANNER
# ------------------------------------------------------------
elif st.session_state.active_tool == "7":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">📅 07. Personalized Study Planner</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    p_c1, p_c2 = st.columns(2)
    with p_c1:
        subj_list = st.text_area("Subjects / Syllabus Topics:", placeholder="e.g. Database Systems, Operating Systems, Machine Learning")
        target_g = st.text_input("Target Goal:", placeholder="e.g. Score 90%+ in finals, Pass certification")
    with p_c2:
        days_remain = st.number_input("Days Remaining until Exam:", min_value=1, max_value=90, value=14)
        daily_hrs = st.slider("Available Daily Study Hours:", min_value=1.0, max_value=12.0, value=4.0, step=0.5)

    if st.button("🗓 Build Master Study Roadmap", type="primary"):
        if not subj_list.strip():
            st.warning("Please enter your subjects.")
        else:
            with st.spinner("Designing optimized daily study schedule..."):
                s_plan = generate_study_plan(subj_list, days_remain, daily_hrs, target_g)
                st.markdown(f'<div class="chat-ai" style="max-width:100%;">{s_plan}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 8. MULTILINGUAL TRANSLATION + SIMPLIFICATION
# ------------------------------------------------------------
elif st.session_state.active_tool == "8":
    st.markdown(
        """
        <div class="window-header">
            <span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span>
            <div class="window-title">🌐 08. Multilingual Translation & ELI5 Simplifier</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t_src = st.text_area("Paste complex study content to translate / simplify:", height=180)
    tc1, tc2 = st.columns(2)
    with tc1:
        t_lang = st.selectbox("Target Language:", ["Tamil", "Hindi", "Spanish", "French", "German", "Arabic", "Japanese", "Chinese", "Portuguese", "Russian", "Telugu", "Malayalam"])
    with tc2:
        simp_level = st.selectbox("Complexity Level:", [
            "Explain Like I'm 5 (ELI5 - Super Simple)",
            "High School Student (Intuitive with Analogies)",
            "University Undergraduate (Technical & Detailed)",
            "Professional / Rigorous"
        ])

    if st.button("🌍 Translate & Simplify", type="primary"):
        if not t_src.strip():
            st.warning("Please paste text to translate.")
        else:
            with st.spinner("Translating and adjusting cognitive complexity..."):
                res_trans = translate_and_simplify(t_src, t_lang, simp_level)
                st.markdown(f'<div class="chat-ai" style="max-width:100%;">{res_trans}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
