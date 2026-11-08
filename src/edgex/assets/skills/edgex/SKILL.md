---
name: edgex
description: Runs the EdgeX research agent team. Use when the user asks for EdgeX, scientific research, evidence review, reproducible experiments, technical papers, or resuming a long research project.
---

# EdgeX

Use this as the single entry to the EdgeX research team. Work through the host's
existing model, tools and native subagents. No separate model subscription,
API server or Python process is required to activate the skills.

Read [the protocol](references/protocol.md). Apply the relevant
[domain requirements](references/domains.md). Resolve these references relative
to this skill directory, independent of the current working directory.

## Start without an installation conversation

1. Infer the task from the user's request and existing context. Announce
   "EdgeX active: research", "EdgeX active: review", "EdgeX active: writing",
   or "EdgeX active: resume", whichever matches the requested work.
2. Use the installed edgex-orchestrator skill for the task graph, checkpoints,
   budgets and acceptance criteria. Use the host's skill discovery or resolve
   sibling edgex-orchestrator/SKILL.md relative to this skill's parent directory.
   Load only specialists relevant to the task, not all references at once.
3. For research, use scout and architect before builder/executor. Add the
   statistician, mathematician and domain-scientist where their checks apply.
4. For reviewing existing work, use referee and relevant specialists. A review
   request authorizes inspection and findings; implement changes only when asked.
5. For papers, use scribe with the existing evidence ledger and actual results.
   Gather missing evidence through scout; expose unverified claims.
6. For resuming work, use context-manager first, verify canonical artifacts,
   reconcile running jobs and remaining budgets, then continue the next action.
7. Delegate with actual native host tools and record worker identifiers when
   available. Give each worker its matching skill, objective, evidence inputs,
   acceptance criteria, budget, and artifact scope. When unavailable, label
   sequential role passes; do not describe them as independent workers.

## Working rules

Distinguish proposals, reported literature results, reproduced observations,
proofs and speculation. Trace central claims to inspected sources or artifacts.
Use referee and reproducibility for consequential acceptance claims. Preserve
failed attempts, contrary evidence, qualifications and current user constraints.

Use durable files in an authorized project/run directory for long work. Keep
working context bounded and retain pointers to original evidence. The optional
EdgeX Python CLI can store tasks and packets; it is not required for activation.
If it is unavailable, use the protocol's JSON/Markdown task records with host
tools. Never invent a running scheduler, background process or completed check.

Ask only for missing information that materially blocks the next authorized
action. A mode announcement is not a permission request or a saved global setting.
Do not grant new authority or override the host's safety and permission controls.

## Finish

Return the requested deliverable, its evidence/artifact pointers, verification
actually performed, important limitations and remaining work. Keep papers visibly
marked as machine-assisted drafts until their research gates have been reviewed.
