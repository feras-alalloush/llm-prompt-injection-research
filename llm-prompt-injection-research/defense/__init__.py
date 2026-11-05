"""
Defense package — integration surface for Person 3.

Person 3 implements:
  - pattern_guard.py      (Tier 1)
  - prompt_isolation.py   (Tier 2)
  - defense_pipeline.py   (orchestration)

The Baseline app never imports these modules.
The Protected app calls `run_defense_pipeline()` only.
"""

from defense.defense_pipeline import DefenseResult, run_defense_pipeline

__all__ = ["DefenseResult", "run_defense_pipeline"]
