import argparse
from textwrap import dedent

TEMPLATES = {
    "bugfix": dedent(
        """\
        You are implementing a fix in the ICGL codebase.
        Goal: {goal}
        Scope files: {files}
        Acceptance:
        - Repro: {repro}
        - Expected: {expected}
        - Tests: add/adjust minimal test to cover the fix.
        Output:
        - Patch ready to apply.
        - Test snippet.
        - Note any side-effects."""
    ),
    "feature": dedent(
        """\
        You are adding a small feature in the ICGL codebase.
        Goal: {goal}
        Scope files: {files}
        Constraints: keep changes minimal and backward compatible.
        Acceptance:
        - Behavior: {expected}
        - Tests: add a focused test to cover the new path.
        Output:
        - Patch ready to apply.
        - Test snippet.
        - Any config/doc updates (brief)."""
    ),
    "docs": dedent(
        """\
        You are improving documentation.
        Goal: {goal}
        Scope files: {files}
        Acceptance:
        - Clear, concise, actionable.
        - No duplicate content.
        Output:
        - Updated doc content ready to apply.
        - Include examples if needed."""
    ),
    "perf": dedent(
        """\
        You are making a targeted performance improvement.
        Goal: {goal}
        Scope files: {files}
        Constraints: preserve behavior; add guardrails for regressions.
        Acceptance:
        - Metric: {expected}
        - Tests/bench: add a small benchmark or assertion if feasible.
        Output:
        - Patch ready to apply with notes on why it’s faster and any trade-offs."""
    ),
}


def main():
    parser = argparse.ArgumentParser(
        description="Render a ready-to-paste LLM prompt for ICGL work."
    )
    parser.add_argument(
        "type",
        choices=TEMPLATES.keys(),
        help="Prompt type: bugfix, feature, docs, perf",
    )
    parser.add_argument("--goal", required=True, help="Short goal/intent")
    parser.add_argument("--files", default="(list key files)", help="File paths/scope")
    parser.add_argument(
        "--repro", default="(how to reproduce)", help="Repro steps (bugfix only)"
    )
    parser.add_argument(
        "--expected", default="(expected result/metric)", help="Expected outcome"
    )
    args = parser.parse_args()

    template = TEMPLATES[args.type]
    prompt = template.format(
        goal=args.goal, files=args.files, repro=args.repro, expected=args.expected
    )
    print(prompt)


if __name__ == "__main__":
    main()
