"""
Karpom AI - Next-Gen Academic Intelligence Platform
Harmoniq Editorial Light Design & Multi-View Workspace
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
    page_title="Karpom AI | Your Haven for Academic Intelligence",
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
def get_logo_html(size: int = 28):
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

def navigate_to(view_name: str, feature_id: str = None):
    st.session_state.view = view_name
    if feature_id:
        st.session_state.active_feature = feature_id
    st.rerun()

# ============================================================
# HARMONIQ EDITORIAL SERENE THEME CSS
# ============================================================
HARMONIQ_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-page: #FAF9F6;
    --text-primary: #121417;
    --text-secondary: #5E6470;
    --border-subtle: rgba(0, 0, 0, 0.08);
    --card-bg: #FFFFFF;
    --accent: #111827;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background-color: var(--bg-page) !important;
}

.main .block-container {
    max-width: 1280px;
    padding: 1rem 1.5rem 3rem;
}

/* Harmoniq Navbar */
.harmoniq-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0 28px;
}

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #111827 !important;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 32px;
    font-size: 0.95rem;
    font-weight: 500;
    color: #4B5563;
}

/* Arch Dome Glow for Hero */
.hero-dome-wrapper {
    position: relative;
    text-align: center;
    padding: 30px 20px 20px;
    margin: 0 auto;
    max-width: 960px;
}

.hero-dome-bg {
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    width: 760px;
    height: 400px;
    background: radial-gradient(circle, rgba(219, 234, 254, 0.7) 0%, rgba(240, 246, 255, 0.4) 45%, transparent 70%);
    border-radius: 500px 500px 0 0;
    z-index: 0;
    pointer-events: none;
}

/* Orbit Floating Badges */
.floating-orbit-badge {
    position: absolute;
    width: 48px;
    height: 48px;
    background: #FFFFFF;
    border-radius: 14px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.07);
    border: 1px solid rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    animation: floatAnim 4s ease-in-out infinite alternate;
}

@keyframes floatAnim {
    0% { transform: translateY(0px); }
    100% { transform: translateY(-8px); }
}

.badge-pos-1 { top: 20px; left: 14%; animation-delay: 0s; }
.badge-pos-2 { top: -10px; left: 30%; animation-delay: 0.8s; }
.badge-pos-3 { top: -25px; left: 50%; transform: translateX(-50%); animation-delay: 0.4s; }
.badge-pos-4 { top: -10px; right: 30%; animation-delay: 1.2s; }
.badge-pos-5 { top: 20px; right: 14%; animation-delay: 0.6s; }

/* Editorial Hero Typography */
.hero-content {
    position: relative;
    z-index: 1;
}

.announcement-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    padding: 6px 18px;
    border-radius: 9999px;
    font-size: 0.86rem;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 24px;
}

.hero-editorial-title {
    font-family: 'Instrument Serif', serif;
    font-size: 4.6rem;
    font-weight: 400;
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: #111827;
    margin: 0 0 18px;
}

.hero-editorial-title i {
    font-style: italic;
    color: #4F46E5;
}

.hero-subtext {
    font-size: 1.12rem;
    color: #5E6470;
    max-width: 660px;
    margin: 0 auto 32px;
    line-height: 1.6;
}

/* Feature Cards */
.harmoniq-card {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.03);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 12px;
}

.harmoniq-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.07);
    border-color: rgba(99, 102, 241, 0.3);
}

.card-icon-pill {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 14px;
}

.card-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    color: #9CA3AF;
}

.card-h {
    font-size: 1.18rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #111827 !important;
    margin: 0 0 6px;
}

.card-p {
    font-size: 0.88rem;
    color: #6B7280 !important;
    line-height: 1.45;
    margin: 0;
}

/* Button Customization */
div[data-testid="stButton"] > button {
    border-radius: 9999px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 8px 24px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #111827 !important;
    color: #FFFFFF !important;
    border: 1px solid #111827 !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #000000 !important;
    transform: scale(1.02);
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #374151 !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background-color: #F3F4F6 !important;
    border-color: #9CA3AF !important;
}

/* Landscape Scenic Backdrop Footer */
.scenic-footer {
    position: relative;
    width: 100%;
    height: 220px;
    margin-top: 50px;
    border-radius: 28px;
    background: linear-gradient(180deg, rgba(250,249,246,0) 0%, rgba(219,234,254,0.3) 30%, rgba(187,247,208,0.3) 100%),
                url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 24px;
    box-shadow: inset 0 20px 40px var(--bg-page);
}

/* Workbench View Specifics */
.workbench-header {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 20px;
    padding: 20px 28px;
    margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

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
st.markdown(HARMONIQ_CSS, unsafe_allow_html=True)

# Tool metadata
TOOLS = [
    {"id": "1", "icon": "🤖", "name": "Offline AI Chatbot", "desc": "Conversational copilot with offline fallback.", "bg": "#EDE9FE", "color": "#7C3AED"},
    {"id": "2", "icon": "🎙️", "name": "Voice Question Asking", "desc": "Speak complex queries with instant speech transcription.", "bg": "#E0F2FE", "color": "#0284C7"},
    {"id": "3", "icon": "📷", "name": "Image & Math Solver", "desc": "Vision AI solving handwritten equations & diagrams.", "bg": "#FFE4E6", "color": "#E11D48"},
    {"id": "4", "icon": "📄", "name": "PDF & Notes Q&A", "desc": "Ground research and book questions into uploaded docs.", "bg": "#D1FAE5", "color": "#059669"},
    {"id": "5", "icon": "📝", "name": "Cornell Notes Generator", "desc": "Convert lecture transcripts into structured recall cues.", "bg": "#FEF3C7", "color": "#D97706"},
    {"id": "6", "icon": "🧠", "name": "MCQ & Exam Generator", "desc": "Practice tests tailored to any syllabus or topic.", "bg": "#FAE8FF", "color": "#C026D3"},
    {"id": "7", "icon": "📅", "name": "Smart Study Planner", "desc": "Day-by-day milestone roadmap customized to exam dates.", "bg": "#DBEAFE", "color": "#2563EB"},
    {"id": "8", "icon": "🌐", "name": "Multilingual & ELI5", "desc": "Translate academic theory with 5-level simplification.", "bg": "#CCFBF1", "color": "#0D9488"},
]

# ============================================================
# VIEW 1: HARMONIQ LANDING PAGE
# ============================================================
if st.session_state.view == "landing":
    
    # 1. Top Navbar
    ai_status = chat_ai_available()
    status_tag = (
        '<span style="color:#059669; font-weight:700; font-size:0.8rem; background:#D1FAE5; padding:4px 12px; border-radius:9999px;">● Cloud AI Active</span>'
        if ai_status else
        '<span style="color:#D97706; font-weight:700; font-size:0.8rem; background:#FEF3C7; padding:4px 12px; border-radius:9999px;">● Offline Ready</span>'
    )
    
    n_col1, n_col2 = st.columns([1, 1])
    with n_col1:
        st.markdown(
            f"""
            <div class="brand-wrapper">
                {get_logo_html(size=32)} Karpom AI
            </div>
            """,
            unsafe_allow_html=True
        )
    with n_col2:
        btn_c1, btn_c2 = st.columns([2, 1])
        with btn_c1:
            st.markdown(f'<div style="text-align:right; padding-top:8px;">{status_tag}</div>', unsafe_allow_html=True)
        with btn_c2:
            if st.button("Open App ➔", key="nav_launch_top", type="primary", use_container_width=True):
                navigate_to("workspace", "1")

    # 2. Harmoniq Arched Hero Section
    st.markdown(
        f"""
        <div class="hero-dome-wrapper">
            <div class="hero-dome-bg"></div>
            
            <!-- Orbit Badges -->
            <div class="floating-orbit-badge badge-pos-1">📝</div>
            <div class="floating-orbit-badge badge-pos-2">📷</div>
            <div class="floating-orbit-badge badge-pos-3">🤖</div>
            <div class="floating-orbit-badge badge-pos-4">🧠</div>
            <div class="floating-orbit-badge badge-pos-5">🎙️</div>
            
            <div class="hero-content">
                <div class="announcement-pill">
                    {get_logo_html(size=18)} Academic Intelligence 2.0 • 8 Super Tools 🚀
                </div>
                <h1 class="hero-editorial-title">
                    Your Haven for <i>Seamless</i><br>Academic Mastery
                </h1>
                <p class="hero-subtext">
                    Empowering students, engineers, and researchers with effortless AI tools to conquer complex exams, 
                    decode handwritten math, query research documents, and synthesize knowledge effortlessly.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # CTA Buttons (Hero)
    cta_c1, cta_c2, cta_c3 = st.columns([1.5, 1, 1.5])
    with cta_c2:
        if st.button("✨ Launch Workspace", key="hero_cta_btn", type="primary", use_container_width=True):
            navigate_to("workspace", "1")

    st.write("")
    st.write("")

    # 3. 8-Tool Bento Showcase Deck
    st.markdown('<div style="font-size:0.85rem; font-weight:800; color:#6B7280; text-transform:uppercase; letter-spacing:0.08em; text-align:center; margin:30px 0 16px;">✨ Explore All Intelligence Engines</div>', unsafe_allow_html=True)

    # Row 1 (Tools 1 to 4)
    r1_cols = st.columns(4)
    for idx in range(4):
        tool = TOOLS[idx]
        with r1_cols[idx]:
            st.markdown(
                f"""
                <div class="harmoniq-card">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="card-icon-pill" style="background:{tool['bg']}; color:{tool['color']};">{tool['icon']}</div>
                            <span class="card-num">0{tool['id']}</span>
                        </div>
                        <h3 class="card-h">{tool['name']}</h3>
                        <p class="card-p">{tool['desc']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Launch 0{tool['id']} ↗", key=f"btn_land_{tool['id']}", use_container_width=True, type="secondary"):
                navigate_to("workspace", tool["id"])

    # Row 2 (Tools 5 to 8)
    r2_cols = st.columns(4)
    for idx in range(4, 8):
        tool = TOOLS[idx]
        with r2_cols[idx - 4]:
            st.markdown(
                f"""
                <div class="harmoniq-card">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="card-icon-pill" style="background:{tool['bg']}; color:{tool['color']};">{tool['icon']}</div>
                            <span class="card-num">0{tool['id']}</span>
                        </div>
                        <h3 class="card-h">{tool['name']}</h3>
                        <p class="card-p">{tool['desc']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Launch 0{tool['id']} ↗", key=f"btn_land_{tool['id']}", use_container_width=True, type="secondary"):
                navigate_to("workspace", tool["id"])

    # 4. Lush Scenic Footer
    st.markdown(
        f"""
        <div class="scenic-footer">
            <div style="background:rgba(255,255,255,0.9); backdrop-filter:blur(8px); padding:8px 24px; border-radius:9999px; font-weight:700; font-size:0.88rem; color:#111827; box-shadow:0 4px 20px rgba(0,0,0,0.08);">
                {get_logo_html(size=20)} Karpom AI • Designed for Intellectual Acceleration
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# VIEW 2: DEDICATED APP WORKBENCH PAGE
# ============================================================
elif st.session_state.view == "workspace":

    # Top Bar with Back to Home
    top_col1, top_col2, top_col3 = st.columns([1.2, 3, 1])
    with top_col1:
        if st.button("← Back to Home", key="btn_back_home", type="secondary"):
            navigate_to("landing")
    with top_col2:
        st.markdown(
            f"""
            <div style="text-align:center; display:flex; align-items:center; justify-content:center; gap:10px;">
                {get_logo_html(size=26)}
                <span style="font-weight:800; font-size:1.15rem; color:#111827;">Karpom AI Workspace</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with top_col3:
        if st.button("Reset Session 🗑", key="btn_reset_ws", type="secondary"):
            st.session_state.chat_history = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

    # Tool Navigation Switcher Pill Bar
    tool_names = [f"0{t['id']}. {t['name']}" for t in TOOLS]
    current_idx = int(st.session_state.active_feature) - 1
    selected_tool_str = st.radio(
        "Switch Tool:",
        tool_names,
        index=current_idx,
        horizontal=True,
        label_visibility="collapsed"
    )
    new_feat_id = selected_tool_str.split(".")[0].replace("0", "")
    if new_feat_id != st.session_state.active_feature:
        st.session_state.active_feature = new_feat_id
        st.rerun()

    st.write("")

    # ------------------------------------------------------------
    # 1. OFFLINE AI CHATBOT
    # ------------------------------------------------------------
    if st.session_state.active_feature == "1":
        st.markdown(
            """
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">🤖 Feature 01: Conversational AI Copilot</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Real-time token streaming for deep problem solving, code reasoning, and conceptual proofs.</p>
                </div>
            </div>
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
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">🎙️ Feature 02: Voice Question Asking</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Speak your question directly. Speech recognition transcribes and solves it instantly.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        audio_val = st.audio_input("Record Voice Query (Click mic)")
        if audio_val:
            with st.spinner("🎙️ Transcribing voice question..."):
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
    # 3. IMAGE & MATH QUESTION SOLVER
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "3":
        st.markdown(
            """
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">📷 Feature 03: Vision Homework & Diagram Solver</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Upload or snap a photo of any handwritten math problem, circuit diagram, or textbook page.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        t1, t2 = st.tabs(["📁 Upload Image", "📸 Live Camera Snap"])
        img_data = None

        with t1:
            u_file = st.file_uploader("Upload Question Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if u_file:
                img_data = u_file.getvalue()
                st.image(u_file, width=400)
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
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">📄 Feature 04: Document Q&A & Research RAG</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Upload lecture slides, syllabus PDFs, or research papers and query them with strict factual grounding.</p>
                </div>
            </div>
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
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">📝 Feature 05: Cornell Notes Generator</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Turn raw lecture transcripts into high-yield Cornell study guides with flashcard recall cues.</p>
                </div>
            </div>
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
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">🧠 Feature 06: MCQ & Practice Exam Generator</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Generate customized practice tests with deep explanations and full answer keys.</p>
                </div>
            </div>
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
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">📅 Feature 07: Personalized Study Planner</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Build a structured milestone revision roadmap tailored to your upcoming test date.</p>
                </div>
            </div>
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
            <div class="workbench-header">
                <div>
                    <h3 style="margin:0 0 4px; font-size:1.3rem; font-weight:800; color:#111827;">🌐 Feature 08: Multilingual Translation & ELI5 Simplifier</h3>
                    <p style="margin:0; color:#6B7280; font-size:0.9rem;">Translate complex academic theory into 20+ languages and adjust cognitive difficulty levels.</p>
                </div>
            </div>
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
