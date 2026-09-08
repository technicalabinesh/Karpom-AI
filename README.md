# Karpom AI

Karpom AI is a professional, multimodal academic assistant built with Streamlit and Azure OpenAI.  
It combines conversational tutoring, vision-based problem solving, document intelligence, quiz generation, and study planning into one focused learning workspace.

---

## Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Feature Walkthrough](#feature-walkthrough)
- [Architecture Notes](#architecture-notes)
- [Operational Notes](#operational-notes)
- [Troubleshooting](#troubleshooting)
- [Security and Responsible Use](#security-and-responsible-use)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Karpom AI is designed as a complete AI learning workbench for students, educators, and self-learners.  
Instead of providing only a chatbot, the application offers multiple specialized tools in a single interface:

- Real-time AI chat for general academic support
- Voice-to-text question capture
- Image-based academic analysis and solution generation
- Document-grounded Q&A for uploaded notes
- Cornell-style notes generation
- MCQ quiz generation with explanations
- Personalized study plan creation
- Translation and simplification for multilingual learning

The app supports two execution modes:

1. **Cloud AI mode** using Azure OpenAI credentials.
2. **Offline fallback mode** for selected features when AI credentials are unavailable.

This keeps the platform usable during setup, local testing, or temporary cloud unavailability.

---

## Core Features

### 1) AI Chat Workspace

- Streaming responses for interactive tutoring
- Conversation state management in Streamlit session state
- Optional persistent chat history through Supabase
- Structured assistant behavior configured by system prompt

### 2) Voice Q&A

- Accepts microphone input from the browser
- Converts speech to text (with local transcription fallback behavior)
- Routes transcribed queries into the AI workflow

### 3) Vision Solver

- Accepts uploaded images or camera captures
- Sends visual input plus prompt context to multimodal model endpoints
- Produces structured educational explanations for:
  - textbook pages
  - handwritten notes
  - diagrams and circuits
  - problem statements

### 4) Document Q&A

- Upload PDF, DOCX, TXT, or Markdown files
- Extract text content
- Ask focused questions grounded in uploaded material
- Includes a local matching fallback if cloud AI is not configured

### 5) Cornell Notes Generator

- Converts raw study content into structured Cornell-style notes
- Creates key concepts, expanded notes, recall cues, and concise summaries
- Useful for revision workflows and memory reinforcement

### 6) Quiz Generator

- Creates multiple-choice question sets from topic input
- Supports adjustable difficulty and question count
- Returns answer keys and explanations for practice loops

### 7) Study Planner

- Generates day-by-day preparation strategy
- Uses target goal, days remaining, and daily study hours
- Produces milestone-driven roadmaps for exam preparation

### 8) Translator & Simplifier

- Translates academic text into selected target language
- Adjusts complexity to a chosen learner level
- Helps bridge comprehension gaps across language and skill boundaries

---

## How It Works

Karpom AI is composed of modular Python components:

- `app.py` handles UI layout, routing, visual system, and feature screens.
- `chatbot.py` manages Azure OpenAI connectivity and token streaming.
- `study_tools.py` contains specialized feature logic (voice, vision, Q&A, planning, translation).
- `summarizer.py` provides structured summary workflows.
- `utils.py` provides file text extraction and local utility helpers.

At runtime:

1. The Streamlit interface loads and initializes session state.
2. Environment variables determine whether cloud AI mode is enabled.
3. User interactions are routed to feature-specific handlers.
4. Responses are rendered in a styled workspace with optional persistence.

---

## Tech Stack

- **Frontend/UI:** Streamlit
- **AI API Client:** OpenAI Python SDK (Azure OpenAI usage)
- **Data Persistence (optional):** Supabase
- **Document Parsing:** `pypdf`, `python-docx`
- **Environment Management:** `python-dotenv`
- **Image Handling:** Pillow

Optional audio dependencies may be required for enhanced local transcription workflows:

- `SpeechRecognition`
- `pydub`

---

## Project Structure

```text
Karpom-AI/
├── app.py             # Main Streamlit application and UI routing
├── chatbot.py         # Azure OpenAI client + token streaming logic
├── study_tools.py     # Voice, vision, doc Q&A, notes, quiz, planner, translation
├── summarizer.py      # AI + fallback summarization helper
├── utils.py           # File text extraction and local utility functions
├── requirements.txt   # Python dependencies
├── logo.png           # Brand asset used as favicon and UI logo
└── LICENSE            # Apache-2.0 license
```

---

## Getting Started

### Prerequisites

- Python 3.10+ recommended
- `pip` package manager
- Azure OpenAI resource (for cloud AI mode)
- (Optional) Supabase project for chat history persistence

### Installation

```bash
git clone https://github.com/technicalabinesh/Karpom-AI.git
cd Karpom-AI
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the repository root and set the required values.

### Required for AI Mode

| Variable | Description |
|---|---|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint base URL |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment/model name |
| `AZURE_OPENAI_API_VERSION` | API version (defaults in code if omitted) |

### Optional for Chat Persistence

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase API/service key used by this app |

> If Azure variables are missing, the app will operate with offline fallbacks where supported.

---

## Running the Application

```bash
streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

---

## Feature Walkthrough

### Landing Page

The default landing view exposes all tools as launchable feature cards.  
This provides clear navigation and separates discovery from active workflows.

### Workspace View

Once a feature is selected, users enter a focused workspace with:

- top navigation controls
- feature-specific input areas
- rendered responses in consistent UI containers

### Chat Persistence Behavior

- With Supabase configured, each chat message is written to `chat_history`.
- Without Supabase, the app still functions using in-memory session state.

### Offline Handling Strategy

When AI credentials are absent:

- conversational and advanced AI operations report clear status messages
- document features may use keyword/sentence extraction fallback logic
- users can still validate UI and interaction flow during setup

---

## Architecture Notes

Karpom AI is intentionally implemented as a lightweight monolith for rapid iteration:

- **Single process runtime:** Streamlit app process
- **Modular feature organization:** functionality split by domain module
- **Environment-gated cloud integrations:** secure defaults when keys are absent
- **Graceful degradation:** limited but useful fallback behavior

This architecture prioritizes developer speed, educational utility, and deployment simplicity.

---

## Operational Notes

### Performance

- Streaming responses improve perceived responsiveness in chat mode.
- Document content is sliced before model submission to avoid oversized payloads.

### Data Handling

- Uploaded files are processed in-session.
- Persisted chat history depends on external Supabase configuration.

### Model Control

- Deployment name is read from environment variables.
- Token budgets are explicitly set for key completion tasks.

---

## Troubleshooting

### 1) “Azure API credentials missing”

Cause: Missing or invalid Azure environment variables.  
Fix: Verify `.env` entries and restart Streamlit.

### 2) Vision or generation request fails

Cause: Incorrect deployment name, endpoint format, or unsupported model configuration.  
Fix: Recheck deployment settings in Azure and confirm API version compatibility.

### 3) Supabase history not loading

Cause: Missing keys, network issue, or table mismatch.  
Fix: Validate `SUPABASE_URL`, `SUPABASE_KEY`, and table schema.

### 4) Audio transcription quality is poor

Cause: Low input quality or unsupported audio environment.  
Fix: Record in a quieter space and ensure optional speech dependencies are installed.

---

## Security and Responsible Use

- Never commit `.env` files or credentials to source control.
- Restrict API keys by environment and rotate them regularly.
- Validate usage costs and quotas for production deployments.
- Review generated academic content before submission or high-stakes use.
- Ensure compliance with institutional AI-use policies.

---

## Roadmap

Potential next improvements:

- richer retrieval pipelines for document Q&A
- source citation spans in generated answers
- analytics dashboard for learner progress
- multi-user auth and profile-level personalization
- export formats for notes, quizzes, and study plans

---

## Contributing

Contributions are welcome.

Suggested workflow:

1. Fork the repository
2. Create a feature branch
3. Make focused, testable changes
4. Submit a pull request with clear context

For larger changes, open an issue first to align scope and design direction.

---

## License

This project is licensed under the **Apache License 2.0**.  
See `/LICENSE` for full terms.
