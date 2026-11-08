---
name: edgex-context-manager
description: Maintains bounded working context and faithful checkpoints for long research tasks. Use before compaction, handoff, restart, or context saturation.
---

# EdgeX context-manager

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Canonical run state, task graph, artifact manifest, evidence ledger, current constraints, resource accounting, and context budget.

## Procedure

1. Identify canonical artifacts and the current objective/authority. Separate durable evidence from working summaries and pointers.
2. Prioritize decision-relevant facts: unresolved blockers, constraints, contradictions, negative results, accepted artifact identities, and remaining budget.
3. Use edgex context RUN --max-chars N for a bounded packet. The limit is characters, not model tokens. Record omissions and retrieve originals on demand.
4. Before compaction persist task states, host/process identifiers, review decisions, spent resources, frozen assumptions, and the exact next action.
5. On resume reread current instructions, rehash critical artifacts, reconcile actually running work, and check whether external actions already completed.
6. Never promote summary text to primary evidence or erase unfavorable results to fit the window. Do not reset budgets or duplicate costly work after context loss.

## Return contract

Bounded context packet; canonical file pointers; checkpoint manifest; unresolved issues; explicit resume procedure.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

Summary is faithful to originals and retains material qualifications, authority constraints, contradictions, and budget state. Omitted material remains retrievable.

## Failure and recovery

Missing canonical artifacts, hash mismatch, ambiguous running state, lost permission constraints, or unrecoverable provenance prevents authoritative resume.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
