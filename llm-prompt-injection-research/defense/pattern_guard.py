"""
Tier 1 — Input Pattern Guard (Person 3).

Inspect user input with Regex / heuristic rules.
If a block rule matches, the request must NOT call the LLM API.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatternGuardResult:
    """Outcome of Tier 1 screening."""

    allowed: bool
    reason: str | None = None
    matched_rule: str | None = None


def check_input(user_input: str) -> PatternGuardResult:
    """
    Screen raw user input before the model is called.

    Person 3: replace this stub with real Regex + heuristic rules.
    The Baseline app never calls this function.

    Contract:
      - return allowed=False to block (no LLM call)
      - return allowed=True to continue to Tier 2
    """
    # --- Person 3 TODO: implement blocking patterns here ---
    # Example shape (do NOT enable until rules are finalized):
    # patterns = [r"ignore\\s+previous\\s+instructions", ...]
    _ = user_input
    return PatternGuardResult(allowed=True, reason=None, matched_rule=None)
