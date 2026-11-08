EdgeX Agents 0.3.0 adds native Codex, Claude Code, and Cursor plugin manifests and
marketplace catalogs. The new edgex entry skill routes requests to twelve research
specialists using the host's model, tools and subagents.

Install account-wide in Codex:

```bash
codex plugin marketplace add https://github.com/KashyapSinh-Gohil/edgex-agents.git && codex plugin add edgex@edgex-agents
```

Then ask: Use EdgeX to research [topic].

Includes the portable project-local installer, native Claude subagent definitions, domain
research protocols, evidence and review gates, persistent task leases, bounded
resume context, offline drafts, and reproducibility guidance. MIT licensed.

Requires Python 3.10+. Install in a project using the one-line command in README.
Host agents supply the actual models and delegated workers. The included Python
research bootstrap is not an autonomous twelve-worker scheduler. Structural
evidence validation does not establish semantic truth or scientific novelty.

Public guidance from NIST and named AI labs informs the documented standards;
EdgeX does not claim lab affiliation, endorsement, private-practice equivalence,
certification, or measured PhD-level research performance.
