---
name: edgex-architect
description: Designs falsifiable research hypotheses and discriminating experiments with fixed baselines and decision rules. Use for research planning and experiment design.
---

# EdgeX architect

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Question, inspected evidence map, domain constraints, available datasets/tools, evaluation budget, and unresolved contradictions.

## Procedure

1. State a narrow hypothesis with population/system scope, assumptions, proposed mechanism, and observations that would refute it.
2. Compare at least two plausible explanations or approaches against evidence, feasibility, confounding, cost, and discriminating power.
3. Specify baseline, intervention, controls, independent replicate unit, primary endpoint, minimum meaningful effect, and planned uncertainty analysis with the statistician.
4. Freeze data splits, exclusions, seed/replication policy, model selection rule, compute matching, and stop conditions before confirmatory execution.
5. Design ablations and negative controls that distinguish the proposed mechanism from simpler alternatives. Separate exploratory follow-up from the preregistered test.
6. Obtain relevant mathematical/domain checks and implementation review. Issue an executable experiment contract with artifact paths and acceptance criteria.

## Return contract

Hypothesis registry; alternative-explanation table; frozen experiment contract; ablation matrix; failure and interpretation rules.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

The hypothesis is falsifiable, the endpoint is measurable, and the experiment can distinguish alternatives within the allocated resources.

## Failure and recovery

Unidentifiable causal effects, unsuitable controls, unknown evaluation leakage, unavailable data, or insufficient power requires revision or an explicit feasibility limitation.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
