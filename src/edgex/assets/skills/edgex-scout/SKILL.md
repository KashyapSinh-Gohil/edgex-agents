---
name: edgex-scout
description: Finds and verifies primary scientific sources, source versions, exact evidence locators, and contrary results. Use for literature review, citations, or novelty checks.
---

# EdgeX scout

Read [the shared protocol](references/protocol.md) before acting. Apply the relevant
[domain requirements](references/domains.md). These are part of this skill and
resolve relative to this directory. Respect current user scope and host permissions.

## Inputs

Bounded research question, inclusion/exclusion criteria, date range, required domains, existing source ledger, and search budget.

## Procedure

1. Translate the question into multiple query families: mechanism, baseline, closest prior work, negative findings, and counterexamples. Record databases, dates, queries, and filters.
2. Search primary repositories, publishers, preprint archives, and authoritative dataset/code releases. Distinguish peer-reviewed papers, preprints, reviews, and vendor claims.
3. Resolve source identity using DOI/arXiv/version or repository commit. Read relevant full text when available; explicitly record abstract-only or inaccessible sources.
4. Extract only necessary excerpts with section/page/equation/table locators, assumptions, sample size, measured endpoint, units, and qualifications.
5. Check corrections, retractions, superseded versions, and duplicate reports where ascertainable. Preserve contradictory evidence rather than ranking only by citation count.
6. Return a claim-to-source map and unresolved access/novelty gaps. A failed search cannot establish novelty or prove absence.

## Return contract

Search log; deduplicated source ledger; located evidence records; closest-work comparison; contrary evidence and access limitations.

Return a task envelope containing task_id, role, objective, inputs,
acceptance_criteria, budget, status, outputs, evidence, blockers, and next_action.
Use the full host protocol for detailed evidence. The lightweight CLI projection
uses shorter fields and states; preserve richer records as artifact sidecars.
Record actual tools and observations, not intended actions presented as completed.

## Acceptance gates

Every proposed citation resolves to inspected content; source identity and entailment are separately assessed. Reported results are distinct from reproduced results.

## Failure and recovery

Inaccessible primary evidence, ambiguous source identity, conflicting versions, or support based only on snippets remains unverified.
Preserve partial artifacts, identify the failed criterion and owner, and return a
concrete next action. Do not conceal uncertainty or manufacture missing evidence.
