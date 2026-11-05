"""
Defense pipeline — single entry point used by the Protected app.

Flow (from project plan):
  User input
    → Tier 1: Pattern Guard   (may BLOCK; no LLM call)
    → Tier 2: Prompt Isolation
    → LLM
"""

from __future__ import annotations

from dataclasses import dataclass, field

from defense.pattern_guard import PatternGuardResult, check_input
from defense.prompt_isolation import IsolationResult, isolate_user_content


@dataclass
class DefenseResult:
    """
    Normalized result for the Protected Streamlit app / test runner.

    Attributes:
        allowed: False if Tier 1 blocked the request (do not call the LLM).
        system_prompt: System prompt after Tier 2 (or original if blocked).
        user_content_for_model: User turn text after Tier 2 isolation.
        block_reason: Human-readable reason when allowed is False.
        matched_rule: Optional Tier 1 rule id/name.
        stages_applied: Which stages ran (for logging/analysis).
        isolation_notes: Optional notes from Tier 2.
    """

    allowed: bool
    system_prompt: str
    user_content_for_model: str
    block_reason: str | None = None
    matched_rule: str | None = None
    stages_applied: list[str] = field(default_factory=list)
    isolation_notes: str | None = None


def run_defense_pipeline(user_input: str, system_prompt: str) -> DefenseResult:
    """
    Apply Tier 1 then Tier 2. Safe default stub allows all traffic.

    Person 3 should keep this function as the only public orchestration API
    so Person 1's Protected app and Person 4's test runner stay stable.
    """
    stages: list[str] = []

    # ----- Tier 1: Input Pattern Guard -----
    stages.append("tier1_pattern_guard")
    guard: PatternGuardResult = check_input(user_input)
    if not guard.allowed:
        return DefenseResult(
            allowed=False,
            system_prompt=system_prompt,
            user_content_for_model=user_input,
            block_reason=guard.reason or "Blocked by Input Pattern Guard",
            matched_rule=guard.matched_rule,
            stages_applied=stages,
        )

    # ----- Tier 2: Prompt Isolation -----
    stages.append("tier2_prompt_isolation")
    isolated: IsolationResult = isolate_user_content(user_input, system_prompt)

    return DefenseResult(
        allowed=True,
        system_prompt=isolated.system_prompt,
        user_content_for_model=isolated.isolated_user_input,
        stages_applied=stages,
        isolation_notes=isolated.notes,
    )
