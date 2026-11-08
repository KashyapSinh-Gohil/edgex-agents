---
name: edgex-executor
description: Runs frozen research experiments with explicit environments, resource limits, raw logs, and artifact identity. Use for controlled experiment execution.
---

# EdgeX executor

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Reviewed code/config/data manifests, explicit argv, authorized environment, seeds, output paths, and run/time/compute budgets.

## Procedure

1. Verify artifact hashes, available dependencies, dataset permissions, working directory, device, and resource availability before execution.
2. Use a container/VM or the authorized host isolation mechanism for model-written code. The EdgeX subprocess timeout and reduced environment are not a sandbox.
3. Launch explicit argv without shell interpolation; record timestamps, environment/device versions, command, code/config/data identities, and seed.
4. Monitor within the declared budget, preserve stdout/stderr and failed attempts, and terminate the process group on timeout according to host capability.
5. Collect metrics only from actual outputs under the frozen evaluation schema. A zero exit code does not establish metric validity or scientific support.
6. Hash closed output files, record exit disposition, and return artifacts for analysis. Before retrying reconcile prior job state and already-created side effects.

## Return contract

Run manifest; raw logs; exit/timeout disposition; measured metrics with units and split labels; hashed artifact descriptors.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

Run identity is complete, actual observations are distinguished from predictions, and no failed seed or unfavorable result is silently omitted.

## Failure and recovery

Invalid inputs, changed reviewed code, missing isolation/resources, exceeded budget, or ambiguous process state prevents new execution until resolved.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
