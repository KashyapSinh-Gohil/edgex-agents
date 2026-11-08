EdgeX 0.4.0 adds the named edgex_researcher custom agent and an executable,
persistent research controller exposed through four MCP tools. The controller
compares next-action proposals, enforces prerequisites and revisions, records
immutable artifacts, and invalidates acceptance when results change.

Install account-wide in Codex:

```bash
npx --yes github:KashyapSinh-Gohil/edgex-agents#v0.4.0
```

Then ask: Use the edgex_researcher agent to research [specific question].

The NPX package is distributed directly from GitHub, not the npm registry. It
requires Node 18+, Git, Codex plugin support and Python 3.10+ for the controller.
The host model supplies reasoning and actual workers; no provider API key is
needed by the controller. Distinct actor labels are audit metadata, not proof of
independent review, and structural evidence checks do not establish scientific truth.

Includes a monochrome logo and lightweight GitHub Pages showcase at
https://kashyapsinh-gohil.github.io/edgex-agents/ .

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
