# EdgeX-Researcher

Version 0.4 adds a named native agent and an executable decision controller.
Earlier releases primarily packaged skills and a fixed bootstrap loop. This
controller persists and checks the research process while the host model reasons
about the actual question and performs work through its tools and workers.

## Components

- `codex/edgex-researcher.toml`: native Codex custom agent; model and permissions
  inherit from the parent session. The NPX installer places it in the personal
  agents directory, following the [official custom-agent format](https://developers.openai.com/codex/subagents/).
- `agents/edgex-researcher.md`: native Claude-compatible research agent definition.
- `research_controller.py`: persistent state, decisions, observations and gates.
- `mcp_server.py`: four explicit tools over MCP stdio; no provider requests.
- `cli/mcp-launcher.mjs`: finds Python 3.10+ and starts the bundled controller.
- The twelve specialist skills: scientific procedures and evidence requirements.

The agent's reasoning is supplied by the host model, not a separately trained
EdgeX model. A controller cannot manufacture judgment quality by assigning scores.
Its purpose is to make decisions inspectable and enforce the declared process.

## Decision and observation cycle

1. Start with a specific question, measurable criteria, research profile, maximum
   steps and wall time. Persist the generated run ID and revision.
2. Read current observations, unmet milestones, budget and allowed next actions.
3. Propose 2..8 distinct candidate actions with a rationale and existing evidence
   references. Estimate information gain, impact, feasibility, cost and risk in
   [0,1]. These estimates are model judgments, not probabilities or dollar amounts.
4. The controller filters action prerequisites and ranks eligible alternatives by
   `0.4*information_gain + 0.3*impact + 0.2*feasibility - 0.15*cost - 0.25*risk`.
   It commits the selected action, alternative scores and an artifact snapshot.
5. Dispatch the selected role to an actual host worker. Perform the work and
   return real files under the run's artifact directory.
6. Observe the outcome, actor ID, actual findings, new artifact paths and evidence.
   The controller checks revisions, containment and integrity before updating state.
7. Reassess the new evidence. Failed or contradictory results invalidate downstream
   acceptance. Revise the plan, gather discriminating evidence or return a bounded
   continuation rather than repeating an unchanged failed action.

All pending decisions survive restart. A resumed agent must reconcile actual
worker/process status before retrying; the controller does not replay external
side effects. One controller writer per run is protected by an OS lock.

## Enforced gates

| Boundary | Executable rule |
| --- | --- |
| Stale decisions | Supplied revision must equal the persisted revision. |
| Concurrent dispatch | A pending decision must receive an observation before another is committed. |
| Action prerequisites | Framing, evidence, design, implementation and analysis milestones apply by profile. |
| Evidence references | Candidate references resolve to recorded evidence IDs or artifact paths. |
| Literature success | At least one source has an HTTPS URL, excerpt and locator. |
| Actual output | Every outcome includes existing contained artifact files, including failures. |
| Artifact identity | SHA-256 is rechecked on status/decide/observe; prior paths are immutable. |
| Review | Reviewer/replicator label differs from producer labels. Only successful review accepts criteria. |
| New manuscript | Writing invalidates review/criterion acceptance; the final draft needs fresh review. |
| Completion | Required profile milestones and all acceptance criteria must pass. |
| Resources | No new decisions after the step count or wall deadline. |

Empirical work requires implementation, execution and replication. Theoretical
work requires proof/implementation artifacts and independent checking but no
empirical execution milestone. Literature work requires sources, analysis,
review and writing. Every profile requires a final reviewed deliverable.

## State and context

Default storage is `~/.local/share/edgex/research/research_<id>/`:

- `agent.json`: complete canonical decisions, evidence, artifacts and criteria.
- `agent-events.jsonl`: event/revision history.
- `artifacts/`: immutable worker returns.

Status exposes recent decisions/observations and a bounded manifest preview;
bulk history stays on disk. Snapshot replacement is atomic, but snapshot and
event writes are not one database transaction. Actor names are audit labels,
not cryptographically authenticated identities. Distinct labels do not prove
independent model contexts. The host must report actual worker IDs and review coverage.

## What this does not establish

Structural evidence checks cannot establish source entailment, scientific
correctness, originality, statistical validity or lab-equivalent performance.
The controller does not execute a free-form shell action supplied through MCP,
grant host permissions or run an unsupervised background daemon. The host provides
actual execution, source access and scientific reasoning. These boundaries remain
visible in the agent's final report.
