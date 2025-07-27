# AIreporter
# StarCraft II AI Battle Report Generator

Generate professional-grade, audience-specific battle reports from StarCraft II replays in seconds.  
Simply drag-and-drop a `.SC2Replay`, pick a large language model and a knowledge base, and receive an in-depth analysis tailored for pro players, coaches, casters, casual gamers, or spectators.

---

## What It Does

| Stakeholder | Example Output |
|-------------|----------------|
| **Pro Player** | “Your 2-base timing is 14 s late. Spending 50 % of the drop investment on +1 attack would yield +23 % DPS by 14:00 and avoid Viking exposure to Photon Cannons.” |
| **Coach** | “Opponent skipped early detection. Drill DT drop at 6:30 (drill-ID #B-14) to exploit the gap.” |
| **Caster** | “A nail-biter! The 12:30 doom-drop mirrors 2023 WCS finals Game 4—perfect clip for the highlight reel.” |
| **Casual** | “You floated 1 200 minerals. Queue more Gateways next time 😊.” |
| **Spectator** | “Auto-marked highlights at 7:45, 11:02, 13:37—ready for social media.” |

---

---

## Key Features

- **Multi-Role Reports** – Same replay, five different voices.  
- **RAG-Enhanced LLM** – 5 000+ SC2 entities, builds, and tactics injected at inference time via `all-MiniLM-L6-v2` embeddings.  
- **Millisecond-Level Parsing** – Uses `sc2reader` to extract 100 % of events; converts to cleaned JSON in <2 s.  
- **One-Click GUI** – Drag-and-drop, model & knowledge-base selectors, live progress bar.  
- **Rich Export** – Sectioned or full reports in Markdown or HTML, ready for copy-paste.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-org/sc2-ai-reporter.git
cd sc2-ai-reporter

# 2. Install
pip install -r requirements.txt

# 3. (Optional) Cache BERT model locally
python - <<'PY'
from sentence_transformers import SentenceTransformer
SentenceTransformer('all-MiniLM-L6-v2').save('models/all-MiniLM-L6-v2')
PY

# 4. Run
python AIReporter.py


---
┌──────────────────────────────────────────────────────────────┐
│                    UI Layer (TkinterDnD)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐  │
│  │ File Drop   │  │ Model Picker│  │ Knowledge Selector │  │
│  └─────────────┘  └─────────────┘  └────────────────────┘  │
└────────────────────────┬───────────────────────────────────┘
│
┌────────────────────────┴───────────────────────────────────┐
│                    Controller Threading                      │
│  - Async replay parsing  - Status callbacks  - Error dialogs │
└────────────────────────┬───────────────────────────────────┘
│
┌────────────────────────┴───────────────────────────────────┐
│                    Data Pipeline                             │
│  1. sc2reader → raw events                                 │
│  2. Clean → 15 s fixed / 5-30 s sliding window             │
│  3. N-gram operation patterns (n=2-7)                      │
│  4. JSON snapshots (temp_data.json)                        │
└────────────────────────┬───────────────────────────────────┘
│
┌────────────────────────┴───────────────────────────────────┐
│                  LLM + RAG Layer                             │
│  - BERT embeddings (all-MiniLM-L6-v2)                    │
│  - Cosine-sim retrieval (top-k=5)                          │
│  - Prompt templates (prompts/*.txt)                      │
│  - OpenAI-compatible endpoints (SiliconFlow, local GGML)   │
└────────────────────────┬───────────────────────────────────┘
│
┌────────────────────────┴───────────────────────────────────┐
│                    Report Renderer                           │
│  - Sectioned or full markdown/HTML                         │
│  - Auto-TOC, syntax-highlighted code blocks, emoji icons   │
└──────────────────────────────────────────────────────────────┘
