"""
Shared chat-turn handler for Baseline and Protected apps.

Baseline: enable_defenses=False (no defense imports required at runtime path).
Protected: enable_defenses=True → calls defense.run_defense_pipeline.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from config.system_prompt import SYSTEM_PROMPT
from utils.logger import log_interaction


@dataclass
class TurnOutcome:
    """Result of processing one user message."""

    assistant_text: str
    latency_ms: float
    blocked: bool = False
    block_reason: str | None = None
    defense_stages: list[str] | None = None


def build_api_messages(
    history: list[dict[str, Any]],
    *,
    system_prompt: str,
    latest_user_content: str,
) -> list[dict[str, str]]:
    """
    Build chat messages for the model.

    Uses conversation history for prior turns, but replaces the latest user
    turn with `latest_user_content` (raw for baseline, isolated for protected).
    """
    api_messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]

    # All messages except the trailing user turn we just appended in the UI layer
    prior = history[:-1] if history and history[-1].get("role") == "user" else history
    for message in prior:
        api_messages.append(
            {"role": message["role"], "content": message["content"]}
        )

    api_messages.append({"role": "user", "content": latest_user_content})
    return api_messages


def call_model(
    client: OpenAI,
    api_messages: list[dict[str, str]],
    model_name: str,
) -> tuple[str, float]:
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model_name,
        messages=api_messages,
        temperature=0.7,
    )
    latency_ms = (time.perf_counter() - start) * 1000.0
    assistant_text = response.choices[0].message.content or ""
    return assistant_text, latency_ms


def process_user_turn(
    *,
    user_input: str,
    history: list[dict[str, Any]],
    client: OpenAI,
    model_name: str,
    session_id: str,
    app_version: str,
    enable_defenses: bool,
) -> TurnOutcome:
    """
    Run optional defenses, then call the LLM (unless blocked).

    `history` must already include the raw user message as the last item.
    """
    system_prompt = SYSTEM_PROMPT
    content_for_model = user_input
    blocked = False
    block_reason: str | None = None
    stages: list[str] = []

    if enable_defenses:
        # Import only on the protected path so Baseline stays defense-free.
        from defense.defense_pipeline import run_defense_pipeline

        defense = run_defense_pipeline(user_input, SYSTEM_PROMPT)
        stages = list(defense.stages_applied)
        if not defense.allowed:
            blocked = True
            block_reason = defense.block_reason or "Blocked by defense pipeline"
            assistant_text = (
                "Your request was blocked by the ShopEase security filter. "
                f"Reason: {block_reason}"
            )
            latency_ms = 0.0
            log_interaction(
                session_id=session_id,
                user_input=user_input,
                model_response=assistant_text,
                latency_ms=latency_ms,
                app_version=app_version,
                blocked=True,
                block_reason=block_reason,
                defense_stages=",".join(stages),
            )
            return TurnOutcome(
                assistant_text=assistant_text,
                latency_ms=latency_ms,
                blocked=True,
                block_reason=block_reason,
                defense_stages=stages,
            )

        system_prompt = defense.system_prompt
        content_for_model = defense.user_content_for_model

    try:
        api_messages = build_api_messages(
            history,
            system_prompt=system_prompt,
            latest_user_content=content_for_model,
        )
        assistant_text, latency_ms = call_model(client, api_messages, model_name)
    except Exception as exc:  # noqa: BLE001
        assistant_text = (
            "Sorry, I could not process your request due to a configuration "
            f"or API error: {exc}"
        )
        latency_ms = 0.0

    log_interaction(
        session_id=session_id,
        user_input=user_input,
        model_response=assistant_text,
        latency_ms=latency_ms,
        app_version=app_version,
        blocked=False,
        block_reason=None,
        defense_stages=",".join(stages) if stages else "",
    )

    return TurnOutcome(
        assistant_text=assistant_text,
        latency_ms=latency_ms,
        blocked=False,
        defense_stages=stages or None,
    )
