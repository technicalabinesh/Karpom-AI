"""
Karpom AI - Universal Multimodal Academic & Vision Intelligence Tools
"""

import os
import io
import base64
from chatbot import get_client, is_ai_mode_available

# ============================================================
# GPT-5.4 UNIVERSAL COMPLETION HELPER
# ============================================================
def gpt5_completion(messages: list, max_tokens: int = 3000):
    """Executes completions with GPT-5.4 using strict max_completion_tokens."""
    client = get_client()
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4").strip()
    return client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_completion_tokens=max_tokens,
    )

# ============================================================
# 2. VOICE QUESTION ASKING (FREE SPEECH RECOGNITION)
# ============================================================
def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribes audio using free local SpeechRecognition."""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes)
        
        with sr.AudioFile(audio_file) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
            
    except Exception:
        try:
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_io) as source:
                audio_data = recognizer.record(source)
                return recognizer.recognize_google(audio_data)
        except Exception:
            return "⚠️ Speech recognition note: Speak closer to mic or install SpeechRecognition (`pip install SpeechRecognition pydub`)."

# ============================================================
# 3. UNIVERSAL VISION AI (SOLVES & EXPLAINS WHATEVER IS UPLOADED)
# ============================================================
def solve_image_question(image_bytes: bytes, user_prompt: str = "") -> str:
    """
    Universal Vision Solver: Accurately analyzes, explains, and solves WHATEVER is in the image.
    Works for book covers, textbook pages, math derivations, circuit schematics, or handwritten notes.
    """
    if not is_ai_mode_available():
        return "⚠️ Vision AI requires an active Azure OpenAI deployment in `.env`."

    try:
        b64_img = base64.b64encode(image_bytes).decode("utf-8")

        # UNIVERSAL ADAPTIVE PEDAGOGICAL PROMPT
        default_prompt = """
You are an expert academic tutor and visual intelligence solver.
Analyze WHATEVER is in this image thoroughly and provide rich, high-yield educational value.

ADAPT AUTOMATICALLY BASED ON WHAT YOU SEE:
1. 📖 IF IT IS A BOOK COVER, TEXTBOOK, OR SUBJECT TITLE (e.g. 'Linear Integrated Circuits'):
   - Identify the title, author, and subject domain immediately.
   - Deliver a high-level masterclass breakdown of this subject (e.g., Core Op-Amp configurations, 555 Timers, Active Filters, Voltage Regulators, DAC/ADC).
   - List the top 5 most critical engineering/academic concepts and essential formulas students must know for exams in this subject.

2. 🧮 IF IT IS A MATH, PHYSICS, OR CHEMISTRY PROBLEM:
   - Transcribe the exact question statement.
   - Provide a complete, rigorous, step-by-step mathematical derivation.
   - Highlight the final numerical or algebraic answer in bold.

3. ⚡ IF IT IS A CIRCUIT, DIAGRAM, OR FLOWCHART:
   - Identify every component and connection.
   - Explain the operational mechanism, input/output characteristics, and working principles.

4. 📝 IF IT IS HANDWRITTEN NOTES OR A DOCUMENT PAGE:
   - Transcribe all visible text accurately.
   - Clean up and structure the concepts into clear, polished study notes with added insights.

STRUCTURE YOUR OUTPUT CLEARLY WITH:
- 📌 **What is in this Image**
- 🧠 **Detailed Academic Breakdown & Explanation**
- 💡 **Key Formulas, Concepts & Exam Takeaways**
""".strip()

        final_prompt = user_prompt.strip() if user_prompt.strip() else default_prompt

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": final_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                    },
                ],
            }
        ]

        res = gpt5_completion(messages, max_tokens=3000)
        return res.choices[0].message.content or "No response generated."
        
    except Exception as exc:
        return f"⚠️ **Vision AI Error:** `{exc}`"

# ============================================================
# 4. PDF / NOTES Q&A (RAG)
# ============================================================
def ask_document(doc_text: str, question: str) -> str:
    """Answers questions grounded in the uploaded document via GPT-5.4."""
    if not is_ai_mode_available():
        sentences = [s.strip() for s in doc_text.split(".") if any(w in s.lower() for w in question.lower().split())]
        return " ".join(sentences[:3]) if sentences else "No direct matching snippet found offline."

    prompt = f"""
You are an academic document tutor. Answer the student's question based strictly on the document below.
If the information is not present, state that clearly.

DOCUMENT CONTENT:
{doc_text[:40000]}

STUDENT QUESTION:
{question}
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        res = gpt5_completion(messages, max_tokens=1500)
        return res.choices[0].message.content or ""
    except Exception as exc:
        return f"⚠️ **Error:** `{exc}`"

# ============================================================
# 5. AI CORNELL NOTES GENERATOR
# ============================================================
def generate_cornell_notes(source_text: str) -> str:
    """Transforms raw text into structured Cornell Notes via GPT-5.4."""
    if not is_ai_mode_available():
        return "### Cornell Notes (Offline Summary)\n- " + source_text[:500]

    prompt = f"""
Convert the following lecture/study text into structured, high-yield Cornell Notes.

Format strictly as:
## 📌 Core Concepts & Vocabulary
- Key term 1: definition
- Key term 2: definition

## 📝 Detailed Study Notes
(Use structured bullet points, bold key principles, formulas, and theories)

## 💡 Quick Recall Cues (Flashcard Q&A)
- Q1: ... ? -> A1: ...
- Q2: ... ? -> A2: ...

## 🎯 Executive Summary
(2-3 sentence wrap-up)

TEXT:
{source_text[:35000]}
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        res = gpt5_completion(messages, max_tokens=2500)
        return res.choices[0].message.content or ""
    except Exception as exc:
        return f"⚠️ **Error generating notes:** `{exc}`"

# ============================================================
# 6. MCQ & QUIZ GENERATOR
# ============================================================
def generate_quiz(text_or_topic: str, num_questions: int = 5, difficulty: str = "Medium") -> str:
    """Generates multiple-choice practice exams with answer keys via GPT-5.4."""
    if not is_ai_mode_available():
        return "Offline Quiz Generation: Please configure Azure OpenAI in `.env`."

    prompt = f"""
Create a high-quality {difficulty}-level practice quiz with {num_questions} Multiple Choice Questions (MCQs) based on the topic/text below.

Format each question clearly:
### Question X: [Question text]
- A) Option 1
- B) Option 2
- C) Option 3
- D) Option 4

**Correct Answer:** [Letter]
**Explanation:** [Brief reason why]
---

TOPIC / CONTENT:
{text_or_topic[:30000]}
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        res = gpt5_completion(messages, max_tokens=3000)
        return res.choices[0].message.content or ""
    except Exception as exc:
        return f"⚠️ **Error generating quiz:** `{exc}`"

# ============================================================
# 7. PERSONALIZED STUDY PLANNER
# ============================================================
def generate_study_plan(subjects: str, days_left: int, hours_per_day: float, target_goal: str) -> str:
    """Creates a milestone study roadmap tailored to exams via GPT-5.4."""
    if not is_ai_mode_available():
        return f"### {days_left}-Day Study Plan\n- Dedicate {hours_per_day} hrs/day rotating through {subjects}."

    prompt = f"""
You are an elite academic coach. Build a personalized {days_left}-day study schedule.
Parameters:
- Target Goal: {target_goal}
- Subjects/Topics: {subjects}
- Daily Available Study Time: {hours_per_day} hours/day

Structure the output as:
1. 🎯 Strategy & Focus Allocation
2. 📅 Phase-by-Phase Roadmap (Day 1 to Day {days_left}) with daily targets
3. ⚡ Active Recall & Practice Milestones
4. 🧠 Exam-Day Readiness Checklist
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        res = gpt5_completion(messages, max_tokens=2500)
        return res.choices[0].message.content or ""
    except Exception as exc:
        return f"⚠️ **Error generating plan:** `{exc}`"

# ============================================================
# 8. MULTILINGUAL TRANSLATION & SIMPLIFICATION
# ============================================================
def translate_and_simplify(text: str, target_lang: str, simplification_level: str) -> str:
    """Translates content and simplifies complexity via GPT-5.4."""
    if not is_ai_mode_available():
        return f"Offline: Cannot translate to {target_lang} without cloud AI."

    prompt = f"""
Translate and adapt the following academic content.
- Target Language: {target_lang}
- Simplification Level: {simplification_level} (e.g. 'Explain Like I'm 5', 'High School Student', 'Academic Graduate')

Provide:
1. 🌐 Translated & Adapted Explanation
2. 💡 Key Takeaway in 1 Sentence
3. 📖 Core Vocabulary glossary (Original Term -> Translated Term)

TEXT:
{text[:25000]}
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        res = gpt5_completion(messages, max_tokens=2048)
        return res.choices[0].message.content or ""
    except Exception as exc:
        return f"⚠️ **Error in translation:** `{exc}`"