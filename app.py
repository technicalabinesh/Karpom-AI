"""
Karpom AI - Next-Gen Academic Intelligence Platform
Multi-View Routing: Landing Page -> Dedicated Tool Workspace
Run:
    streamlit run app.py
"""

import os
import uuid
import base64
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
    page_title="Karpom AI | Next-Gen Academic Intelligence",
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

# Dynamic Logo Engine: Checks for logo.png in project folder
def get_logo_html(size: int = 28):
    """Loads custom logo.png from project root or displays default fallback."""
    for fname in ["logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "logo.svg"]:
        if os.path.exists(fname):
            try:
                with open(fname, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/svg+xml" if fname.endswith(".svg") else "image/png"
                return f'<img src="data:{mime};base64,{b64}" width="{size}" height="{size}" style="vertical-align:middle; border-radius:6px; object-fit:contain;" />'
            except Exception:
                pass
    # Fallback emblem if logo.png is not added yet
    return f'<span style="font-size:{size-6}px; vertical-align:middle;">🌸</span>'

# ============================================================
# STATE INITIALIZATION & ROUTING ENGINE
# ============================================================
if "view" not in st.session_state:
    st.session_state.view = "landing"  # 'landing' or 'workspace'

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "active_feature" not in st.session_state:
    st.session_state.active_feature = "1"

if "chat_history" not in st.session_state:
    db_history = load_chat_history(st.session_state.session_id)
    st.session_state.chat_history = db_history if db_history else []

def open_workspace(feature_id: str):
    """Switches view to dedicated workspace for selected feature."""
    st.session_state.active_feature = feature_id
    st.session_state.view = "workspace"
    st.rerun()

def back_to_landing():
    """Switches view back to landing page."""
    st.session_state.view = "landing"
    st.rerun()

# ============================================================
# DRIBBBLE-GRADE MATTE DARK DESIGN SYSTEM
# ============================================================
DRIBBBLE_SAAS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,700;1,800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-dark: #0A0A0C;
    --card-dark: #121216;
    --card-surface: #18181E;
    --border: #23232C;
    --border-hover: #3E3E4E;
    --text-pure: #FFFFFF;
    --text-dim: #9E9EA8;
}

/* Global Reset */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-dark) !important;
    color: var(--text-pure) !important;
}

.stApp {
    background: 
        radial-gradient(ellipse at 50% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 40%, rgba(244, 63, 94, 0.08) 0%, transparent 40%),
        radial-gradient(ellipse at 20% 80%, rgba(14, 165, 233, 0.08) 0%, transparent 40%),
        #0A0A0C !important;
    background-attachment: fixed;
}

.main .block-container {
    max-width: 1240px;
    padding: 1.25rem 1.5rem 5rem;
}

/* Floating Pill Navbar */
.nav-pill-container {
    background: rgba(18, 18, 22, 0.85);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 9999px;
    padding: 10px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    margin-bottom: 30px;
}

.brand-title {
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 10px;
    color: #FFFFFF !important;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    background: rgba(34, 197, 94, 0.12);
    color: #4ADE80 !important;
    border: 1px solid rgba(74, 222, 128, 0.3);
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #4ADE80;
    box-shadow: 0 0 8px #4ADE80;
}

/* Hero Typography */
.hero-wrapper {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px 0 36px;
    margin: 0 auto;
}

.hero-pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #F8FAFC !important;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 18px;
}

.hero-headline {
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.15;
    color: #FFFFFF !important;
    margin: 0 0 14px;
    text-align: center;
}

.hero-italic {
    font-style: italic;
    font-weight: 400;
    color: #A1A1AA !important;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: var(--text-dim) !important;
    max-width: 740px;
    margin: 0 auto;
    line-height: 1.65;
    text-align: center !important;
}

/* Section Header */
.section-tag {
    font-size: 0.8rem;
    font-weight: 700;
    color: #A1A1AA;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* 8-Feature Card Deck */
.feature-card {
    background: var(--card-dark);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 24px;
    min-height: 190px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    margin-bottom: 16px;
}

.feature-card:hover {
    transform: translateY(-4px);
    border-color: var(--border-hover);
    box-shadow: 0 14px 34px -4px rgba(0, 0, 0, 0.6);
}

.card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.card-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
}

.card-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    color: #71717A;
}

.card-title {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 6px;
    color: #FFFFFF !important;
}

.card-desc {
    font-size: 0.84rem;
    color: var(--text-dim) !important;
    line-height: 1.45;
    margin: 0;
}

/* Buttons */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    background: #18181E !important;
    border: 1px solid #272732 !important;
    color: #FFFFFF !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    min-height: 46px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {
    background: #23232C !important;
    border-color: #6366F1 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: #FFFFFF !important;
    color: #0A0A0C !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 18px rgba(255, 255, 255, 0.2) !important;
}

/* Dedicated Workspace View Elements */
.workbench-panel {
    background: #121216 !important;
    border: 1px solid #23232C !important;
    border-radius: 24px;
    padding: 28px;
    margin-top: 16px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
}

.workbench-title {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0 0 6px;
    color: #FFFFFF !important;
}

.workbench-desc {
    font-size: 0.95rem;
    color: var(--text-dim) !important;
    margin: 0 0 24px;
}

/* Chat Input */
div[data-testid="stChatInput"] { background: transparent !important; }
div[data-testid="stChatInput"] > div {
    background: #18181E !important;
    border: 1px solid #272732 !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
}

div[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Chat Bubbles */
.chat-user {
    background: #4F46E5 !important;
    color: #FFFFFF !important;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 12px 0 12px auto;
    max-width: 80%;
    font-size: 0.95rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.chat-user * { color: #FFFFFF !important; }

.chat-ai {
    background: #18181E !important;
    color: #F4F4F5 !important;
    padding: 18px 22px;
    border-radius: 18px 18px 18px 4px;
    margin: 12px 0;
    max-width: 88%;
    border: 1px solid #272732;
    font-size: 0.95rem;
    line-height: 1.65;
}
.chat-ai * { color: #F4F4F5 !important; }

/* Dark Form Controls */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #18181E !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid #272732 !important;
    border-radius: 12px !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #18181E !important;
    border: 2px dashed #2E2E3C !important;
    border-radius: 16px !important;
}
div[data-testid="stFileUploaderDropzone"] * { color: #A1A1AA !important; }

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(DRIBBBLE_SAAS_CSS, unsafe_allow_html=True)


# ============================================================
# PAGE VIEW 1: LANDING PAGE (8-CARD SHOWCASE)
# ============================================================
if st.session_state.view == "landing":
    
    # 1. Floating Pill Navbar
    ai_connected = chat_ai_available()
    status_html = (
        '<span class="status-badge"><span class="status-dot"></span>Cloud AI Active</span>'
        if ai_connected
        else '<span class="status-badge" style="color:#FBBF24 !important; border-color:rgba(251,191,36,0.3); background:rgba(251,191,36,0.1);"><span class="status-dot" style="background:#FBBF24;"></span>Offline Mode</span>'
    )

    st.markdown(
        f"""
        <div class="nav-pill-container">
            <div class="brand-title">
                {get_logo_html(size=28)} Karpom AI
            </div>
            <div>
                {status_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Hero Header Section
    st.markdown(
        f"""
        <div class="hero-wrapper">
            <div class="hero-pill-badge">{get_logo_html(size=18)} Academic Intelligence Suite — 8 Powerful Tools</div>
            <h1 class="hero-headline">Build Your Mind,<br><span class="hero-italic">Accelerate</span> Your Knowledge</h1>
            <p class="hero-subtitle">
                An elite cognitive space engineered for students and researchers. Solve complex homework with Vision AI, 
                query textbooks, master interactive exams, and command voice intelligence in real time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. 8-Feature Visual Cards Deck
    st.markdown(f'<div class="section-tag">{get_logo_html(size=18)} SELECT A FEATURE TO LAUNCH WORKBENCH</div>', unsafe_allow_html=True)

    # Row 1 (Cards 1 to 4)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #8B5CF6;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(139, 92, 246, 0.15); color:#A78BFA;">🤖</div>
                        <span class="card-number">01</span>
                    </div>
                    <h4 class="card-title">Offline AI Chatbot</h4>
                    <p class="card-desc">Real-time conversational intelligence with zero-downtime offline fallback.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Chatbot ↗", key="btn_f1", use_container_width=True):
            open_workspace("1")

    with c2:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #0EA5E9;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(14, 165, 233, 0.15); color:#38BDF8;">🎤</div>
                        <span class="card-number">02</span>
                    </div>
                    <h4 class="card-title">Voice Asking</h4>
                    <p class="card-desc">Speech-to-text question solving with instant audio transcription.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Voice Q&A ↗", key="btn_f2", use_container_width=True):
            open_workspace("2")

    with c3:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #F43F5E;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(244, 63, 94, 0.15); color:#FB7185;">📷</div>
                        <span class="card-number">03</span>
                    </div>
                    <h4 class="card-title">Image Question Solver</h4>
                    <p class="card-desc">Vision AI step-by-step solver for handwritten math, diagrams, & book covers.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Vision Solver ↗", key="btn_f3", use_container_width=True):
            open_workspace("3")

    with c4:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #10B981;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(16, 185, 129, 0.15); color:#34D399;">📄</div>
                        <span class="card-number">04</span>
                    </div>
                    <h4 class="card-title">PDF / Notes Q&A</h4>
                    <p class="card-desc">Chat directly with uploaded research papers, textbooks, and lecture slides.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Document Q&A ↗", key="btn_f4", use_container_width=True):
            open_workspace("4")

    # Row 2 (Cards 5 to 8)
    c5, c6, c7, c8 = st.columns(4)

    with c5:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #F59E0B;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(245, 158, 11, 0.15); color:#FBBF24;">📝</div>
                        <span class="card-number">05</span>
                    </div>
                    <h4 class="card-title">AI Notes Generator</h4>
                    <p class="card-desc">Synthesize lecture transcripts into structured Cornell notes and recall cues.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Notes Maker ↗", key="btn_f5", use_container_width=True):
            open_workspace("5")

    with c6:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #D946EF;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(217, 70, 239, 0.15); color:#E879F9;">🧠</div>
                        <span class="card-number">06</span>
                    </div>
                    <h4 class="card-title">MCQ & Exam Generator</h4>
                    <p class="card-desc">Generate tailored practice tests with answer keys and deep explanations.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Quiz Generator ↗", key="btn_f6", use_container_width=True):
            open_workspace("6")

    with c7:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #3B82F6;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(59, 130, 246, 0.15); color:#60A5FA;">📅</div>
                        <span class="card-number">07</span>
                    </div>
                    <h4 class="card-title">Study Planner</h4>
                    <p class="card-desc">Personalized milestone revision roadmaps customized to your exam schedule.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Study Planner ↗", key="btn_f7", use_container_width=True):
            open_workspace("7")

    with c8:
        st.markdown(
            """
            <div class="feature-card" style="border-top: 3px solid #14B8A6;">
                <div>
                    <div class="card-top">
                        <div class="card-icon" style="background: rgba(20, 184, 166, 0.15); color:#2DD4BF;">🌐</div>
                        <span class="card-number">08</span>
                    </div>
                    <h4 class="card-title">Translation & ELI5</h4>
                    <p class="card-desc">Translate study text into 20+ languages with Explain-Like-I'm-5 adaptation.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Translator ↗", key="btn_f8", use_container_width=True):
            open_workspace("8")


# ============================================================
# PAGE VIEW 2: DEDICATED TOOL WORKSPACE
# ============================================================
elif st.session_state.view == "workspace":

    # Top Navigation Bar with Back Button
    nav_left, nav_center, nav_right = st.columns([1.5, 3, 1.5])
    with nav_left:
        if st.button("← Back to All Tools", key="btn_back_home", type="secondary"):
            back_to_landing()
    with nav_center:
        st.markdown(
            f"""
            <div style="text-align:center; display:flex; align-items:center; justify-content:center; gap:10px; font-weight:800; font-size:1.15rem; color:#FFFFFF;">
                {get_logo_html(size=24)} Karpom AI Workspace
            </div>
            """,
            unsafe_allow_html=True
        )
    with nav_right:
        if st.session_state.active_feature == "1":
            if st.button("🗑 Reset Chat", key="btn_reset_chat_top", type="secondary"):
                st.session_state.chat_history = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()

    # Workspace Container
    st.markdown('<div class="workbench-panel">', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 1. OFFLINE AI CHATBOT
    # ------------------------------------------------------------
    if st.session_state.active_feature == "1":
        st.markdown(
            """
            <div class="workbench-title">🤖 Feature 01: Conversational AI Copilot</div>
            <p class="workbench-desc">Real-time token streaming intelligence for deep problem solving, code generation, and study reasoning.</p>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.chat_history:
            st.markdown(
                """
                <div class="chat-ai">
                    👋 <b>Hello! I am your AI Academic Copilot.</b><br>
                    Ask me anything — write code, solve math derivations, analyze essay logic, or review study concepts.
                </div>
                """,
                unsafe_allow_html=True,
            )

        for turn in st.session_state.chat_history:
            css = "chat-user" if turn["role"] == "user" else "chat-ai"
            sender = "👤 You" if turn["role"] == "user" else "Karpom AI"
            st.markdown(f'<div class="{css}"><div style="font-size:0.75rem; font-weight:700; opacity:0.85; margin-bottom:5px;">{sender}</div><div>{turn["content"]}</div></div>', unsafe_allow_html=True)

        user_input = st.chat_input("Ask a question, enter code, or paste formulas...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            save_chat_message(st.session_state.session_id, "user", user_input)

            st.markdown(f'<div class="chat-user"><div style="font-size:0.75rem; font-weight:700; opacity:0.85; margin-bottom:5px;">👤 You</div><div>{user_input}</div></div>', unsafe_allow_html=True)
            with st.container():
                st.markdown(f'<div style="font-size:0.75rem; color:#818CF8; font-weight:800; margin:10px 0 4px;">{get_logo_html(size=16)} Karpom AI</div>', unsafe_allow_html=True)
                stream_gen = stream_answer(user_input, st.session_state.chat_history[:-1])
                full_ai = st.write_stream(stream_gen)

            st.session_state.chat_history.append({"role": "assistant", "content": full_ai})
            save_chat_message(st.session_state.session_id, "assistant", full_ai)
            st.rerun()

    # ------------------------------------------------------------
    # 2. VOICE QUESTION ASKING
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "2":
        st.markdown(
            """
            <div class="workbench-title">🎤 Feature 02: Voice Question Asking</div>
            <p class="workbench-desc">Speak your question directly. Speech recognition transcribes your voice and generates an instant step-by-step solution.</p>
            """,
            unsafe_allow_html=True,
        )

        audio_val = st.audio_input("Record Audio Question (Click mic to record)")
        if audio_val:
            with st.spinner("🎙️ Transcribing voice query..."):
                transcribed_text = transcribe_audio(audio_val.getvalue())
                st.info(f"📝 **Transcribed Question:** {transcribed_text}")
                
                if st.button("🚀 Answer Transcribed Question", type="primary"):
                    with st.spinner("Computing solution..."):
                        stream_gen = stream_answer(transcribed_text, [])
                        full_res = ""
                        for token in stream_gen:
                            full_res += token
                        st.markdown(f'<div class="chat-ai" style="max-width:100%;">{full_res}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 3. IMAGE QUESTION SOLVING
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "3":
        st.markdown(
            """
            <div class="workbench-title">📷 Feature 03: Vision Homework & Diagram Solver</div>
            <p class="workbench-desc">Upload an image or snap a photo of a math problem, circuit diagram, textbook page, or book cover.</p>
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

        custom_instr = st.text_input("Additional guidance (Optional):", placeholder="e.g. Solve step-by-step or teach the core concepts")

        if st.button("✨ Solve with Vision AI", type="primary"):
            if not img_data:
                st.warning("Please upload an image or capture a photo first.")
            else:
                with st.spinner("🔮 Neural Vision analyzing image & computing solution..."):
                    sol = solve_image_question(img_data, custom_instr)
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;"><h4 style="color:#FB7185; margin:0 0 10px;">📝 Step-by-Step Solution</h4><div style="line-height:1.7;">{sol}</div></div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 4. PDF / NOTES Q&A
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "4":
        st.markdown(
            """
            <div class="workbench-title">📄 Feature 04: Document Q&A & Research RAG</div>
            <p class="workbench-desc">Upload study notes, research papers, or syllabus documents to ask targeted questions.</p>
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
                        st.markdown(f'<div class="chat-ai" style="max-width:100%;"><h4 style="color:#34D399; margin:0 0 10px;">💡 Document Answer</h4><p style="line-height:1.7; font-size:0.98rem; margin:0;">{ans}</p></div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 5. AI NOTES GENERATOR
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "5":
        st.markdown(
            """
            <div class="workbench-title">📝 Feature 05: AI Cornell Notes Generator</div>
            <p class="workbench-desc">Convert raw lecture transcripts into high-yield Cornell study guides with flashcard recall cues.</p>
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
    elif st.session_state.active_feature == "6":
        st.markdown(
            """
            <div class="workbench-title">🧠 Feature 06: MCQ & Practice Exam Generator</div>
            <p class="workbench-desc">Generate customized multiple-choice practice exams with answer keys and explanations from any topic.</p>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            q_topic = st.text_input("Quiz Topic or Subject:", placeholder="e.g. Graph Algorithms & Shortest Path")
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
    elif st.session_state.active_feature == "7":
        st.markdown(
            """
            <div class="workbench-title">📅 Feature 07: Personalized Study Planner</div>
            <p class="workbench-desc">Build a day-by-day milestone roadmap based on your exam date, subjects, and daily study hours.</p>
            """,
            unsafe_allow_html=True,
        )

        p_c1, p_c2 = st.columns(2)
        with p_c1:
            subj_list = st.text_area("Subjects / Syllabus Topics:", placeholder="e.g. Database Systems, Machine Learning Theory, Operating Systems")
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
    elif st.session_state.active_feature == "8":
        st.markdown(
            """
            <div class="workbench-title">🌐 Feature 08: Multilingual Translation & ELI5 Simplifier</div>
            <p class="workbench-desc">Translate complex academic theory into 20+ languages and adjust the explanation complexity.</p>
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
