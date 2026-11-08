# Contributing

Use Python 3.10 or newer. Install with `python -m pip install -e '.[dev]'` and run
`python -m pytest -q`. Validate an installed wheel, including bundled SKILL.md and
reference files, before changing the installer or package layout.

Send focused pull requests with a concrete behavioral example and verification.
Do not commit keys, private datasets, research runs, or upstream source checkouts.
Preserve existing project instructions and locally modified installed skills.

Changes to research protocols must state their evidence basis, failure modes, and
how a researcher can verify the resulting claims. Keep source existence, source
entailment, experiment success, and scientific validity separate. Never claim lab
endorsement, certification, legal compliance, or benchmark performance without evidence.

The runtime uses one coordinator per run; use the CLI lock when driving it from
multiple processes. Native host agents do the delegated research. Add tests for
state transitions, evidence handling, recovery, and installer conflicts.
