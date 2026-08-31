"""
LexieLingua - Document Summarizer module with AI synthesis.
"""

import os
import re
from utils import extractive_summary, key_points, word_count
from chatbot import get_client, is_ai_mode_available

def summarize(text: str, length: str = "Medium") -> dict:
    """Generates structured summaries using GPT-5.4."""
    if not text or not text.strip():
        return {"summary": "No readable text provided.", "key_points": [], "mode": "None", "original_words": 0, "summary_words": 0}

    if not is_ai_mode_available():
        summary = extractive_summary(text, num_sentences=6)
        return {"summary": summary, "key_points": key_points(text, 5), "mode": "Offline", "original_words": word_count(text), "summary_words": word_count(summary)}

    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4").strip()
    client = get_client()

    prompt = f"""
Summarize the provided document clearly.
Respond strictly using this format:
SUMMARY:
<executive summary text>

KEY POINTS:
- Point 1
- Point 2
- Point 3
- Point 4
- Point 5

DOCUMENT:
{text[:50000]}
"""
    try:
        res = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4096,
        )
        raw = res.choices[0].message.content or ""
        summary_text = raw
        points = []

        kp_match = re.search(r"(?i)\*{0,2}KEY (?:POINTS|TAKEAWAYS)\*{0,2}:?", raw)
        if kp_match:
            summary_part = raw[:kp_match.start()]
            points_part = raw[kp_match.end():]
            summary_text = re.sub(r"(?i)^\s*\*{0,2}SUMMARY\*{0,2}:?\s*", "", summary_part).strip()
            for line in points_part.splitlines():
                clean_pt = re.sub(r"^[-•*–\d+\.]\s*", "", line.strip()).strip()
                if clean_pt:
                    points.append(clean_pt)

        return {
            "summary": summary_text.strip(),
            "key_points": points[:5],
            "mode": f"Azure AI ({deployment})",
            "original_words": word_count(text),
            "summary_words": word_count(summary_text),
        }
    except Exception as exc:
        return {"summary": f"Error: {exc}", "key_points": [], "mode": "Error", "original_words": 0, "summary_words": 0}