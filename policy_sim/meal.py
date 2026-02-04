from __future__ import annotations

from typing import Iterable, List, Mapping

from .models import HistoricalPolicy, PolicyInput


def _context_diff(policy_meta: Mapping[str, str], hist_meta: Mapping[str, str]) -> List[str]:
    diffs = []
    for key in sorted(set(policy_meta) | set(hist_meta)):
        if policy_meta.get(key) != hist_meta.get(key):
            diffs.append(key)
    return diffs


def generate_context_warnings(
    policy: PolicyInput,
    historical_policies: Iterable[HistoricalPolicy],
    max_warnings: int = 3,
) -> List[str]:
    """Generate MEAL-style warnings about context transferability."""

    warnings: List[str] = []

    for episode in historical_policies:
        diffs = _context_diff(policy.metadata, episode.metadata)
        if diffs:
            warnings.append(
                "Context differs from historical episode "
                f"'{episode.name}' on: {', '.join(diffs)}."
            )
        if len(warnings) >= max_warnings:
            break

    if not warnings:
        warnings.append("No material context differences detected in metadata.")

    return warnings
