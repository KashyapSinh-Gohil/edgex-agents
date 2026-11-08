# Third-party provenance

The following repositories were downloaded into `upstream/` for inspection and architectural reference:

| Project | URL | Commit | License note |
|---|---|---|---|
| AIDE ML | https://github.com/WecoAI/aideml | `ad73d227af481bea3de06f884f41b2993dd6453a` | MIT License |
| AI Scientist-v2 | https://github.com/SakanaAI/AI-Scientist-v2 | `96bd51617cfdbb494a9fc283af00fe090edfae48` | The AI Scientist Source Code License 1.0 |

EdgeX does not vendor source files from either project. It implements an independent orchestration layer using the following ideas observed in the repositories:

- AIDE: executable solution nodes, metric feedback, journal persistence, and tree-search improvement.
- AI Scientist-v2: staged progression, experiment-manager state, Semantic Scholar tool usage, plot/result review, and paper-generation guardrails.

The local `upstream/` directory is excluded from Git, wheels, and source distributions.
EdgeX does not import or invoke either upstream runtime. The MIT license applies
to independently authored EdgeX files only. Anyone distributing or executing
upstream code must review its own license.

The supplied Medium ASR article is secondary commentary. The Intology Zochi page
returned no readable article text during inspection, so no performance or design
claims were derived from it. EvoMaster (https://arxiv.org/html/2604.17406v1) was
read as architectural background; its authors' benchmark results do not establish
EdgeX performance.
