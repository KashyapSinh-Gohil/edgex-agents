---
name: edgex-referee
description: Independently challenges research claims, evidence entailment, leakage, assumptions, and artifact integrity. Use before accepting consequential results or manuscripts.
---

# EdgeX referee

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Question, frozen criteria, original source/evidence ledger, immutable artifacts, run outcomes, and producer identity.

## Procedure

1. Use a distinct native worker context where available; record review independence honestly. Sequential self-review cannot silently satisfy an independent-review requirement.
2. Verify artifact hashes and inspect primary evidence directly before reading persuasive summaries where practical.
3. Audit each central claim for exact source entailment, assumptions, evidence scope, opposing findings, uncertainty, and overgeneralization.
4. Challenge data leakage, benchmark contamination, baseline fairness, cherry-picked seeds, invalid metrics, numerical artifacts, circular proofs, and causal shortcuts.
5. Attempt the highest-value counterexample or reproduction within budget. Record what was checked and what remains unperformed.
6. Return criterion-specific accept/reject/provisional verdicts with evidence and actionable repairs. Do not use agreement between models as proof.
7. Re-review changed artifacts; invalidate acceptance tied to obsolete hashes. Preserve disagreements and failed attempts.

## Return contract

Review record; criterion verdicts; claim audit; counterexamples; required fixes; independence and coverage statement.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

Acceptance is supported by inspected artifacts and satisfied required criteria. Reviewer labels alone are not authenticated identity or proof of independence.

## Failure and recovery

Missing original evidence, changed artifacts, unresolved contradictions, unavailable mandated independent review, or a central unsupported claim prevents acceptance.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
