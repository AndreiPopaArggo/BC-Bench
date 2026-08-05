"""Arggo review profile: score code reviews against Arggo house conventions.

The upstream dataset and scoring stay untouched under the default profile.
Under ``--review-profile arggo``:

- ``arggo__*`` entry IDs resolve from ``dataset/arggo/codereview.jsonl`` — a
  separate task set whose golds are Arggo convention violations (paired
  defect/clean entries; some ship a committed CONVENTIONS.md fixture).
- Upstream entry IDs are merged with ``dataset/arggo/upstream-overlays.jsonl``:
  ``required_comments`` join the golds (TP/FN), ``allowed_comments`` become
  neutral (matching one is neither TP nor FP). An upstream entry without an
  overlay refuses to run under the arggo profile — partially annotated
  aggregates would just relocate the unfairness the profile exists to fix.

Annotations are frozen data adjudicated offline; no live judge decides what
counts as an acceptable finding at scoring time.
"""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from bcbench.config import get_config
from bcbench.dataset.codereview import CodeReviewEntry, ReviewComment
from bcbench.types import EvaluationCategory

_config = get_config()

ARGGO_ENTRY_PREFIX = "arggo__"


class ReviewProfile(StrEnum):
    UPSTREAM = "upstream"
    ARGGO = "arggo"


def arggo_dataset_dir() -> Path:
    return _config.paths.dataset_dir / "arggo"


def arggo_dataset_path() -> Path:
    return arggo_dataset_dir() / "codereview.jsonl"


def upstream_overlays_path() -> Path:
    return arggo_dataset_dir() / "upstream-overlays.jsonl"


class UpstreamOverlay(BaseModel):
    """Arggo annotations for one upstream code-review entry."""

    model_config = ConfigDict(frozen=True)

    instance_id: str
    required_comments: list[ReviewComment] = Field(default_factory=list)
    allowed_comments: list[ReviewComment] = Field(default_factory=list)


def load_overlays(path: Path | None = None) -> dict[str, UpstreamOverlay]:
    path = path or upstream_overlays_path()
    if not path.exists():
        return {}
    overlays: dict[str, UpstreamOverlay] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        overlay = UpstreamOverlay.model_validate(json.loads(line))
        if overlay.instance_id in overlays:
            raise ValueError(f"Duplicate overlay for {overlay.instance_id} in {path}")
        overlays[overlay.instance_id] = overlay
    return overlays


def apply_overlay(entry: CodeReviewEntry, overlay: UpstreamOverlay) -> CodeReviewEntry:
    return entry.model_copy(
        update={
            "expected_comments": [*entry.expected_comments, *overlay.required_comments],
            "allowed_comments": [*entry.allowed_comments, *overlay.allowed_comments],
        }
    )


def resolve_codereview_entry(entry_id: str, profile: ReviewProfile) -> CodeReviewEntry:
    """Load a code-review entry honoring the review profile.

    Raises ValueError on profile/entry mismatches instead of silently degrading:
    arggo entries scored upstream-style (or upstream entries scored arggo-style
    without an adjudicated overlay) would produce numbers that look comparable
    but are not.
    """
    if entry_id.startswith(ARGGO_ENTRY_PREFIX):
        if profile is not ReviewProfile.ARGGO:
            raise ValueError(f"{entry_id} is an Arggo-profile entry; run it with --review-profile arggo")
        return CodeReviewEntry.load(arggo_dataset_path(), entry_id=entry_id)[0]

    entry = CodeReviewEntry.load(EvaluationCategory.CODE_REVIEW.dataset_path, entry_id=entry_id)[0]
    if profile is ReviewProfile.UPSTREAM:
        return entry

    overlay = load_overlays().get(entry_id)
    if overlay is None:
        raise ValueError(
            f"{entry_id} has no Arggo overlay in {upstream_overlays_path()}; "
            "annotate it (required/allowed) before scoring it under the arggo profile"
        )
    return apply_overlay(entry, overlay)
