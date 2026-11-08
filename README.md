# EdgeX Agents

An open-source research team for Codex, Claude Code, Cursor, VS Code Copilot,
and agents that can read Markdown instructions. One entry skill and twelve specialist skills,
research protocols, persistent handoffs, context packets, and an evidence ledger.

**Version 0.4.0: named research agent with a persistent decision controller.** The host provides
models and tools. Installing skills does not train a model or establish research
accuracy. EdgeX has no affiliation with or endorsement from any AI laboratory.

## Install the whole team

### One-command native research agent

```bash
npx --yes github:KashyapSinh-Gohil/edgex-agents#v0.4.0
```

Requires Node 18+, Git, Codex with plugin support, and Python 3.10+ for the
controller. This is an NPX package distributed from GitHub, not a published npm
registry name. It installs the native plugin and the personal custom agent
`edgex_researcher` under `~/.codex/agents/`. Existing modified files are preserved.
Use `--dry-run` to inspect installation first.

Start a new chat and ask:

> Use the edgex_researcher agent to research [specific question]. Compare next actions,
> preserve evidence and continue until the acceptance criteria or budget is reached.

[Website](https://kashyapsinh-gohil.github.io/edgex-agents/) ·
[Research controller](docs/RESEARCHER.md) · [Source and releases](https://github.com/KashyapSinh-Gohil/edgex-agents/releases)

### Native Codex plugin (account-wide)

Install once, then use EdgeX across projects, like other installed Codex plugins:

```bash
codex plugin marketplace add https://github.com/KashyapSinh-Gohil/edgex-agents.git && codex plugin add edgex@edgex-agents
```

Start a new turn/session so the host discovers the plugin's skills. Say
`Use EdgeX to research [topic]`, or explicitly request the `edgex` skill
(namespaced as `edgex:edgex` where the host displays plugin namespaces).
The entry skill chooses research, review, writing, or resume from the request,
then loads only relevant specialists. Existing task authorization remains in effect.

The native plugin starts its bundled MCP controller through Node and Python.
The host's existing model supplies reasoning and native workers; the controller
needs no provider API key. Installing the plugin alone loads the skills and tools;
the NPX installer also installs the named Codex custom agent. Research progresses
while the host agent is running, and its state survives host/session restarts.

### Native Claude Code plugin

```bash
claude plugin marketplace add KashyapSinh-Gohil/edgex-agents
claude plugin install edgex@edgex-agents
```

The manifest includes thirteen skills, twelve specialist agents and the research agent.
Native Cursor plugin/marketplace manifests are also included; use Cursor's plugin
installation flow for this repository. Codex installation is verified with its CLI;
Claude manifests are validated, while live execution in other hosts depends on
the installed host version.

### Portable project installation

Run inside the project where you want the agents available. Requires [uv](https://docs.astral.sh/uv/),
Git, and Python 3.10+. `uvx` runs the CLI in an isolated environment.

```bash
uvx --from "git+https://github.com/KashyapSinh-Gohil/edgex-agents.git@v0.4.0" edgex install --target all --project .
```

Choose `--target codex`, `claude`, `cursor`, `copilot`, or `generic` for one host.
Add `--dry-run` to preview. Installation is project-local, detects modified files,
and preserves existing agent configuration. It never configures credentials.

Alternatively, install the CLI in a Python virtual environment:

```bash
python -m pip install "git+https://github.com/KashyapSinh-Gohil/edgex-agents.git@v0.4.0"
edgex install --target all --project .
```

| Host | Installed integration | How to start |
|---|---|---|
| Codex | `.agents/skills/edgex-*/SKILL.md` | Ask to use `edgex-orchestrator` |
| Claude Code | `.claude/skills/` and native `.claude/agents/edgex-*.md` | Reload the host and request EdgeX delegation |
| Cursor | `.cursor/skills/` | Request `edgex-orchestrator` in agent mode |
| VS Code with Copilot | `.github/skills/` | Use Agent Skills in a supported Copilot version |
| Other hosts / Antigravity | `.edgex/skills/` and `EDGE-X.md` | Attach/read `EDGE-X.md`; discovery depends on the host |

File formats follow the [Agent Skills specification](https://agentskills.io/specification),
[Claude subagent docs](https://code.claude.com/docs/en/sub-agents), and
[VS Code skills docs](https://code.visualstudio.com/docs/agent-customization/agent-skills).
Integrations are verified as installed files and package resources; live behavior
in every host/version is not benchmarked. Hosts with native delegation can spawn
workers. Other hosts follow the roles sequentially and must say so.

## Ask the team to work

```text
Use edgex_researcher and delegate to the relevant EdgeX specialists.
Research whether [specific intervention] improves [metric] on [fixed benchmark].
Set a 2-hour / 20-call budget. First record the hypothesis, baseline, splits,
failure criteria, and replication plan. Keep original evidence and artifacts.
Use independent review. Return a reproducible research bundle and a draft with
claim-to-evidence links, limitations, and machine-assistance disclosure.
```

| Role | Responsibility and deliverable |
|---|---|
| Orchestrator | Task graph, budgets, acceptance criteria, and next actions |
| Scout | Search log, primary sources, located evidence, contradictions |
| Architect | Falsifiable hypotheses, alternatives, preregistered experiments |
| Builder | Runnable baseline and intervention with fixed evaluation contract |
| Executor | Controlled run, environment, raw logs, hashed output artifacts |
| Statistician | Effect sizes, uncertainty, multiplicity and leakage assessment |
| Mathematician | Definitions, assumptions, derivations, edge cases, proof gaps |
| Domain scientist | Domain validity, applicable models and limitations |
| Referee | Independent claim audit, counterexamples, acceptance reasons |
| Scribe | Evidence-linked draft, bibliography, limitations and disclosure |
| Context manager | Bounded context and source-preserving resume handoffs |
| Reproducibility | Clean rerun instructions, environment/data/code provenance |

The separate `edgex` entry skill routes requests to this team; it is not an
additional research worker. Native plugin manifests and Python wheels point to
the same canonical skill files, keeping protocol versions consistent.

Domain guidance covers AI, ML, deep learning, programming, mathematics, physics,
chemistry, biology, quantum technology, and space. Instructions express verification
requirements; they do not imply lab access or qualified expert validation. See
[research standards](docs/RESEARCH_STANDARDS.md) and [protocol](docs/PROTOCOL.md).

## Runtime and long tasks

The native research agent uses executable controller tools: `research_start`,
`research_status`, `research_decide` and `research_observe`. It compares 2..8
candidate actions, commits a decision, records actual work and replans. Revisions,
prerequisites, immutable artifacts, distinct reviewer labels, step budgets and
wall-clock budgets are enforced in code. The controller cannot verify semantic
truth or authenticate a self-reported worker identity. See [the precise contract](docs/RESEARCHER.md).

The following commands are the **legacy bootstrap/task toolkit**, retained for
compatibility; `edgex run` is not the new research controller:

The CLI persists research state and task handoffs. Host agents perform specialist
work; `edgex run` itself is a literature/hypothesis/draft bootstrap, not a scheduler
that autonomously spawns twelve model workers.

```bash
edgex init "Reliable AI research agents" --question "Does evidence review reduce unsupported claims?" --run-dir runs/research
edgex run runs/research --iterations 2 --offline
edgex status runs/research
edgex context runs/research --max-chars 12000
edgex paper runs/research --offline
edgex validate runs/research
```

Offline mode makes no model or literature-network calls. Networked mode retrieves
Semantic Scholar/arXiv metadata; set `OPENAI_API_KEY`, `EDGEX_MODEL`, and optionally
`OPENAI_BASE_URL` for the optional OpenAI-compatible manuscript backend. The CLI
has zero runtime Python dependencies. Model access and compute are supplied
separately. Model failure is recorded and a deterministic draft is used.

`state.json` holds canonical evidence, claims, hypotheses, tasks, and the search
tree; `events.jsonl` records progress; `artifacts/` holds worker outputs. Repeating
`run` resumes an existing run. The CLI takes an OS coordinator lock. Use the same
lock for direct library writes; the coordinator alone updates shared state.
Snapshots use atomic replacement; snapshot and event writes are not a database
transaction. Budgets stop new iterations; in-flight calls have their own timeouts.

```bash
edgex task runs/research add scout "Locate primary evidence" --accept "Return a sourced excerpt with section locator"
edgex task runs/research list
edgex task runs/research claim TASK_ID --owner scout-1 --lease-seconds 1800
# Worker writes findings.md under runs/research/artifacts/.
edgex task runs/research finish TASK_ID --owner scout-1 --output findings.md --evidence SOURCE_ID
edgex task runs/research review TASK_ID --reviewer referee-1 --accept --reason "Checked the primary source against acceptance criteria"
```

Tasks move through `queued → running → review → completed`, with `blocked` and
rejected-review recovery. Expired leases can be reclaimed within an attempt budget.
A different reviewer label is required and artifact hashes are checked again at
acceptance. Labels are audit metadata, not authenticated identities. Context packets
have a character budget and retain pointers to canonical records and original evidence.

## Scientific claims and standards

The evidence gate checks located excerpts, support links, provenance, and reviewer
metadata. A title, URL, or successful process exit alone cannot support a scientific
claim. No claims assessed produces `NOT READY`. A passing structural check is not
proof that the source entails the claim. Prose always remains a draft, and generated
prose is not automatically checked for every new claim it might introduce.

Standards map public guidance from NIST, Google DeepMind, OpenAI, Anthropic, Meta,
xAI, and Scale to review practices. This is a design mapping, not certification,
regulatory advice, or a copy of private lab procedures. See the standards document
for sources and implementation limits.

## Architecture and upstream research

EdgeX takes architectural inspiration from [AIDE ML](https://github.com/WecoAI/aideml)
(executable candidates and metric-guided search),
[AI Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) (staged research and
manuscripts), and [EvoMaster](https://arxiv.org/html/2604.17406v1) (modular research
harnesses). Search primitives provide candidate selection and score propagation;
the bootstrap does not perform automatic model-written experiment search. Host
workers can follow the protocols to carry out that work.

Upstream repositories were cloned locally for inspection and are excluded from
the published package. Their source is neither bundled nor invoked by this runtime.
See [THIRD_PARTY.md](THIRD_PARTY.md) for exact commits and license boundaries.

## Develop and verify

```bash
git clone https://github.com/KashyapSinh-Gohil/edgex-agents.git
cd edgex-agents
python -m venv .venv
# Activate the environment for your shell, then:
python -m pip install -e '.[dev]'
python -m pytest -q
```

Tests cover evidence downgrades, empty evidence, dependencies, expired lease recovery,
retry budgets, artifact tampering, bounded context, and installer conflicts. CI
exercises Python 3.10/3.12 on Linux, Windows, and macOS and installs a built wheel.
See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

MIT-licensed EdgeX code and instructions. External models, datasets, tools, and
optional upstream checkouts retain their own terms.
