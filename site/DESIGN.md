# EdgeX site design system

## Design read

- **Energy: 3/5.** EdgeX should feel like a serious research instrument: decisive typography, crisp navigation, and direct commands, without promotional spectacle.
- **Rhythm: 3/5.** Pages alternate short editorial statements with detailed, scannable operational content. The four pages give install, protocol, and team information room to breathe.
- **Motion: 1/5.** Movement is limited to subtle focus and hover feedback. No animation is required to understand or use the product.

The existing EdgeX identity sets a monochrome black and warm-ivory palette, oversized system typography, restrained serif italics, and monospace operational labels. This fits a technical research tool and remains legible without downloaded fonts or color-coded claims.

The warm-ivory surfaces use a very low-opacity monochrome grain tile from the Feral UI Lantern collection. The texture gives the paper sections a tactile surface while preserving the existing palette and measured text contrast. The optimized 256px WebP is credited in `ASSET-CREDITS.md`.

## Page structure

- `index.html`: product purpose and primary GitHub NPX command.
- `install.html`: Codex, NPX, and portable setup with copyable commands and prerequisites.
- `method.html`: persistent research protocol, decision policy, and clearly illustrative examples.
- `agents.html`: the named Codex researcher and twelve specialist roles.

Every page shares the same real, keyboard-accessible navigation and footer. The interface uses ordinary links, buttons, select controls, details/summary, and preformatted commands. JavaScript progressively enhances copy feedback and the fixed example selector; content remains readable if JavaScript is unavailable.

## Content integrity

The site describes implemented behavior and its limits. It does not claim scientific truth, zero hallucinations, institutional endorsement, benchmark performance, or unsupervised background work. Example traces are editorial examples, not live controller runs. Candidate scores are host estimates, not probabilities.

## Interaction and responsive rules

- Include a skip link, page-specific title and description, one main heading, visible focus, and `aria-current="page"` on the active navigation link.
- Keep interactive targets at least 44px tall. Use distinct hover, focus, active, and disabled states.
- Reflow navigation and content at narrow widths, including 320px. Preserve readable command wrapping and avoid horizontal page overflow.
- Respect reduced-motion preferences and maintain WCAG AA text contrast for the chosen palette.
- Copy controls report success only after the browser copy operation succeeds, and otherwise provide a manual-copy instruction.

## Identity and type

Use the supplied unmodified transparent black mark on ivory. The wordmark remains text so the product name is available independently of the image. Arial/Helvetica, Georgia, and system monospace are system stacks: no network font fetch is necessary.
