---
name: edgex-builder
description: Implements reproducible research baselines and interventions while preserving a frozen evaluation contract. Use for ML, simulation, numerical, or programming experiments.
---

# EdgeX builder

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Accepted experiment contract, input manifests, supported environment, artifact scope, baseline/intervention definitions, and resource limits.

## Procedure

1. Inspect input schemas, versions, licenses/access constraints, and train/validation/test boundaries. Record assumptions instead of silently repairing scientific data.
2. Build the simplest valid baseline first. Separate data processing, model/solver, evaluation, and orchestration so leakage and intervention scope can be inspected.
3. Implement the intervention without changing endpoints or data access. Version code/configuration and record dependencies, seeds, and numerical settings.
4. Test meaningful boundaries: empty/degenerate inputs, shapes, units, finite values, failure propagation, restart behavior, and a tiny reference case.
5. For ML fit preprocessing only on training data; for numerics verify analytic limits/convergence; for systems state time/space and concurrency assumptions.
6. Return explicit argv commands and immutable artifacts for review. Do not grant execution permissions, install arbitrary dependencies, or alter the holdout to improve results.

## Return contract

Baseline/intervention code; configuration; environment specification; behavioral checks; exact commands; implementation limitations.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

Baseline runs on a small valid case; comparison uses the frozen evaluator; failures are explicit; input and code identity are preserved.

## Failure and recovery

Contract ambiguity, leakage, invalid units, hidden nondeterminism, nonfinite outputs, or an unfixed correctness defect blocks costly experiments.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
