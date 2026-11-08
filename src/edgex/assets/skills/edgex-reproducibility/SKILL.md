---
name: edgex-reproducibility
description: Independently reproduces central research results from frozen code, data, environment, and commands. Use before asserting reproducibility or releasing a research bundle.
---

# EdgeX reproducibility

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Frozen manifests, accepted experiment/proof artifacts, original reported outcomes, exact commands, and reproduction tolerance/budget.

## Procedure

1. Verify identities and accessibility of code, configurations, data splits/releases, dependencies, hardware assumptions, and artifacts.
2. Prepare a clean authorized environment from the recorded specification. Document unavailable proprietary inputs, nondeterministic kernels, and platform differences.
3. Rerun the smallest decisive baseline/intervention or formal/symbolic check without silently borrowing producer intermediate state.
4. Compare observed outcomes to preregistered numerical/statistical tolerances. Distinguish bitwise determinism, numerical agreement, and scientific replication.
5. Diagnose discrepancies through version, seed, preprocessing, hardware, solver, and analysis differences; preserve failed attempts and raw logs.
6. Return exact instructions and a manifest that another researcher can follow. If required independent resources are unavailable, record reproduction as unperformed.

## Return contract

Clean-environment instructions; rerun logs; hashed output manifest; comparison/tolerance assessment; discrepancy report.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

An actual rerun supports the stated reproduction claim within a defined scope and tolerance. A README or producer rerun alone is insufficient.

## Failure and recovery

Missing data/code, unverifiable versions, unperformed rerun, unexplained discrepancy, or hidden producer state prevents a reproducibility claim.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
