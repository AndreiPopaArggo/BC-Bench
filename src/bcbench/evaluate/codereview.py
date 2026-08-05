import subprocess
from collections.abc import Callable
from pathlib import Path

from bcbench.dataset.codereview import CodeReviewEntry, ReviewComment
from bcbench.evaluate.base import EvaluationPipeline
from bcbench.evaluate.codereview_judge import judge_comment_matches
from bcbench.evaluate.review_parsing import parse_review_output
from bcbench.github_actions import github_log_group
from bcbench.logger import get_logger
from bcbench.operations import apply_patch, fetch_commit_if_missing, setup_repo_prebuild
from bcbench.results.codereview import CodeReviewResult, match_comments
from bcbench.types import EvaluationContext

logger = get_logger(__name__)

REVIEW_OUTPUT_FILE = "review.json"

__all__ = ["CodeReviewPipeline"]


def _patched_paths(patch: str) -> list[str]:
    return [line[6:].strip() for line in patch.splitlines() if line.startswith("+++ b/")]


class CodeReviewPipeline(EvaluationPipeline[CodeReviewEntry]):
    """Pipeline for code-review evaluation category.

    Code review does not require a BC container. We materialize the dataset patch
    as local git changes so the agent can review the branch diff directly.
    """

    def setup_workspace(self, entry: CodeReviewEntry, repo_path: Path) -> None:
        """Setup workspace for code review by applying the entry patch as local changes."""
        # Code-review base commits are pre-squash PR commits, so they might be missing from local dev setups.
        fetch_commit_if_missing(repo_path, entry.base_commit)
        setup_repo_prebuild(entry, repo_path)
        if entry.fixture_patch:
            self._commit_fixture(entry, repo_path)
        apply_patch(repo_path, entry.patch, f"{entry.instance_id} review patch")
        # Mark newly added files as intent-to-add so they appear in `git diff HEAD`;
        # all dataset patches are new-file diffs, which are otherwise untracked and invisible to the agent.
        if paths := _patched_paths(entry.patch):
            subprocess.run(
                ["git", "add", "-N", "--", *paths],
                cwd=repo_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True,
            )

    def _commit_fixture(self, entry: CodeReviewEntry, repo_path: Path) -> None:
        """Apply and commit supporting fixture files (e.g. CONVENTIONS.md).

        Committing keeps fixtures visible as workspace context while excluding
        them from the uncommitted diff the agent is asked to review.
        """
        assert entry.fixture_patch is not None
        apply_patch(repo_path, entry.fixture_patch, f"{entry.instance_id} fixture patch")
        subprocess.run(["git", "add", "-A"], cwd=repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        subprocess.run(
            ["git", "-c", "user.name=bcbench", "-c", "user.email=bcbench@localhost", "commit", "-m", f"{entry.instance_id} conventions fixture", "--no-verify"],
            cwd=repo_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
        )

    def setup(self, context: EvaluationContext[CodeReviewEntry]) -> None:
        self.setup_workspace(context.entry, context.repo_path)

    def run_agent(self, context: EvaluationContext[CodeReviewEntry], agent_runner: Callable) -> None:
        with github_log_group(f"{context.agent_name} -- Entry: {context.entry.instance_id}"):
            context.metrics, context.experiment = agent_runner(context)

    def evaluate(self, context: EvaluationContext[CodeReviewEntry]) -> None:
        review_output_file: Path = context.repo_path / REVIEW_OUTPUT_FILE

        if not review_output_file.exists():
            logger.error(f"No review generated for {context.entry.instance_id}")
            raise RuntimeError(f"No review generated for {context.entry.instance_id}")
        output: str = review_output_file.read_text(encoding="utf-8")

        generated_comments: list[ReviewComment] | None = parse_review_output(output)

        if generated_comments is None:
            logger.warning(f"Invalid review output for {context.entry.instance_id}")
            result = CodeReviewResult.create_invalid(context, output, context.entry.expected_comments)
        else:
            structural_matches = match_comments(
                context.entry.expected_comments,
                generated_comments,
            )
            validated_matches = judge_comment_matches(
                structural_matches,
                work_dir=context.repo_path,
            )
            allowed_pairs = self._match_allowed_comments(context, generated_comments, validated_matches)
            result = CodeReviewResult.create(
                context,
                output=output,
                expected_comments=context.entry.expected_comments,
                generated_comments=generated_comments,
                matched_pairs=validated_matches,
                allowed_pairs=allowed_pairs,
            )
        logger.info(f"Parsed {len(result.generated_comments)} comments from {REVIEW_OUTPUT_FILE}")
        logger.info(
            f"Code review metrics: matched={result.matched_comment_count}, "
            f"incorrect={result.incorrect_comment_count}, missed={result.missed_comment_count}, "
            f"allowed={result.allowed_match_count}, "
            f"precision={result.precision:.3f}, recall={result.recall:.3f}, f1={result.f1:.3f}"
        )

        self.save_result(context, result)

    def _match_allowed_comments(
        self,
        context: EvaluationContext[CodeReviewEntry],
        generated_comments: list[ReviewComment],
        validated_matches: list[tuple[ReviewComment, ReviewComment]],
    ) -> list[tuple[ReviewComment, ReviewComment]]:
        """Match leftover generated comments against the entry's allowed_comments (arggo profile).

        Runs AFTER gold matching so an allowed comment can never absorb a finding
        that should have counted as a gold match. One-to-one: each allowed comment
        neutralizes at most one generated comment; duplicates stay false positives.
        """
        if not context.entry.allowed_comments:
            return []

        remaining = list(generated_comments)
        for _, generated in validated_matches:
            remaining.remove(generated)
        if not remaining:
            return []

        structural = match_comments(context.entry.allowed_comments, remaining)
        return judge_comment_matches(structural, work_dir=context.repo_path)
