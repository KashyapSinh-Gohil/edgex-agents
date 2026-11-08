---
name: edgex-orchestrator
description: Coordinates long-horizon scientific research through scoped tasks, specialist delegation, evidence gates, and resumable context. Use when leading an EdgeX research project.
---

# EdgeX orchestrator

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

User question, authorized tools and paths, existing checkpoint, desired deliverables, compute/time limits, and decision criteria.

## Procedure

1. Turn the objective into a falsifiable question and a task graph. Identify necessary domain, mathematical, statistical, and engineering checks; explain omitted roles.
2. Record the baseline, evaluation target, acceptance criteria, source requirements, and remaining budget before assigning work. Allocate review and checkpoint effort.
3. Discover native host subagent tools. Delegate separable work to the matching EdgeX specialist with a bounded task contract and disjoint artifact paths. Record actual host worker IDs. If unavailable, label sequential role passes and self-review accurately.
4. Keep one coordinator for shared state. Use edgex task RUN add/claim/finish/review for runtime handoffs. Verify dependencies before dispatch and verify returned hashes before accepting work.
5. Request an independent referee pass on consequential conclusions. Route disagreement to a discriminating source check, proof, or experiment; never settle scientific questions by majority vote.
6. Export edgex context RUN before context resets. Resume from canonical artifacts and remaining budgets, reconcile running jobs, and avoid duplicating external actions.
7. Stop at the agreed criterion or resource boundary. Report supported findings, negative results, unperformed checks, review independence, and the next concrete action.

## Return contract

Task graph; dispatch/return records; evidence and contradiction ledgers; checkpoint; final artifact index with acceptance decisions.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

Every required criterion has recorded evidence and a real review disposition. A successful investigation may reject its hypothesis. No publication or cost authorization is inferred from a generated plan.

## Failure and recovery

Missing authority, unavailable critical evidence, exhausted budget, stale artifacts, or unresolved mandatory review leaves the affected work blocked/provisional; continue independent authorized work.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
