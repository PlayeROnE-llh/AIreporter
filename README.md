# AIreporter
# StarCraft II AI Report Generator
Generate professional-grade, audience-specific battle reports from StarCraft II replays in seconds.  
Simply drag-and-drop a `.SC2Replay`, pick a large language model and a knowledge base, and receive an in-depth analysis tailored for pro players, coaches, casters, casual gamers, or spectators.

---
https://github.com/user-attachments/assets/fa362f6f-b922-4097-83f1-5466e67690cd
## 1.What It Does

| Stakeholder | Example Output |
|-------------|----------------|
| **Pro Player** | “Your 2-base timing is 14 s late. Spending 50 % of the drop investment on +1 attack would yield +23 % DPS by 14:00 and avoid Viking exposure to Photon Cannons.” |
| **Coach** | “Opponent skipped early detection. Drill DT drop at 6:30 (drill-ID #B-14) to exploit the gap.” |
| **Caster** | “A nail-biter! The 12:30 doom-drop mirrors 2023 WCS finals Game 4—perfect clip for the highlight reel.” |
| **Casual** | “You floated 1 200 minerals. Queue more Gateways next time .” |
| **Spectator** | “Auto-marked highlights at 7:45, 11:02, 13:37—ready for social media.” |

---

---

## 2.Key Features

- **Multi-Role Reports** – Same replay, five different voices.  
- **RAG-Enhanced LLM** – 5 000+ SC2 entities, builds, and tactics injected at inference time via `all-MiniLM-L6-v2` embeddings.  
- **Millisecond-Level Parsing** – Uses `sc2reader` to extract 100 % of events; converts to cleaned JSON in <2 s.  
- **One-Click GUI** – Drag-and-drop, model & knowledge-base selectors, live progress bar.  
- **Rich Export** – Sectioned or full reports in Markdown or HTML, ready for copy-paste.

---
## 3.Technology Overview

The app consists of six main parts:
- **AIReporter.py** : A fully integrated scripting program that can perform a complete report generation process by simply adjusting APIs, models, and visual front-ends in the corresponding functions.
- **data.py** : Use sc2reader to '. SC2Replay' file for maximum possible data extraction and data processing that is easy to integrate into the prompt.
- **prompt.py** : Different prompt templates for different scenarios and audiences, used to ask questions to the LLM after integrating data.
- **api.py** : For the rendering of the invocation LLMapi flow.
- **llm.py** : Integrate the data file .json, select relevant KB.json and prompt content from RAG to form a complete question and interact with the LLM.
---
### 3.1.Data Cleaning Pipeline
| Step               | Rule                                         | Rationale              |
| ------------------ | -------------------------------------------- | ---------------------- |
| **Deduplication**  | Merge consecutive identical commands         | Removes spam clicks    |
| **Anomaly Fix**    | Forward-fill missing unit death events       | Replay gaps            |
| **Time Alignment** | Convert frame → seconds (`frame / game_fps`) | Uniform timeline       |
| **Windowing**      | 15 s fixed + 5-30 s dynamic sliding window   | Balance detail vs size |
```json
{
  "timestamp": 180,
  "player": "Maru",
  "race": "Terran",
  "minerals": 425,
  "gas": 150,
  "supply": "44/54",
  "workers": 32,
  "army_count": 12,
  "building_count": 18,
  "upgrades": ["Stimpack", "Combat Shield"],
  "camera_pos": [64.3, 87.1],
  "ngram_ops": ["select_cc", "train_scv", "select_barracks", "train_marine"]
}
```
Final JSON is an array of per-second snapshots ready for LLM prompts:
```json
[
  {"time": 0,  "Maru": {"minerals": 50, "gas": 0}},
  {"time": 15, "Maru": {"minerals": 125, "gas": 0}},
]
```
### 3.2.Extending the Knowledge Base
Knowledge files are JSON arrays:

```json
[
  {
    "name": "Marine",
    "race": "Terran",
    "hp": 45,
    "armor": "0/1/2/3",
    "speed": 2.25,
    "attributes": ["Light", "Biological"],
    "weapon": {"name": "C-14 Rifle", "damage": 6},
    "abilities": ["Stimpack", "Combat Shield"],
    "tactics": ["Bio Push", "Medivac Drop"]
  }
]
```
### 3.3.Prompt Stack Overview
| Audience | Tone | Depth | Key Metrics |
|---|---|---|---|
| **Pro Player** | Technical, terse | Deep | Timing drift, upgrade ROI, micro mistakes |
| **Coach** | Directive, tactical | Very deep | Drill IDs, build deviation %, scouting gaps |
| **Caster** | Dramatic, narrative | Medium | Turning points, highlight timestamps |
| **Casual** | Friendly, explanatory | Shallow | Floating resources, “what to build next” |
| **Spectator** | Curated, emoji | Visual | Auto-clipped GIF times, meme moments |
```text
You are an elite SC2 coach. Use only Battle.net terminology.
- Output in markdown with ## headers
- End every section with ✅ or ❌
- Quantify every claim
```

---
## 4.Quick Start
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
```
