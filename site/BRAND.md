# EdgeX website identity

## Reusable design prompt

Create a lightweight, multi-page editorial showcase for EdgeX, a host-powered persistent research controller and the native Codex custom agent `edgex_researcher`. The central message is “Research that knows its next step.” Explain the real loop: the host supplies models, tools, and permissions; EdgeX preserves run IDs, revisions, decisions, observations, evidence, and artifact records.

Use black and warm ivory, oversized system typography, asymmetric columns, fine rules, small monospace annotations, and generous whitespace. Let product information shape the layout rather than using a generic feature-card grid. The existing EdgeX identity is intentionally monochrome and restrained because this is research infrastructure; motion is limited to practical interaction feedback. Add the optimized low-opacity grayscale Feral UI Lantern grain tile to ivory surfaces for a tactile paper finish; see `ASSET-CREDITS.md` for its source and terms.

Use the plain text EdgeX wordmark without a registration symbol. Display the supplied transparent black mark at `assets/edgex-mark.png` on ivory, at its natural proportions. Text must identify the product independently of the image.

Make four directly linked pages: Home, Install, Method, and Agents. Keep the primary GitHub NPX command easy to find and copy:

```sh
npx --yes github:KashyapSinh-Gohil/edgex-agents#v0.4.0
```

Identify this as a GitHub-distributed NPX package, not an npm registry package. Explain that it installs the EdgeX plugin with MCP tools and `~/.codex/agents/edgex-researcher.toml`. State Python 3.10+, Node 18+, Git, and Codex as prerequisites. Portable installation additionally needs uv. The host provides model access; no separate API key is needed for this setup.

Describe `research_start`, `research_status`, `research_decide`, and `research_observe`. Compare 2–8 distinct host-proposed candidates under prerequisites. Explain that estimated information gain, impact, feasibility, cost, and risk are host judgments, not scientific confidence. Show three explicitly illustrative decision traces: evidence gap → scout/search, failed experiment → builder/repair, final review → referee/review. State that examples do not call MCP tools.

List the twelve specialist roles and their actual responsibilities: orchestrator, scout, architect, builder, executor, statistician, mathematician, domain scientist, referee, scribe, context manager, and reproducibility. Distinguish host delegation from sequential role passes. Structural validation, artifact hashes, and reviewer labels do not establish scientific truth. Do not invent benchmarks, endorsements, customer logos, lab equivalence, or accuracy claims.

Use static HTML, CSS, and vanilla JavaScript, with relative paths that work on GitHub Pages under `/edgex-agents/`. Add no frameworks, build dependencies, external fonts, icon libraries, analytics, or application network calls. Support a 320px viewport, visible keyboard focus, reduced motion, accessible copy feedback, and readable content with JavaScript disabled. Link to `https://github.com/KashyapSinh-Gohil/edgex-agents`.

## Design dials

- **Energy 3/5:** decisive headings and clear actions, without promotional spectacle.
- **Rhythm 3/5:** concise editorial framing followed by detailed, scannable operational content.
- **Motion 1/5:** subtle hover and focus feedback only; animation adds no essential information.

## Design rationale

- The oversized wordmark gives the project a recognizable identity; the adjacent headline explains its purpose.
- Narrow index columns establish rhythm while wider columns hold explanations and commands.
- Ivory marks practical entry points. The research method returns to black, with an ivory surface for the selected example action.
- Arial/Helvetica provides a familiar utilitarian voice, Georgia adds restrained contrast, and system monospace marks tools and operational detail. No font download is required.
- The illustrative trace is separate from actual execution. Candidate estimates are separate from scientific confidence. Persistent state is separate from scientific validation.
- Copy controls and the scenario selector progressively enhance semantic HTML. Commands and the first example remain available without scripts.

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| Ink | `#111110` | Main background and text on ivory |
| Ivory | `#f0eee6` | Main text and paper sections |
| Muted on ink | `#b2b0a8` | Supporting copy |
| Muted on ivory | `#56564f` | Supporting copy |
| Rule on ink | `#45453e` | Editorial separators |
| Rule on ivory | `#bdbbb2` | Editorial separators |
| Sans | Arial, Helvetica, sans-serif | Titles and body |
| Serif | Georgia, Times New Roman, serif | Selected italic phrases |
| Mono | SFMono-Regular, Consolas, Liberation Mono | Labels and commands |
