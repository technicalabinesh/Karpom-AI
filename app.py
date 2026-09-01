"""
Karpom AI - Next-Gen Academic Intelligence Platform
Harmoniq Editorial Light Design + Dedicated Workspace Routing
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

def get_logo_path():
    for fname in ["logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "logo.svg"]:
        if os.path.exists(fname):
            return fname
    return "🌸"

st.set_page_config(
    page_title="Karpom AI | Your Sanctuary for Academic Intelligence",
    page_icon=get_logo_path(),
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

# Dynamic Logo Engine
def get_logo_html(size: int = 32):
    """Loads custom logo.png from project root with optimized styling."""
    for fname in ["logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "logo.svg"]:
        if os.path.exists(fname):
            try:
                with open(fname, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/svg+xml" if fname.endswith(".svg") else "image/png"
                return (
                    f'<span style="display:inline-flex; align-items:center; justify-content:center; '
                    f'background:#FFFFFF; border-radius:10px; padding:2px; vertical-align:middle; '
                    f'box-shadow: 0 2px 8px rgba(0,0,0,0.06);">'
                    f'<img src="data:{mime};base64,{b64}" width="{size}" height="{size}" '
                    f'style="object-fit:contain; border-radius:8px; display:block;" />'
                    f'</span>'
                )
            except Exception:
                pass
    return f'<span style="font-size:{size-6}px; vertical-align:middle;">🌸</span>'

# ============================================================
# STATE INITIALIZATION & ROUTING
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

def open_tool(tool_id: str):
    st.session_state.active_feature = tool_id
    st.session_state.view = "workspace"
    st.rerun()

def back_home():
    st.session_state.view = "landing"
    st.rerun()

# ============================================================
# EDITORIAL DESIGN SYSTEM CSS
# ============================================================
EDITORIAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-page: #FAF9F6;
    --text-main: #111827;
    --text-muted: #5E6470;
    --accent-dark: #111827;
    --brand-indigo: #4F46E5;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-page) !important;
    color: var(--text-main) !important;
}

.stApp {
    background-color: var(--bg-page) !important;
}

.main .block-container {
    max-width: 1240px;
    padding: 1.25rem 1.5rem 4rem;
}

/* Navbar */
.navbar-clean {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0 24px;
}

.nav-brand {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 10px;
    color: #111827 !important;
}

.status-badge-light {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
}

/* Hero Section with Arch Glow */
.hero-wrapper {
    position: relative;
    text-align: center;
    padding: 30px 20px 24px;
    max-width: 940px;
    margin: 0 auto;
}

.hero-arch-bg {
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    width: 740px;
    height: 380px;
    background: radial-gradient(circle, rgba(224, 231, 255, 0.7) 0%, rgba(243, 244, 246, 0.4) 50%, transparent 70%);
    border-radius: 400px 400px 0 0;
    z-index: 0;
    pointer-events: none;
}

.hero-orbit-pill {
    position: absolute;
    width: 44px;
    height: 44px;
    background: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    animation: float 4s ease-in-out infinite alternate;
}

@keyframes float {
    0% { transform: translateY(0px); }
    100% { transform: translateY(-7px); }
}

.orbit-1 { top: 20px; left: 12%; animation-delay: 0s; }
.orbit-2 { top: -10px; left: 28%; animation-delay: 0.8s; }
.orbit-3 { top: -20px; right: 28%; animation-delay: 0.4s; }
.orbit-4 { top: 20px; right: 12%; animation-delay: 1.2s; }

.hero-inner {
    position: relative;
    z-index: 1;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    padding: 6px 18px;
    border-radius: 9999px;
    font-size: 0.84rem;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 20px;
}

.hero-title {
    font-family: 'Instrument Serif', serif;
    font-size: 4.5rem;
    font-weight: 400;
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: #111827;
    margin: 0 0 16px;
}

.hero-title i {
    font-style: italic;
    color: #4F46E5;
}

.hero-desc {
    font-size: 1.1rem;
    color: #5E6470;
    max-width: 660px;
    margin: 0 auto 30px;
    line-height: 1.6;
}

/* Bento Stat Cards */
.bento-card {
    border-radius: 24px;
    padding: 28px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.25s ease;
}

.bento-primary {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
    color: #FFFFFF !important;
}
.bento-primary * { color: #FFFFFF !important; }

.bento-white {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03);
}

.bento-lime {
    background: #D4FF00;
    color: #111827 !important;
}
.bento-lime * { color: #111827 !important; }

.bento-num {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 14px 0 6px;
}

/* Feature Cards */
.card-clean {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.02);
    min-height: 195px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.25s ease;
    margin-bottom: 12px;
}

.card-clean:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.06);
    border-color: #4F46E5;
}

.card-icon-box {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 12px;
}

.card-title-text {
    font-size: 1.12rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #111827;
    margin: 0 0 4px;
}

.card-desc-text {
    font-size: 0.86rem;
    color: #6B7280;
    line-height: 1.45;
    margin: 0;
}

/* Custom Buttons */
div[data-testid="stButton"] > button {
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #111827 !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #000000 !important;
    transform: scale(1.02);
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background-color: #F3F4F6 !important;
    border-color: #9CA3AF !important;
}

/* Workspace Specifics */
.ws-panel {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 24px;
    padding: 30px;
    margin-top: 14px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
}

.ws-title {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0 0 4px;
    color: #111827 !important;
}

.ws-desc {
    font-size: 0.92rem;
    color: #6B7280 !important;
    margin: 0 0 24px;
}

/* Chat UI */
.chat-user {
    background: #111827 !important;
    color: #FFFFFF !important;
    padding: 14px 20px;
    border-radius: 20px 20px 4px 20px;
    margin: 12px 0 12px auto;
    max-width: 80%;
    font-size: 0.95rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.chat-user * { color: #FFFFFF !important; }

.chat-ai {
    background: #FFFFFF !important;
    color: #1F2937 !important;
    padding: 20px 24px;
    border-radius: 20px 20px 20px 4px;
    margin: 12px 0;
    max-width: 88%;
    border: 1px solid rgba(0, 0, 0, 0.08);
    font-size: 0.95rem;
    line-height: 1.65;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    border-radius: 12px !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(EDITORIAL_CSS, unsafe_allow_html=True)

# 8 Intelligence Tools Specifications
TOOLS = [
    {"id": "1", "icon": "🤖", "name": "Offline AI Chatbot", "desc": "Deep reasoning conversational copilot with offline fallback.", "bg": "#EDE9FE", "color": "#7C3AED", "category": "Core Reasoning"},
    {"id": "2", "icon": "🎙️", "name": "Voice Question Asking", "desc": "Speak complex queries with instant neural transcription.", "bg": "#E0F2FE", "color": "#0284C7", "category": "Core Reasoning"},
    {"id": "3", "icon": "📷", "name": "Vision Homework Solver", "desc": "Step-by-step solver for handwritten math & diagrams.", "bg": "#FFE4E6", "color": "#E11D48", "category": "Document & Vision"},
    {"id": "4", "icon": "📄", "name": "PDF & Notes Q&A", "desc": "Ground research and textbook questions into uploaded files.", "bg": "#D1FAE5", "color": "#059669", "category": "Document & Vision"},
    {"id": "5", "icon": "📝", "name": "Cornell Notes Maker", "desc": "Convert lecture transcripts into high-yield recall cues.", "bg": "#FEF3C7", "color": "#D97706", "category": "Exam Mastery"},
    {"id": "6", "icon": "🧠", "name": "MCQ & Exam Engine", "desc": "Practice tests tailored to any syllabus or difficulty level.", "bg": "#FAE8FF", "color": "#C026D3", "category": "Exam Mastery"},
    {"id": "7", "icon": "📅", "name": "Smart Study Planner", "desc": "Milestone revision roadmap customized to test dates.", "bg": "#DBEAFE", "color": "#2563EB", "category": "Exam Mastery"},
    {"id": "8", "icon": "🌐", "name": "Translation & ELI5", "desc": "Translate academic theory with 5-tier complexity levels.", "bg": "#CCFBF1", "color": "#0D9488", "category": "Core Reasoning"},
]

# ============================================================
# VIEW 1: LANDING PAGE
# ============================================================
if st.session_state.view == "landing":

    # 1. Top Navbar
    ai_status = chat_ai_available()
    status_html = (
        '<span class="status-badge-light" style="background:#D1FAE5; color:#059669;">● Cloud AI Active</span>'
        if ai_status else
        '<span class="status-badge-light" style="background:#FEF3C7; color:#D97706;">● Offline Mode Ready</span>'
    )

    n1, n2 = st.columns([1, 1])
    with n1:
        st.markdown(f'<div class="nav-brand">{get_logo_html(size=30)} Karpom AI</div>', unsafe_allow_html=True)
    with n2:
        c_status, c_btn = st.columns([2, 1])
        with c_status:
            st.markdown(f'<div style="text-align:right; padding-top:6px;">{status_html}</div>', unsafe_allow_html=True)
        with c_btn:
            if st.button("Launch App ↗", key="nav_btn_launch", type="primary", use_container_width=True):
                open_tool("1")

    # 2. Hero Section
    st.markdown(
        f"""
        <div class="hero-wrapper">
            <div class="hero-arch-bg"></div>
            
            <div class="hero-orbit-pill orbit-1">🤖</div>
            <div class="hero-orbit-pill orbit-2">📷</div>
            <div class="hero-orbit-pill orbit-3">📝</div>
            <div class="hero-orbit-pill orbit-4">🧠</div>
            
            <div class="hero-inner">
                <div class="hero-badge">
                    {get_logo_html(size=18)} Next-Gen Academic Intelligence Suite 🚀
                </div>
                <h1 class="hero-title">
                    Your Sanctuary for <i>Seamless</i><br>Academic Mastery
                </h1>
                <p class="hero-desc">
                    An elite cognitive workspace built for students and researchers. Solve complex homework with Vision AI, 
                    query textbooks, generate Cornell notes, and command voice intelligence effortlessly.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    h_btn1, h_btn2, h_btn3 = st.columns([1.5, 1, 1.5])
    with h_btn2:
        if st.button("✨ Enter Workspace", key="hero_enter_btn", type="primary", use_container_width=True):
            open_tool("1")

    st.write("")

    # 3. Bento Stats Grid
    b1, b2, b3 = st.columns([1.3, 1, 1])
    with b1:
        st.markdown(
            """
            <div class="bento-card bento-primary">
                <div style="font-size:0.85rem; font-weight:700; letter-spacing:0.06em; opacity:0.85;">KARPOM RESEARCH ENGINE</div>
                <div>
                    <div class="bento-num">120+</div>
                    <div style="font-size:0.95rem; opacity:0.9;">Universities and competitive exam curricula indexed and supported.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b2:
        st.markdown(
            """
            <div class="bento-card bento-white">
                <div style="font-size:0.82rem; font-weight:700; color:#6B7280; text-transform:uppercase;">Fact Grounding</div>
                <div>
                    <div class="bento-num" style="color:#111827;">100%</div>
                    <p style="font-size:0.88rem; color:#6B7280; margin:0;">Zero hallucinations with strict citation-based document answers.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b3:
        st.markdown(
            """
            <div class="bento-card bento-lime">
                <div style="font-size:0.82rem; font-weight:800; text-transform:uppercase;">Questions Solved</div>
                <div>
                    <div class="bento-num">520k+</div>
                    <div style="font-size:0.88rem; font-weight:600;">Handwritten problems solved with full step-by-step proofs.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. 8-Tool Visual Cards Showcase
    st.write("")
    st.markdown(
        """
        <div style="text-align:center; margin:40px 0 20px;">
            <div style="font-size:0.8rem; font-weight:800; color:#6B7280; text-transform:uppercase; letter-spacing:0.08em;">• ALL 8 TOOLS READY •</div>
            <h2 style="font-size:2.2rem; font-weight:800; letter-spacing:-0.03em; margin:4px 0 0;">Select a Feature to Launch Workbench</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Row 1 (Tools 1 to 4)
    r1 = st.columns(4)
    for idx in range(4):
        tool = TOOLS[idx]
        with r1[idx]:
            st.markdown(
                f"""
                <div class="card-clean">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="card-icon-box" style="background:{tool['bg']}; color:{tool['color']};">{tool['icon']}</div>
                            <span style="font-family:'JetBrains Mono'; font-size:0.75rem; font-weight:700; color:#9CA3AF;">0{tool['id']}</span>
                        </div>
                        <h4 class="card-title-text">{tool['name']}</h4>
                        <p class="card-desc-text">{tool['desc']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Launch 0{tool['id']} ↗", key=f"btn_t_{tool['id']}", use_container_width=True, type="secondary"):
                open_tool(tool["id"])

    # Row 2 (Tools 5 to 8)
    r2 = st.columns(4)
    for idx in range(4, 8):
        tool = TOOLS[idx]
        with r2[idx - 4]:
            st.markdown(
                f"""
                <div class="card-clean">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="card-icon-box" style="background:{tool['bg']}; color:{tool['color']};">{tool['icon']}</div>
                            <span style="font-family:'JetBrains Mono'; font-size:0.75rem; font-weight:700; color:#9CA3AF;">0{tool['id']}</span>
                        </div>
                        <h4 class="card-title-text">{tool['name']}</h4>
                        <p class="card-desc-text">{tool['desc']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Launch 0{tool['id']} ↗", key=f"btn_t_{tool['id']}", use_container_width=True, type="secondary"):
                open_tool(tool["id"])


# ============================================================
# VIEW 2: DEDICATED TOOL WORKSPACE
# ============================================================
elif st.session_state.view == "workspace":

    # Top Bar Navigation
    top_c1, top_c2, top_c3 = st.columns([1.5, 3, 1.5])
    with top_c1:
        if st.button("← Back to All Tools", key="btn_back_home_ws", type="secondary"):
            back_home()
    with top_c2:
        st.markdown(
            f"""
            <div style="text-align:center; display:flex; align-items:center; justify-content:center; gap:8px; font-weight:800; font-size:1.18rem; color:#111827;">
                {get_logo_html(size=26)} Karpom AI Workspace
            </div>
            """,
            unsafe_allow_html=True
        )
    with top_c3:
        if st.session_state.active_feature == "1":
            if st.button("🗑 Reset Session", key="btn_reset_chat", type="secondary"):
                st.session_state.chat_history = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()

    # Tool Navigation Switcher Pill Bar
    tool_names = [f"0{t['id']}. {t['name']}" for t in TOOLS]
    curr_idx = int(st.session_state.active_feature) - 1
    selected_tool_str = st.radio(
        "Switch Workspace Tool:",
        tool_names,
        index=curr_idx,
        horizontal=True,
        label_visibility="collapsed"
    )
    new_id = selected_tool_str.split(".")[0].replace("0", "")
    if new_id != st.session_state.active_feature:
        st.session_state.active_feature = new_id
        st.rerun()

    # Workspace Panel
    st.markdown('<div class="ws-panel">', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 1. OFFLINE AI CHATBOT
    # ------------------------------------------------------------
    if st.session_state.active_feature == "1":
        st.markdown(
            """
            <div class="ws-title">🤖 Feature 01: Conversational AI Copilot</div>
            <p class="ws-desc">Real-time token streaming for deep academic problem solving, code reasoning, and conceptual proofs.</p>
            """,
            unsafe_allow_html=True
        )

        if not st.session_state.chat_history:
            st.markdown(
                """
                <div class="chat-ai">
                    👋 <b>Hello! I am your Karpom AI Academic Copilot.</b><br>
                    Ask me anything — write code, solve math derivations, analyze essay logic, or review study concepts.
                </div>
                """,
                unsafe_allow_html=True,
            )

        for turn in st.session_state.chat_history:
            css = "chat-user" if turn["role"] == "user" else "chat-ai"
            sender = "👤 You" if turn["role"] == "user" else f"{get_logo_html(size=18)} Karpom AI"
            st.markdown(f'<div class="{css}"><div style="font-size:0.75rem; font-weight:700; opacity:0.8; margin-bottom:5px;">{sender}</div><div>{turn["content"]}</div></div>', unsafe_allow_html=True)

        user_input = st.chat_input("Ask a question, enter code, or paste formulas...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            save_chat_message(st.session_state.session_id, "user", user_input)

            st.markdown(f'<div class="chat-user"><div style="font-size:0.75rem; font-weight:700; opacity:0.8; margin-bottom:5px;">👤 You</div><div>{user_input}</div></div>', unsafe_allow_html=True)
            with st.container():
                st.markdown(f'<div style="font-size:0.8rem; color:#4F46E5; font-weight:800; margin:10px 0 4px; display:flex; align-items:center; gap:6px;">{get_logo_html(size=16)} Karpom AI</div>', unsafe_allow_html=True)
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
            <div class="ws-title">🎙️ Feature 02: Voice Question Asking</div>
            <p class="ws-desc">Speak your question directly. Speech recognition transcribes and solves it instantly.</p>
            """,
            unsafe_allow_html=True
        )

        audio_val = st.audio_input("Record Voice Query (Click mic)")
        if audio_val:
            with st.spinner("🎙️ Transcribing voice query..."):
                transcribed_text = transcribe_audio(audio_val.getvalue())
                st.info(f"📝 **Transcribed Query:** {transcribed_text}")
                
                if st.button("🚀 Answer Transcribed Question", type="primary"):
                    with st.spinner("Computing solution..."):
                        stream_gen = stream_answer(transcribed_text, [])
                        full_res = ""
                        for token in stream_gen:
                            full_res += token
                        st.markdown(f'<div class="chat-ai" style="max-width:100%;">{full_res}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 3. VISION HOMEWORK & DIAGRAM SOLVER
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "3":
        st.markdown(
            """
            <div class="ws-title">📷 Feature 03: Vision Homework & Diagram Solver</div>
            <p class="ws-desc">Upload or snap a photo of any handwritten math problem, circuit diagram, or textbook page.</p>
            """,
            unsafe_allow_html=True
        )

        t1, t2 = st.tabs(["📁 Upload Image", "📸 Live Camera Snap"])
        img_data = None

        with t1:
            u_file = st.file_uploader("Upload Question Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if u_file:
                img_data = u_file.getvalue()
                st.image(u_file, width=420)
        with t2:
            c_file = st.camera_input("Take photo of question")
            if c_file:
                img_data = c_file.getvalue()

        custom_instr = st.text_input("Additional guidance (Optional):", placeholder="e.g. Show full algebraic derivation step-by-step")

        if st.button("✨ Solve with Vision AI", type="primary"):
            if not img_data:
                st.warning("Please upload an image or capture a photo first.")
            else:
                with st.spinner("🔮 Neural Vision analyzing question..."):
                    sol = solve_image_question(img_data, custom_instr)
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;"><h4 style="color:#E11D48; margin:0 0 10px;">📝 Step-by-Step Solution</h4><div style="line-height:1.7;">{sol}</div></div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 4. PDF / NOTES Q&A
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "4":
        st.markdown(
            """
            <div class="ws-title">📄 Feature 04: Document Q&A & Research RAG</div>
            <p class="ws-desc">Upload lecture slides, syllabus PDFs, or research papers and query them with strict factual grounding.</p>
            """,
            unsafe_allow_html=True
        )

        doc_f = st.file_uploader("Upload PDF or Word Document", type=["pdf", "docx", "txt", "md"])
        if doc_f:
            doc_raw = extract_text(doc_f)
            st.success(f"✓ Document Loaded: **{doc_f.name}** (~{len(doc_raw.split()):,} words)")

            q_input = st.text_input("Ask a question grounded in this document:")
            if st.button("🔍 Search & Answer", type="primary"):
                if q_input.strip():
                    with st.spinner("Searching document context..."):
                        ans = ask_document(doc_raw, q_input)
                        st.markdown(f'<div class="chat-ai" style="max-width:100%;"><h4 style="color:#059669; margin:0 0 10px;">💡 Answer from Document</h4><p style="line-height:1.7; margin:0;">{ans}</p></div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 5. AI CORNELL NOTES GENERATOR
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "5":
        st.markdown(
            """
            <div class="ws-title">📝 Feature 05: Cornell Notes Generator</div>
            <p class="ws-desc">Turn raw lecture transcripts into high-yield Cornell study guides with flashcard recall cues.</p>
            """,
            unsafe_allow_html=True
        )

        source_mode = st.radio("Input Method:", ["Paste Text / Transcript", "Upload Document File"], horizontal=True)
        raw_study_text = ""

        if source_mode == "Paste Text / Transcript":
            raw_study_text = st.text_area("Paste lecture text or transcript:", height=180)
        else:
            n_file = st.file_uploader("Upload file", type=["pdf", "docx", "txt"])
            if n_file:
                raw_study_text = extract_text(n_file)

        if st.button("✨ Generate Cornell Notes", type="primary"):
            if not raw_study_text.strip():
                st.warning("Please provide study text first.")
            else:
                with st.spinner("Structuring Cornell notes & recall cues..."):
                    c_notes = generate_cornell_notes(raw_study_text)
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;">{c_notes}</div>', unsafe_allow_html=True)
                    st.download_button("⬇ Download Cornell Notes (.txt)", data=c_notes, file_name="cornell_notes.txt", mime="text/plain")

    # ------------------------------------------------------------
    # 6. MCQ & PRACTICE EXAM GENERATOR
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "6":
        st.markdown(
            """
            <div class="ws-title">🧠 Feature 06: MCQ & Practice Exam Generator</div>
            <p class="ws-desc">Generate customized practice tests with deep explanations and full answer keys.</p>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            q_topic = st.text_input("Topic / Syllabus Subject:", placeholder="e.g. Graph Algorithms & Dynamic Programming")
        with c2:
            num_q = st.number_input("Number of MCQs:", min_value=3, max_value=20, value=5)
        with c3:
            diff_level = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard", "Finals Exam Level"])

        if st.button("🚀 Generate Exam Questions", type="primary"):
            if not q_topic.strip():
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Generating exam questions and answer keys..."):
                    quiz_output = generate_quiz(q_topic, num_q, diff_level)
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;">{quiz_output}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 7. PERSONALIZED STUDY PLANNER
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "7":
        st.markdown(
            """
            <div class="ws-title">📅 Feature 07: Personalized Study Planner</div>
            <p class="ws-desc">Build a structured milestone revision roadmap tailored to your upcoming test date.</p>
            """,
            unsafe_allow_html=True
        )

        p_c1, p_c2 = st.columns(2)
        with p_c1:
            subj_list = st.text_area("Subjects / Syllabus Topics:", placeholder="e.g. Operating Systems, Database Internals, Computer Networks")
            target_g = st.text_input("Target Goal:", placeholder="e.g. Score 90%+ in finals")
        with p_c2:
            days_remain = st.number_input("Days Remaining until Exam:", min_value=1, max_value=90, value=14)
            daily_hrs = st.slider("Available Daily Study Hours:", min_value=1.0, max_value=12.0, value=4.0, step=0.5)

        if st.button("🗓 Generate Study Schedule", type="primary"):
            if not subj_list.strip():
                st.warning("Please enter your subjects.")
            else:
                with st.spinner("Synthesizing daily roadmap..."):
                    s_plan = generate_study_plan(subj_list, days_remain, daily_hrs, target_g)
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;">{s_plan}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 8. MULTILINGUAL TRANSLATION + SIMPLIFICATION
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "8":
        st.markdown(
            """
            <div class="ws-title">🌐 Feature 08: Multilingual Translation & ELI5 Simplifier</div>
            <p class="ws-desc">Translate complex academic theory into 20+ languages and adjust cognitive difficulty levels.</p>
            """,
            unsafe_allow_html=True
        )

        t_src = st.text_area("Paste complex study content:", height=160)
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
                st.warning("Please enter text to translate.")
            else:
                with st.spinner("Translating and simplifying..."):
                    res_trans = translate_and_simplify(t_src, t_lang, simp_level)
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;">{res_trans}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
