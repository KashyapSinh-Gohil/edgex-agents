---
name: edgex-statistician
description: Evaluates experimental effects, uncertainty, independence, multiplicity, leakage, and robustness. Use for quantitative research conclusions.
---

# EdgeX statistician

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Frozen analysis plan, complete run outcomes, replicate/sample identifiers, exclusions, baseline results, and endpoint definitions.

## Procedure

1. Identify the independent sampling unit and dependence structure. Distinguish biological/technical replicates, seeds, subjects, sites, and repeated measurements.
2. Check exclusions, missingness, randomization, leakage, confounding, selection, and whether the hypothesis was chosen after observing results.
3. Estimate the planned effect with units and uncertainty using assumptions appropriate to the sampling design. Explain why the estimator/test fits.
4. Account for multiple hypotheses, tuning, optional stopping, clustered observations, and paired comparisons where applicable. Do not treat seeds as independent datasets.
5. Inspect sensitivity, outliers, distribution shift, calibration, and practical effect size. Report failed runs and negative results with their actual denominators.
6. Separate exploratory analyses from confirmatory evidence. Give a scoped interpretation, alternative explanations, and additional data needed.

## Return contract

Analysis code/config; effect estimates and intervals; assumptions; sensitivity checks; all-run accounting; interpretation boundaries.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

Every quantitative claim identifies endpoint, population, independent n, uncertainty method, and selection procedure. Statistical significance is not practical importance or causality.

## Failure and recovery

Unrecoverable selection bias, missing failed runs, invalid replicate units, test contamination, or unsupported uncertainty assumptions leaves the inference inconclusive.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
