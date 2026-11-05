"""
Protected ShopEase app — same UI as Baseline, defenses enabled.

Person 3 implements the real logic in:
  defense/pattern_guard.py
  defense/prompt_isolation.py
  defense/defense_pipeline.py

This file only flips the integration switch so the shared UI calls
`run_defense_pipeline()` before the LLM.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import app.baseline_app as baseline

# Integration switch for Person 3
baseline.APP_VERSION = "protected"
baseline.ENABLE_DEFENSES = True


def main() -> None:
    baseline.main()


if __name__ == "__main__":
    main()
