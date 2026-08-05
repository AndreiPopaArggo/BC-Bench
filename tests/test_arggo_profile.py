"""Tests for the Arggo review profile: entry resolution, overlays, allowed-comment scoring."""

import json
from unittest.mock import patch

import pytest

from bcbench import arggo_profile
from bcbench.arggo_profile import ReviewProfile, UpstreamOverlay, apply_overlay, load_overlays, resolve_codereview_entry
from bcbench.dataset.codereview import ReviewComment, Severity
from bcbench.evaluate.codereview import CodeReviewPipeline
from bcbench.results.codereview import CodeReviewResult, CodeReviewResultSummary
from bcbench.types import EvaluationCategory
from tests.conftest import create_codereview_entry, create_codereview_result, create_evaluation_context


def _comment(line: int, body: str, file: str = "src/app.al") -> ReviewComment:
    return ReviewComment(file=file, line_start=line, body=body, severity=Severity.LOW)


class TestEntryResolution:
    def test_arggo_entry_requires_arggo_profile(self):
        with pytest.raises(ValueError, match="--review-profile arggo"):
            resolve_codereview_entry("arggo__naming-001", ReviewProfile.UPSTREAM)

    def test_upstream_entry_under_arggo_profile_requires_overlay(self):
        with patch.object(arggo_profile, "load_overlays", return_value={}):
            with pytest.raises(ValueError, match="no Arggo overlay"):
                resolve_codereview_entry("synthetic__security-001", ReviewProfile.ARGGO)

    def test_upstream_entry_under_upstream_profile_is_unchanged(self):
        entry = resolve_codereview_entry("synthetic__security-001", ReviewProfile.UPSTREAM)
        assert entry.instance_id == "synthetic__security-001"
        assert entry.allowed_comments == []
        assert entry.fixture_patch is None

    def test_upstream_entry_under_arggo_profile_merges_overlay(self):
        overlay = UpstreamOverlay(
            instance_id="synthetic__security-001",
            required_comments=[_comment(1, "required house finding")],
            allowed_comments=[_comment(2, "allowed house finding")],
        )
        with patch.object(arggo_profile, "load_overlays", return_value={overlay.instance_id: overlay}):
            entry = resolve_codereview_entry("synthetic__security-001", ReviewProfile.ARGGO)

        assert entry.expected_comments[-1].body == "required house finding"
        assert [c.body for c in entry.allowed_comments] == ["allowed house finding"]

    def test_rule_id_survives_dataset_roundtrip(self):
        comment = ReviewComment(file="src/app.al", line_start=3, body="x", severity=Severity.LOW, rule_id="ARGGO.NAMING.PARAM_PREFIX")
        restored = ReviewComment.model_validate(json.loads(comment.model_dump_json()))
        assert restored.rule_id == "ARGGO.NAMING.PARAM_PREFIX"


class TestOverlayLoading:
    def test_load_overlays_missing_file_returns_empty(self, tmp_path):
        assert load_overlays(tmp_path / "nope.jsonl") == {}

    def test_load_overlays_parses_entries(self, tmp_path):
        path = tmp_path / "overlays.jsonl"
        path.write_text(
            json.dumps({"instance_id": "synthetic__style-001", "allowed_comments": [{"file": "src/a.al", "line_start": 1, "body": "b"}]}) + "\n",
            encoding="utf-8",
        )
        overlays = load_overlays(path)
        assert overlays["synthetic__style-001"].allowed_comments[0].body == "b"
        assert overlays["synthetic__style-001"].required_comments == []

    def test_load_overlays_rejects_duplicates(self, tmp_path):
        path = tmp_path / "overlays.jsonl"
        line = json.dumps({"instance_id": "synthetic__style-001"})
        path.write_text(line + "\n" + line + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Duplicate overlay"):
            load_overlays(path)

    def test_apply_overlay_appends_not_replaces(self):
        entry = create_codereview_entry(expected_comments=[_comment(10, "upstream gold")])
        overlay = UpstreamOverlay(instance_id=entry.instance_id, required_comments=[_comment(20, "house gold")], allowed_comments=[_comment(30, "optional")])
        merged = apply_overlay(entry, overlay)
        assert [c.body for c in merged.expected_comments] == ["upstream gold", "house gold"]
        assert [c.body for c in merged.allowed_comments] == ["optional"]
        # original stays frozen/unmodified
        assert [c.body for c in entry.expected_comments] == ["upstream gold"]


class TestAllowedScoring:
    def test_allowed_matches_leave_precision_and_recall(self, tmp_path):
        expected = [_comment(10, "gold issue")]
        generated = [_comment(10, "found gold"), _comment(30, "house convention"), _comment(50, "noise")]
        context = create_evaluation_context(tmp_path, entry=create_codereview_entry(expected_comments=expected), category=EvaluationCategory.CODE_REVIEW)

        result = CodeReviewResult.create(
            context,
            output="[]",
            expected_comments=expected,
            generated_comments=generated,
            matched_pairs=[(expected[0], generated[0])],
            allowed_pairs=[(_comment(30, "allowed"), generated[1])],
        )

        # precision: 1 matched / (3 generated - 1 allowed) = 0.5; recall 1/1
        assert result.matched_comment_count == 1
        assert result.allowed_match_count == 1
        assert result.incorrect_comment_count == 1
        assert result.precision == pytest.approx(0.5)
        assert result.recall == pytest.approx(1.0)

    def test_no_allowed_pairs_matches_legacy_scoring(self, tmp_path):
        expected = [_comment(10, "gold issue")]
        generated = [_comment(10, "found gold"), _comment(50, "noise")]
        context = create_evaluation_context(tmp_path, entry=create_codereview_entry(expected_comments=expected), category=EvaluationCategory.CODE_REVIEW)

        kwargs = dict(output="[]", expected_comments=expected, generated_comments=generated, matched_pairs=[(expected[0], generated[0])])
        legacy = CodeReviewResult.create(context, **kwargs)
        with_empty_allowed = CodeReviewResult.create(context, **kwargs, allowed_pairs=[])

        assert with_empty_allowed.precision == legacy.precision == pytest.approx(0.5)
        assert with_empty_allowed.incorrect_comment_count == legacy.incorrect_comment_count == 1
        assert with_empty_allowed.allowed_match_count == legacy.allowed_match_count == 0

    def test_summary_reports_clean_task_gate(self):
        clean_pass = create_codereview_result(instance_id="synthetic__style-001", output="[]")
        clean_fail = create_codereview_result(instance_id="synthetic__style-002", output='[{"file": "a.al", "line_start": 1, "body": "fp one"}, {"file": "a.al", "line_start": 2, "body": "fp two"}]')
        positive = create_codereview_result(
            instance_id="synthetic__style-003",
            output='[{"file": "src/app.al", "line_start": 10, "body": "hit"}]',
            expected_comments=[_comment(10, "gold")],
        )

        summary = CodeReviewResultSummary.from_results([clean_pass, clean_fail, positive], run_id="t")

        assert summary.clean_task_count == 2
        assert summary.clean_pass_rate == pytest.approx(0.5)
        assert summary.mean_fp_per_clean_task == pytest.approx(1.0)

    def test_pipeline_allowed_matching_runs_only_on_leftovers(self, tmp_path):
        expected = [_comment(10, "gold issue")]
        allowed = [_comment(10, "house rule near the gold"), _comment(30, "house rule elsewhere")]
        generated = [_comment(10, "found gold"), _comment(30, "house convention")]
        entry = create_codereview_entry(expected_comments=expected).model_copy(update={"allowed_comments": allowed})
        context = create_evaluation_context(tmp_path, entry=entry, category=EvaluationCategory.CODE_REVIEW)

        pipeline = CodeReviewPipeline()
        validated = [(expected[0], generated[0])]
        with patch("bcbench.evaluate.codereview.judge_comment_matches", side_effect=lambda pairs, work_dir: pairs) as judge:
            allowed_pairs = pipeline._match_allowed_comments(context, generated, validated)

        # the gold-matched generated comment is excluded, so only the leftover
        # can match — and it lands on the line-30 allowed comment.
        assert len(allowed_pairs) == 1
        assert allowed_pairs[0][0].line_start == 30
        assert allowed_pairs[0][1] is generated[1]
        judge.assert_called_once()

    def test_pipeline_allowed_matching_skips_without_allowed_comments(self, tmp_path):
        entry = create_codereview_entry(expected_comments=[_comment(10, "gold")])
        context = create_evaluation_context(tmp_path, entry=entry, category=EvaluationCategory.CODE_REVIEW)

        pipeline = CodeReviewPipeline()
        with patch("bcbench.evaluate.codereview.judge_comment_matches") as judge:
            assert pipeline._match_allowed_comments(context, [_comment(50, "noise")], []) == []
        judge.assert_not_called()
