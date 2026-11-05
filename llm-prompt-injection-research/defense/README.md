# Defense Integration Guide (Person 3)

The Protected app already calls this package. You only fill in the Tier 1 / Tier 2 logic.

## Pipeline (already wired)

```
User message
   → defense.defense_pipeline.run_defense_pipeline()
        → Tier 1: pattern_guard.check_input()
             └─ if blocked → return (no LLM call)
        → Tier 2: prompt_isolation.isolate_user_content()
   → LLM (Groq / OpenAI-compatible)
   → log to logs/protected_interactions.csv
```

## Files to implement

| File | Responsibility |
|------|----------------|
| `pattern_guard.py` | Regex / heuristics. Return `allowed=False` to block. |
| `prompt_isolation.py` | Wrap user text (e.g. XML) + harden system prompt. |
| `defense_pipeline.py` | Keep as the single public entry (`run_defense_pipeline`). |

## Contracts (do not break)

### `check_input(user_input) -> PatternGuardResult`
- `allowed=False` → Protected app shows a block message and **must not** call the API.
- Set `reason` / `matched_rule` for logging.

### `isolate_user_content(user_input, system_prompt) -> IsolationResult`
- Return final `system_prompt` and `isolated_user_input` sent to the model.

### `run_defense_pipeline(user_input, system_prompt) -> DefenseResult`
- Public API used by `app/turn_handler.py`.
- Keep the function name and `DefenseResult` fields stable for Person 4’s test runner.

## How to run the Protected app

From `llm-prompt-injection-research/`:

```bash
streamlit run app/protected_app.py
```

Baseline (no defenses):

```bash
streamlit run app/baseline_app.py
```

## Current stub behavior

Stubs **allow all traffic** and pass user text unchanged, so the Protected app runs end-to-end before your rules are ready. Replace the `TODO` sections when implementing defenses.
