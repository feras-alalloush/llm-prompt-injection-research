# Evaluating Layered Defenses Against Direct Prompt Injection in LLM-Based Web Applications

Research codebase for measuring **Attack Success Rate (ASR)** and **Response Latency** of an LLM-backed e-commerce support chatbot, with and without layered prompt-injection defenses.

## Baseline Application (Person 1)

The baseline Streamlit app is the **unprotected** control condition. User messages are forwarded to Groq `openai/gpt-oss-20b` (free tier) with only the ShopEase system prompt—no input sanitization, output filtering, or other defenses.

## Project Structure

```
llm-prompt-injection-research/
├── app/
│   ├── __init__.py
│   ├── baseline_app.py      # Baseline UI (ENABLE_DEFENSES = False)
│   ├── protected_app.py     # Same UI + defenses ON (Person 3 hook)
│   └── turn_handler.py      # Shared chat-turn pipeline
├── defense/                 # Person 3 implements these
│   ├── pattern_guard.py     # Tier 1 — Input Pattern Guard
│   ├── prompt_isolation.py  # Tier 2 — Prompt Isolation
│   ├── defense_pipeline.py  # Orchestration entry point
│   └── README.md            # Integration guide for Person 3
├── config/
│   └── system_prompt.py
├── utils/
│   └── logger.py
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## What Person 1 should upload (for the team)

Upload / push these:
- `app/`, `config/`, `defense/`, `utils/`, `logs/.gitkeep`
- `requirements.txt`, `.env.example`, `.gitignore`, `README.md`
- `تعليمات_التشغيل.md` (Arabic setup guide for teammates)

Do **not** upload:
- `.env` (API key)
- `.venv/`
- `__pycache__/`
- `logs/*.csv` (optional local data)

Teammates follow **`تعليمات_التشغيل.md`**: create a Groq key, install requirements, run the app.

## Prerequisites

- Python 3.12+
- A free Groq API key: https://console.groq.com/keys

## Setup

```bash
cd llm-prompt-injection-research
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env`:

```
GROQ_API_KEY=gsk_...
```

## Run

From `llm-prompt-injection-research/`:

```bash
# Person 1 — Baseline (no defenses)
streamlit run app/baseline_app.py

# Person 3 — Protected (calls defense pipeline)
streamlit run app/protected_app.py
```

## Defense integration (Person 3)

Protected mode calls only:

```python
defense.defense_pipeline.run_defense_pipeline(user_input, system_prompt)
```

Implement rules inside:

1. `defense/pattern_guard.py` — block suspicious input (no LLM call)
2. `defense/prompt_isolation.py` — wrap user content + harden system prompt

See `defense/README.md` for contracts and expected return types.

## Logging & Metrics

| Column | Description |
|--------|-------------|
| `timestamp` | UTC ISO-8601 |
| `session_id` | Per-browser session UUID |
| `user_input` | Raw user message |
| `model_response` | Assistant reply or block message |
| `latency_ms` | Model call latency (`time.perf_counter`) |
| `app_version` | `baseline` or `protected` |
| `blocked` | `true` if Tier 1 blocked the request |
| `block_reason` | Why it was blocked |
| `defense_stages` | Stages applied (protected only) |

- Baseline → `logs/baseline_interactions.csv`
- Protected → `logs/protected_interactions.csv`
