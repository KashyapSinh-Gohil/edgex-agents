# AntiSlop delivery gate

**Mode:** During build, selected in this session.
**Direction:** ENERGY 3/5, RHYTHM 3/5, MOTION 1/5.
**Evidence boundary:** source review, `node --check`, `git diff --check`, a four-page HTML parser/link audit, contrast calculations, and HTTP 200 responses from the local static server. Work settings disabled browser control during this run, so rendered desktop/mobile review and live click-through could not be performed. The related items below are marked FAIL rather than inferred from source.

## Mandatory rules

- **R-01 PASS:** Black and warm ivory come from the existing EdgeX identity; the rationale is in `DESIGN.md`.
- **R-02 PASS:** UI copy has no em dash. The UI source scan found none.
- **R-03 FAIL:** Responsive CSS includes narrow breakpoints down to 320px, but visual overflow and text wrapping could not be checked at 320px because browser control was disabled.
- **R-04 PASS:** No decorative icon set or generic AI glyphs are used.
- **R-05 PASS:** Four pages separate installation, protocol, and team content; section compositions vary with content.
- **R-06 PASS:** System sans, serif, and monospace stacks have documented roles and do not download fonts.
- **R-07 PASS:** No decorative grid or blueprint background.
- **R-08 PASS:** No decorative arrow buttons. Arrows appear only in the protocol notation that names the selected action.
- **R-09 PASS:** No capsule badges or redundant headline labels.
- **R-10 PASS:** No glassmorphism.
- **R-11 PASS:** No pill-shaped component system; controls retain squared edges.
- **R-12 PASS:** No decorative shadows.
- **R-13 PASS:** No glow effects.
- **R-14 PASS:** Content is arranged as a protocol list and named specialist roster, not repeated generic feature cards.
- **R-15 PASS:** Links name their destination or action.
- **R-16 PASS:** Copy avoids unsupported AI marketing claims.
- **R-17 PASS:** No invented statistics; protocol numbering is structural.
- **R-18 PASS:** No testimonials.
- **R-19 PASS:** No looping or essential motion; reduced-motion support is present.
- **R-20 PASS:** Logo, wordmark, monochrome system, and content-specific research trace give the pages a distinct identity.
- **R-21 PASS:** Dark and ivory surfaces express the established brand; no theme toggle is shipped.
- **R-22 PASS:** No unrelated illustration is used; the supplied brand mark is explicitly requested and identified.
- **R-23 PASS:** Logo and multi-page navigation were explicitly requested; the mark has alt text and intrinsic size.
- **R-24 PASS:** All local navigation targets exist; each page marks its active link.
- **R-25 PASS:** Palette ratios calculated from CSS hex values: ivory on ink 16.26:1; muted ink text 8.70:1; ink on ivory 16.26:1; muted ivory text 6.37:1.
- **R-26 PASS (source review):** Copy controls and the example selector have handlers, including visible clipboard failure guidance. Browser click-through remains unverified under R-35.
- **R-27 PASS (source review):** Copy interactions have copying, success, and unavailable states. No data dashboard or form state is invented.
- **R-28 PASS:** No irrelevant FAQ.
- **R-29 PASS:** Palette uses two neutrals with documented contrast variants.
- **R-30 PASS:** The design uses its own EdgeX identity and does not reproduce another product's site.
- **R-31 PASS:** Major visual decisions and interaction choices are recorded in `DESIGN.md`.
- **R-32 PASS (source review):** Native links, buttons, select, and details controls are keyboard-operable with visible focus styles. Keyboard traversal was not observed live.
- **R-33 PASS:** Files were edited directly; no source-rewriting patch script was introduced.
- **R-34 PASS:** No theme toggle or additional theme is shipped; dark and ivory section treatments are declared in the single palette.
- **R-35 FAIL:** Browser control was disabled by Work settings. I could not record a rendered-page click-through of every interactive element or a visual browser console review.
- **R-36 PASS:** Product and research limitations are stated; no security certification, benchmark, endorsement, or scientific-truth guarantee is claimed.
- **R-37 PASS:** Design direction and all three dials are recorded before completion in `DESIGN.md`.
- **R-38 PASS:** Research examples are visibly labeled illustrative; no fictional people, customers, or live research results appear.
- **R-39 PASS (source review):** Documents declare English, title, landmarks, skip link, named controls, visible focus, hover/active states, image alt text, pointer cursors, and reduced motion. Rendered keyboard use remains unverified under R-35.
- **R-40 PASS (source review):** Images have width and height; the mark is below the fold and lazy-loaded. There is no hero image, external font, third-party blocking script, or reported performance metric. `script.js` is deferred.

## Craftsmanship and UI supplement

- **C-1 PASS:** Design reasons are documented.
- **C-2 FAIL:** Implemented behaviors are present in source, but functional click-through is blocked by disabled browser control.
- **C-3 PASS:** Each page serves a product task: understand, install, inspect the method, or inspect agent roles.
- **C-4 FAIL:** Static source checks pass, but live 320px, desktop, keyboard, and interactive behavior review could not be completed.
- **C-5 PASS:** No testimonial, measured result, endorsement, or scientific correctness claim is presented as fact.
- **Liveliness PASS (source review):** Oversized EdgeX wordmark, asymmetric editorial structure, and the evidence-dependent decision trace create a recognizable composition; a rendered screenshot review is pending.
- **Interactive source inventory:** Copy buttons exist on Home (one command) and Install (three commands). The Method page has one native example selector and one details disclosure. No other page control is interactive.
- **Local delivery check:** All four pages and the logo returned HTTP 200 from the static server. HTML parsing found one title, one H1, header/main/footer landmarks, unique IDs, and no missing relative links per page. JavaScript syntax and whitespace checks passed.

**Gate result: NOT FULLY VERIFIED.** The site is implemented and serves locally, but R-03, R-35, C-2, and C-4 remain blocked on browser access. Re-run the visual and interactive checks after enabling browser control in Work settings.
