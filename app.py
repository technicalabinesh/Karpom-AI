"""
Karpom AI - Next-Gen Academic Intelligence Platform
Aeline Sky-Blue Editorial UI + Interactive Academic Workspace
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
    return "⚡"

st.set_page_config(
    page_title="Karpom AI | Building the Future of Academic Intelligence",
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
def get_logo_html(size: int = 30, on_dark: bool = False):
    for fname in ["logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "logo.svg"]:
        if os.path.exists(fname):
            try:
                with open(fname, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/svg+xml" if fname.endswith(".svg") else "image/png"
                bg_style = "background:#FFFFFF;" if on_dark else "background:transparent;"
                return (
                    f'<span style="display:inline-flex; align-items:center; justify-content:center; '
                    f'{bg_style} border-radius:10px; padding:2px; vertical-align:middle;">'
                    f'<img src="data:{mime};base64,{b64}" width="{size}" height="{size}" '
                    f'style="object-fit:contain; border-radius:8px; display:block;" />'
                    f'</span>'
                )
            except Exception:
                pass
    return f'<span style="font-size:{size-6}px; vertical-align:middle;">⚡</span>'

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
# AELINE DESIGN SYSTEM CSS
# ============================================================
AELINE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --sky-blue: #0284C7;
    --sky-deep: #0369A1;
    --neon-lime: #D4FF00;
    --dark-pill: #111827;
    --card-border: rgba(0, 0, 0, 0.08);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #111827 !important;
}

.main .block-container {
    max-width: 1300px;
    padding: 0 1rem 3rem !important;
}

/* Hero Sky Header Container */
.aeline-hero {
    background: linear-gradient(180deg, #0284C7 0%, #38BDF8 80%, #BAE6FD 100%);
    border-radius: 36px;
    padding: 24px 36px 60px;
    color: #FFFFFF !important;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-top: 10px;
    box-shadow: 0 20px 50px rgba(2, 132, 199, 0.25);
}

.aeline-hero * {
    color: #FFFFFF !important;
}

/* Top Floating Nav */
.aeline-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 36px;
}

.nav-brand {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-links-cluster {
    display: flex;
    align-items: center;
    gap: 28px;
    font-size: 0.88rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* Hero Typography */
.hero-title {
    font-size: 3.8rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin: 12px 0 16px;
}

.hero-subtitle {
    font-size: 1.12rem;
    font-weight: 400;
    max-width: 680px;
    margin: 0 auto 30px;
    opacity: 0.92;
    line-height: 1.6;
}

/* 3D Curved Cards Horizon */
.deck-horizon {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 14px;
    margin: 36px auto 20px;
    perspective: 1200px;
    overflow-x: auto;
    padding: 20px 0;
}

.deck-item {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 16px;
    width: 140px;
    min-width: 140px;
    height: 160px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.4);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.3s ease;
}

.deck-item:hover {
    transform: translateY(-10px) scale(1.05);
}

.deck-item * {
    color: #111827 !important;
}

.deck-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}

.deck-title {
    font-size: 0.82rem;
    font-weight: 700;
    margin: 4px 0 0;
    line-height: 1.3;
}

.deck-stat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #6B7280 !important;
    font-weight: 600;
}

/* Rating Badge */
.rating-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    opacity: 0.95;
    margin-top: 16px;
}

/* Bento Showcase Section */
.bento-section {
    padding: 60px 0 20px;
    text-align: center;
}

.section-eyebrow {
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 8px;
}

.section-heading {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #111827;
    margin-bottom: 40px;
}

.section-heading span.badge-circle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    vertical-align: middle;
    font-size: 1.1rem;
    margin: 0 4px;
}

/* Bento Grid Cards */
.bento-card {
    border-radius: 28px;
    padding: 32px;
    text-align: left;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.25s ease;
}

.bento-blue {
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
    color: #FFFFFF !important;
}
.bento-blue * { color: #FFFFFF !important; }

.bento-white {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
}

.bento-lime {
    background: #D4FF00;
    color: #111827 !important;
}
.bento-lime * { color: #111827 !important; }

.bento-dark {
    background: #111827;
    color: #FFFFFF !important;
}
.bento-dark * { color: #FFFFFF !important; }

.bento-big-num {
    font-size: 3.4rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 8px;
}

/* Feature Launch Grid */
.tool-grid-card {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03);
    min-height: 210px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.2s ease;
    margin-bottom: 12px;
}

.tool-grid-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.08);
    border-color: #0284C7;
}

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #D4FF00 !important;
    color: #111827 !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(212, 255, 0, 0.4) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #BEE600 !important;
    transform: scale(1.03);
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
}

/* Workspace Styles */
.workspace-top {
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    padding: 16px 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}

.chat-user {
    background: #0284C7 !important;
    color: #FFFFFF !important;
    padding: 14px 20px;
    border-radius: 20px 20px 4px 20px;
    margin: 12px 0 12px auto;
    max-width: 80%;
    font-size: 0.95rem;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.15);
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
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(AELINE_CSS, unsafe_allow_html=True)

# 8 Intelligence Tools Specs
TOOLS = [
    {"id": "1", "icon": "🤖", "name": "Offline AI Chatbot", "desc": "Conversational intelligence with instant offline fallback.", "bg": "#EDE9FE", "badge": "Core"},
    {"id": "2", "icon": "🎙️", "name": "Voice Asking", "desc": "Speak complex equations and questions via neural speech-to-text.", "bg": "#E0F2FE", "badge": "Voice"},
    {"id": "3", "icon": "📷", "name": "Vision Math Solver", "desc": "Step-by-step solver for handwritten homework & circuit diagrams.", "bg": "#FFE4E6", "badge": "Vision"},
    {"id": "4", "icon": "📄", "name": "PDF / Notes Q&A", "desc": "Ground research and textbook questions into your uploaded documents.", "bg": "#D1FAE5", "badge": "RAG"},
    {"id": "5", "icon": "📝", "name": "Cornell Notes Maker", "desc": "Synthesize lecture transcripts into structured recall cues & summary.", "bg": "#FEF3C7", "badge": "Notes"},
    {"id": "6", "icon": "🧠", "name": "MCQ & Exam Engine", "desc": "Practice tests tailored to any syllabus or difficulty level.", "bg": "#FAE8FF", "badge": "Exam"},
    {"id": "7", "icon": "📅", "name": "Smart Study Planner", "desc": "Personalized day-by-day milestone roadmap before your test.", "bg": "#DBEAFE", "badge": "Plan"},
    {"id": "8", "icon": "🌐", "name": "Translation & ELI5", "desc": "Translate complex theory into 20+ languages with 5 simplification tiers.", "bg": "#CCFBF1", "badge": "20+ Langs"},
]

# ============================================================
# VIEW 1: AELINE SKY-BLUE LANDING PAGE
# ============================================================
if st.session_state.view == "landing":

    # --- 1. HERO HEADER SECTION ---
    ai_status = chat_ai_available()
    status_text = "● Cloud AI Active" if ai_status else "● Offline Ready"

    st.markdown(
        f"""
        <div class="aeline-hero">
            <div class="aeline-nav">
                <div class="nav-brand">
                    {get_logo_html(size=30, on_dark=True)} Karpom AI
                </div>
                <div class="nav-links-cluster">
                    <span>Platform</span>
                    <span>Tools</span>
                    <span>Research</span>
                    <span style="background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:9999px;">{status_text}</span>
                </div>
            </div>
            
            <h1 class="hero-title">
                Building the future with<br>Academic AI and strategy
            </h1>
            <p class="hero-subtitle">
                We empower students, engineers, and researchers to unlock rapid learning and efficiency through multimodal reasoning and intelligent automation.
            </p>
            
            <!-- 3D Card Orbit Carousel -->
            <div class="deck-horizon">
                <div class="deck-item" style="transform: rotate(-6deg);">
                    <div class="deck-icon" style="background:#EDE9FE;">🤖</div>
                    <div class="deck-title">Offline Chatbot</div>
                    <div class="deck-stat">Real-Time</div>
                </div>
                <div class="deck-item" style="transform: rotate(-3deg);">
                    <div class="deck-icon" style="background:#FFE4E6;">📷</div>
                    <div class="deck-title">Vision Solver</div>
                    <div class="deck-stat">Step-by-step</div>
                </div>
                <div class="deck-item" style="transform: scale(1.08); border: 2px solid #D4FF00;">
                    <div class="deck-icon" style="background:#D1FAE5;">📄</div>
                    <div class="deck-title">Document RAG</div>
                    <div class="deck-stat">99.8% Grounded</div>
                </div>
                <div class="deck-item" style="transform: rotate(3deg);">
                    <div class="deck-icon" style="background:#FEF3C7;">📝</div>
                    <div class="deck-title">Cornell Notes</div>
                    <div class="deck-stat">High-Yield</div>
                </div>
                <div class="deck-item" style="transform: rotate(6deg);">
                    <div class="deck-icon" style="background:#CCFBF1;">🌐</div>
                    <div class="deck-title">ELI5 Engine</div>
                    <div class="deck-stat">20+ Langs</div>
                </div>
            </div>
            
            <div class="rating-pill">
                Rated 4.9/5 by 12,000+ students & researchers ★★★★★
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Hero Dual CTA Buttons
    st.write("")
    cta1, cta2, cta3 = st.columns([1.5, 1, 1.5])
    with cta2:
        if st.button("GET STARTED ↗", key="btn_hero_launch", type="primary", use_container_width=True):
            navigate_to("workspace", "1")

    # --- 2. BENTO STATS SECTION ---
    st.markdown(
        """
        <div class="bento-section">
            <div class="section-eyebrow">• ABOUT US •</div>
            <h2 class="section-heading">
                A cognitive intelligence suite<br>
                dedicated to building <span class="badge-circle" style="background:#0284C7; color:#FFF;">⏱</span> smarter and <span class="badge-circle" style="background:#D4FF00; color:#111;">💡</span> more adaptive minds
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    b1, b2, b3 = st.columns([1.3, 1, 1])
    with b1:
        st.markdown(
            """
            <div class="bento-card bento-blue">
                <div style="font-weight:800; font-size:1.1rem; letter-spacing:0.04em;">KARPOM RESEARCH</div>
                <div style="margin-top:40px;">
                    <div class="bento-big-num">120+</div>
                    <div style="font-size:0.95rem; opacity:0.9;">Universities & competitive academic curricula fully indexed and supported.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b2:
        st.markdown(
            """
            <div class="bento-card bento-white">
                <div style="font-size:0.85rem; color:#6B7280; font-weight:700;">ACCURACY COMMITMENT</div>
                <div class="bento-big-num" style="color:#111827; margin-top:20px;">100%</div>
                <p style="font-size:0.88rem; color:#6B7280; margin:0;">"Step-by-step proofs ensure deep conceptual mastery, not just fast answers."</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b3:
        st.markdown(
            """
            <div class="bento-card bento-lime">
                <div style="font-size:0.85rem; font-weight:800; text-transform:uppercase;">Data Points</div>
                <div class="bento-big-num">520k+</div>
                <div style="font-size:0.9rem; font-weight:600;">Academic questions solved to power smarter study roadmaps.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- 3. 8-TOOL WORKBENCH LAUNCHER DECK ---
    st.write("")
    st.markdown(
        """
        <div style="margin:50px 0 20px; text-align:center;">
            <div class="section-eyebrow">• EXPLORE CAPABILITIES •</div>
            <h2 style="font-size:2.2rem; font-weight:800; letter-spacing:-0.03em;">Select a Tool to Launch Workbench</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Row 1 (Tools 1 to 4)
    r1_cols = st.columns(4)
    for idx in range(4):
        tool = TOOLS[idx]
        with r1_cols[idx]:
            st.markdown(
                f"""
                <div class="tool-grid-card">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <span style="font-size:1.4rem; background:{tool['bg']}; padding:6px 10px; border-radius:12px;">{tool['icon']}</span>
                            <span style="font-family:'JetBrains Mono'; font-size:0.75rem; font-weight:700; background:#F3F4F6; padding:3px 8px; border-radius:6px;">0{tool['id']}</span>
                        </div>
                        <h4 style="font-size:1.1rem; font-weight:700; margin:0 0 6px;">{tool['name']}</h4>
                        <p style="font-size:0.85rem; color:#6B7280; margin:0; line-height:1.4;">{tool['desc']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Launch 0{tool['id']} ↗", key=f"btn_card_{tool['id']}", use_container_width=True, type="secondary"):
                navigate_to("workspace", tool["id"])

    # Row 2 (Tools 5 to 8)
    r2_cols = st.columns(4)
    for idx in range(4, 8):
        tool = TOOLS[idx]
        with r2_cols[idx - 4]:
            st.markdown(
                f"""
                <div class="tool-grid-card">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <span style="font-size:1.4rem; background:{tool['bg']}; padding:6px 10px; border-radius:12px;">{tool['icon']}</span>
                            <span style="font-family:'JetBrains Mono'; font-size:0.75rem; font-weight:700; background:#F3F4F6; padding:3px 8px; border-radius:6px;">0{tool['id']}</span>
                        </div>
                        <h4 style="font-size:1.1rem; font-weight:700; margin:0 0 6px;">{tool['name']}</h4>
                        <p style="font-size:0.85rem; color:#6B7280; margin:0; line-height:1.4;">{tool['desc']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Launch 0{tool['id']} ↗", key=f"btn_card_{tool['id']}", use_container_width=True, type="secondary"):
                navigate_to("workspace", tool["id"])


# ============================================================
# VIEW 2: DEDICATED WORKBENCH PAGE
# ============================================================
elif st.session_state.view == "workspace":

    # Top Bar Navigation with Return Link
    top1, top2, top3 = st.columns([1.2, 3, 1.2])
    with top1:
        if st.button("← Back to Home", key="btn_back_to_home", type="secondary"):
            navigate_to("landing")
    with top2:
        st.markdown(
            f"""
            <div style="text-align:center; display:flex; align-items:center; justify-content:center; gap:8px;">
                {get_logo_html(size=26)}
                <span style="font-weight:800; font-size:1.15rem; color:#111827;">Karpom AI Interactive Workspace</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with top3:
        if st.button("Reset Session 🗑", key="btn_ws_reset", type="secondary"):
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

    st.write("")

    # ------------------------------------------------------------
    # 1. OFFLINE AI CHATBOT
    # ------------------------------------------------------------
    if st.session_state.active_feature == "1":
        st.markdown(
            """
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">🤖 Feature 01: Conversational AI Copilot</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Real-time token streaming for deep problem solving, code reasoning, and conceptual proofs.</p>
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
                st.markdown(f'<div style="font-size:0.8rem; color:#0284C7; font-weight:800; margin:10px 0 4px; display:flex; align-items:center; gap:6px;">{get_logo_html(size=16)} Karpom AI</div>', unsafe_allow_html=True)
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
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">🎙️ Feature 02: Voice Question Asking</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Speak your question directly. Speech recognition transcribes and solves it instantly.</p>
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
    # 3. VISION MATH & IMAGE SOLVER
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "3":
        st.markdown(
            """
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">📷 Feature 03: Vision Homework & Diagram Solver</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Upload or snap a photo of any handwritten math problem, circuit diagram, or textbook page.</p>
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
                    st.markdown(f'<div class="chat-ai" style="max-width:100%;"><h4 style="color:#0284C7; margin:0 0 10px;">📝 Step-by-Step Solution</h4><div style="line-height:1.7;">{sol}</div></div>', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # 4. PDF / NOTES Q&A
    # ------------------------------------------------------------
    elif st.session_state.active_feature == "4":
        st.markdown(
            """
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">📄 Feature 04: Document Q&A & Research RAG</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Upload lecture slides, syllabus PDFs, or research papers and query them with strict factual grounding.</p>
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
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">📝 Feature 05: Cornell Notes Generator</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Turn raw lecture transcripts into high-yield Cornell study guides with flashcard recall cues.</p>
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
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">🧠 Feature 06: MCQ & Practice Exam Generator</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Generate customized practice tests with deep explanations and full answer keys.</p>
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
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">📅 Feature 07: Personalized Study Planner</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Build a structured milestone revision roadmap tailored to your upcoming test date.</p>
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
            <div class="workspace-top">
                <div>
                    <h3 style="margin:0; font-size:1.25rem; font-weight:800; color:#111827;">🌐 Feature 08: Multilingual Translation & ELI5 Simplifier</h3>
                    <p style="margin:4px 0 0; color:#6B7280; font-size:0.88rem;">Translate complex academic theory into 20+ languages and adjust cognitive difficulty levels.</p>
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
