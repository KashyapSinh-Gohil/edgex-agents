# EdgeX research standards

Version 1.0, reviewed 8 November 2026. These are EdgeX's operating requirements,
informed by published primary material. They are not private laboratory procedures,
endorsements, certification, or a legal compliance determination.

## Source mapping and limits

| Public source | Published subject | EdgeX design decision |
| --- | --- | --- |
| [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) and [GenAI profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | Voluntary risk management and GenAI considerations | Record scope, accountable owners, evaluations, findings, and dispositions. |
| [Google DeepMind frontier safety](https://deepmind.google/frontier-safety/) | Capability evaluation and mitigation | Explicit evaluation plans, threshold-based local decisions, and qualified review where required. |
| [OpenAI Frontier Governance Framework](https://openai.com/index/openai-frontier-governance-framework/) | Risk assessment, reporting, external input, and governance | Keep incident records, review independence, limitations, and release evidence. |
| [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) and [long-running harnesses](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | Context curation, compaction, durable notes and incremental progress | Persist canonical state and bounded resume packets; retain evidence outside working context. |
| [Meta Developer Use Guide](https://dev.meta.ai/developer-use-guide) | Responsible LLM development and agent considerations | Document intended use, system boundaries, evaluations, and deployment limitations. |
| [xAI safety](https://x.ai/safety) | Lifecycle evaluations, model cards and transparency | Version model/system configurations and expose tested capabilities and limitations. |
| [Scale Labs](https://scale.com/blog/scale-labs) | Benchmarking, evaluation and alignment research | Separate system performance from model performance and specify grading methodology. |
| [Agent Skills specification](https://agentskills.io/specification) | Portable skill packaging | Ship named SKILL.md entry points and self-contained references. |

These sources support the stated general design motivations, not a claim that each
organization uses EdgeX's twelve roles, JSON contract, hash policy, or exact gates.
Frontier-model frameworks and deployment regulations have different scopes from a
research toolkit. Applicability must be assessed for the actual system and use.
Revisit sources when versions or intended uses change.

## Required research records

1. **Question and hypothesis:** explicit population/system, assumptions, alternatives,
   falsifying observations, desired deliverables, and stopping conditions.
2. **Evidence:** source identity/version/access status, exact excerpt and locator,
   provenance and opposing findings. Citation existence and entailment are distinct.
3. **Design:** fixed baseline/intervention, controls, endpoints, independent units,
   exclusions, split/seed policy, selection rule, resource matching and analysis plan.
4. **Execution:** code/config/data/environment identities, actual commands, measured
   outcomes, exit dispositions, raw logs, and all unsuccessful attempts.
5. **Analysis:** effect size and uncertainty, assumptions, multiplicity/selection
   handling, relevant sensitivities, domain validity and interpretation boundaries.
6. **Review:** distinct producer/reviewer contexts where available, inspected methods,
   immutable artifact hashes, per-criterion verdicts and required repairs.
7. **Reporting:** claim-to-evidence links, negative results, verified references,
   limitations, machine-assistance disclosure, and reproduction instructions.

## Acceptance gates

| Gate | Evidence required | On failure |
| --- | --- | --- |
| Scope | Current authorization and bounded task contract | Pause affected action; preserve useful authorized work. |
| Provenance | Resolvable sources/artifacts and exact locators | Keep claims unverified. |
| Correctness | Domain-appropriate tests, derivations or reference cases | Repair before expensive experiments. |
| Evaluation | Frozen endpoints and uncontaminated comparisons | Redesign or explicitly limit conclusions. |
| Statistical validity | Appropriate independent units and uncertainty | Mark inference inconclusive if unsupported. |
| Independent review | Recorded reviewer coverage and immutable outputs | Keep required review open; self-review is labeled. |
| Reproducibility | Actual clean rerun within stated tolerance, where claimed | Report reproduction as unperformed or failed. |
| Manuscript | Audited central claims, citations, tables and disclosure | Keep draft provisional. |

An honest null result can pass an investigation's acceptance criteria while
rejecting its scientific hypothesis. No gate turns confidence or model agreement
into evidence. Artifact hashes establish byte identity rather than correctness.

## Domain standards

Each installed skill bundles the complete [domain requirements](../src/edgex/assets/skills/edgex-domain-scientist/references/domains.md).

- **AI/ML:** data/model versions; leakage and contamination checks; suitable baselines;
  tuning/selection transparency; held-out evaluation; distribution-specific claims.
- **Deep learning:** architecture/weights/tokenizer identity; precision and hardware;
  gradient/loss checks; checkpoint/random state; matched data and compute.
- **Programming:** behavioral contracts; meaningful boundary tests; failure/cancellation
  and concurrency semantics; dependency, performance and security assumptions.
- **Mathematics:** quantified definitions; complete derivations; theorem applicability;
  degenerate cases and counterexamples; symbolic/formal checks accurately labeled.
- **Physics:** regime, governing equations, dimensions, approximations, conservation,
  boundary conditions, numerical convergence and observational uncertainty.
- **Chemistry:** species/charge/spin, stoichiometry, phase and standard states;
  method/basis/solvation, convergence and thermodynamic/kinetic distinction.
- **Biology:** biological replicate units, controls, batch/confounding, reference
  assemblies/annotations, cohort provenance and association/causation distinction.
- **Quantum:** valid states/operators/channels; basis conventions; shots/noise;
  preparation/measurement costs; simulation versus hardware; classical comparison.
- **Space:** reference frames and time scales/epochs; ephemeris/calibration versions;
  dynamical assumptions, convergence, covariance and observation selection effects.

Cross-domain projects satisfy every relevant domain requirement. Computational
authorization does not imply wet-lab, clinical, spacecraft or other operational authority.

## Long-horizon operation and implementation boundaries

Use one coordinator, bounded task leases/retries, explicit dependencies, immutable
worker outputs and review before acceptance. Preserve source records and failed
attempts. Checkpoint constraints, decisions, spending, running processes, blockers
and next actions before context resets. Resume by checking current state and
artifact identity rather than assuming old running records remain accurate.

The Python CLI enforces task ownership labels, lease timing, attempt ceilings,
dependencies, artifact containment/hashes and a distinct reviewer label. Labels
are not authenticated identities. Its evidence gate checks provenance structure;
source entailment, statistical correctness, originality and prose accuracy need
actual specialist review. Host skills specify richer records and budgets than the
runtime enforces; see the [runtime projection](PROTOCOL.md#10-runtime-projection-and-host-enforcement).

Maintain an evaluation report naming task distribution, dataset versions, baseline,
host/model/tools, resources, graders, independent review, failures and uncertainty
before claiming performance improvements. EdgeX currently reports software tests,
not scientific benchmark scores or measured equivalence to expert researchers.

## Governance and release

Version protocol changes, preserve review history, and rerun affected evaluations.
Document incidents such as corrupted artifacts, data leaks, fabricated evidence
or invalid conclusions with scope, affected outputs, owner, remediation and checks.
Withdraw dependent conclusions pending repair. Follow current user authorization
for public release, and verify artifact/data/model licenses for the actual bundle.
Do not claim compliance with a jurisdiction or standard merely because its name
appears in these instructions.
