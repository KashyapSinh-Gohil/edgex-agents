# Working on EdgeX

EdgeX's scientific integrity claims must match actual implementation and tests.
Keep host instructions, local structural checks, and semantic scientific review
distinct. Do not describe a passing process or a citation ID as a validated finding.

Use Python 3.10+ and standard-library runtime dependencies. Run
`python -m pytest -q` after installing `.[dev]`. Changes to package resources or
installation must also be tested from a built wheel outside the source directory.
Preserve locally modified user skills; do not add force-overwrite behavior.

The coordinator alone updates run state. Use `RunStore.exclusive()` for library
workflows with multiple processes. Return specialist artifacts through task leases.
Tests must cover consequential state transitions and recovery, not only happy paths.

Keep every shipped skill self-contained: all references must resolve within its
installed directory. Native subagent behavior is supplied by the host, and generic
sequential role passes must never be represented as independent parallel work.

Do not commit credentials, research runs, local environment files, unrelated
workspace files, or upstream source checkouts. Public guidance can motivate EdgeX
policies but cannot establish private lab equivalence, endorsement, or certification.
