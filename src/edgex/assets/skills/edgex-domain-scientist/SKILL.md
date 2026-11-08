---
name: edgex-domain-scientist
description: Checks physical and disciplinary validity across physics, chemistry, biology, quantum science, space, AI, and engineering. Use for domain assumptions and cross-domain research.
---

# EdgeX domain-scientist

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Question, governing model, domain regime, data provenance, experimental or simulation setup, claimed conclusions, and applicable domain checklist.

## Procedure

1. Select relevant sections of the bundled domain requirements. Identify required expertise/tools and explicitly mark unavailable validation.
2. For physics inspect governing laws, dimensions, approximations, conservation, symmetries, boundary conditions, and numerical convergence.
3. For chemistry inspect species, charge/spin, stoichiometry, phase, standard states, method/basis/solvation, and thermodynamic versus kinetic interpretations.
4. For biology inspect organism/reference versions, assay controls, independent replicates, batch/confounding, consent/access, and observational versus causal claims.
5. For quantum work inspect state/operator validity, basis conventions, preparation/measurement costs, noise/shots, and comparable classical baselines.
6. For space inspect frames, units, time scales/epochs, ephemeris versions, calibration, uncertainty propagation, and observation versus simulation.
7. Evaluate whether the evidence supports conclusions under the stated regime. Request qualified review when acceptance requires expertise or physical experiments outside the available environment.

## Return contract

Domain assumption register; units/regime checks; model applicability; validation requirements; scoped verdict and limitations.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

No cross-regime, unit, frame, replicate, or simulation/observation substitution supports a conclusion. Computational success does not imply physical validation.

## Failure and recovery

Incompatible regimes, invalid states/structures, pseudoreplication, uncalibrated data, or operational activity outside existing authorization blocks the affected claim.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
