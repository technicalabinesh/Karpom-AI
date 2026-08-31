"""
Text extraction and local statistical utility helpers.
"""

from pypdf import PdfReader
from docx import Document

def extract_text(uploaded_file) -> str:
    """Extracts raw text from PDF, DOCX, TXT, or MD files."""
    if uploaded_file is None:
        return ""
    
    filename = uploaded_file.name.lower()
    content = ""
    
    try:
        if filename.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
        elif filename.endswith(".docx"):
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                if para.text:
                    content += para.text + "\n"
        elif filename.endswith((".txt", ".md")):
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Extraction error: {e}")
        
    return content.strip()

def word_count(text: str) -> int:
    """Returns total word count."""
    return len(text.split()) if text else 0

def extractive_summary(text: str, num_sentences: int = 5) -> str:
    """Offline sentence extraction fallback."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 20]
    return ". ".join(sentences[:num_sentences]) + ("." if sentences else "")

def key_points(text: str, num_points: int = 5) -> list:
    """Offline bullet point extraction fallback."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 30]
    return sentences[:num_points] if sentences else ["No distinct key points extracted."]