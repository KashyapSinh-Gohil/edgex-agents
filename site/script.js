"use strict";

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
      // Use the document copy fallback if clipboard permission is denied.
    }
  }
  const previousFocus = document.activeElement;
  const field = document.createElement("textarea");
  field.value = text;
  field.className = "sr-only";
  field.setAttribute("aria-label", "Installation command to copy");
  document.body.append(field);
  field.focus({ preventScroll: true });
  field.select();
  let copied = false;
  try {
    copied = document.execCommand("copy");
  } finally {
    field.remove();
    previousFocus?.focus({ preventScroll: true });
  }
  if (!copied) throw new Error("Clipboard unavailable");
}

for (const button of document.querySelectorAll("[data-copy]")) {
  const command = document.getElementById(button.dataset.copy);
  const region = button.closest(".install-content, .install-option");
  const status = region?.querySelector(".copy-status");
  if (!command || !status) continue;

  button.hidden = false;
  button.addEventListener("click", async () => {
    const label = button.textContent.trim();
    button.disabled = true;
    if (label !== "Copied") button.textContent = "Copying";
    status.textContent = "Copying command…";
    try {
      await copyText(command.textContent.trim());
      button.textContent = "Copied";
      status.textContent = "Command copied. Paste it into your terminal.";
    } catch {
      button.textContent = label === "Copied" ? "Copy command" : label;
      status.textContent = "Clipboard unavailable. Select and copy the command above manually.";
    } finally {
      button.disabled = false;
    }
  });
}

// Fixed editorial examples, not controller outputs or simulated scientific data.
const scenarios = {
  evidence: {
    meta: "Illustrative / Literature profile",
    title: "A claim has no primary source.",
    observation: "The question is framed, but a key claim rests on a secondary summary. The source milestone is missing.",
    gate: "Search is allowed after framing. Review is unavailable until analysis is recorded.",
    candidates: ["Search for the original study", "Search for a narrower source", "Reframe the question"],
    action: "Dispatch\nthe scout.",
    reason: "Locate the original study and return an excerpt with a section locator. Closing the evidence gap is more useful here than reframing an already specific question.",
    artifact: "A source record and search artifact. An unsuccessful search must still return an artifact.",
    tool: "research_decide → search",
  },
  failure: {
    meta: "Illustrative / Empirical profile",
    title: "The experiment failed to run.",
    observation: "The baseline was built, but execution failed on a mismatched input schema. The failure log is preserved; there is no successful execution milestone.",
    gate: "Build and execute are allowed. Analysis is unavailable until successful execution; downstream review and acceptance must be revisited.",
    candidates: ["Build a corrected input adapter", "Execute again without a repair", "Redesign the experiment"],
    action: "Dispatch\nthe builder.",
    reason: "Repair the concrete schema mismatch and return a new artifact. Repeating the unchanged run would preserve the same failure, while a full redesign is not yet justified by this log.",
    artifact: "A corrected adapter and a repair note at fresh artifact paths. Execute the repaired version in a subsequent step.",
    tool: "research_decide → build",
  },
  review: {
    meta: "Illustrative / Literature profile",
    title: "The draft needs a final claim audit.",
    observation: "Sources, analysis, and a literature draft are recorded. The latest producer output requires review; acceptance criteria are not yet accepted.",
    gate: "Review is allowed after analysis. Completion remains unavailable until required milestones and acceptance criteria are satisfied.",
    candidates: ["Review the draft against criteria", "Analyze the same evidence again", "Search a broader literature scope"],
    action: "Dispatch\nthe referee.",
    reason: "Audit claim-to-evidence links and record criterion-level acceptance or rejection. The outstanding need is substantive review of the current draft, not broader search or repeated analysis.",
    artifact: "A review artifact from an actor label distinct from producers. A successful review may accept specified criteria; completion is a separate action.",
    tool: "research_decide → review",
  },
};

const scenarioSelect = document.getElementById("scenario");
if (scenarioSelect) {
  const controls = scenarioSelect.closest(".trace-controls");
  controls.hidden = false;
  scenarioSelect.addEventListener("change", () => {
    const example = scenarios[scenarioSelect.value];
    if (!example) return;
    for (const key of ["meta", "title", "observation", "gate", "action", "reason", "artifact", "tool"]) {
      const target = key === "artifact" ? "trace-artifact" : `trace-${key}`;
      document.getElementById(target).textContent = example[key];
    }
    const rows = example.candidates.map((candidate, index) => {
      const row = document.createElement("li");
      const label = document.createElement("span");
      label.textContent = `${String(index + 1).padStart(2, "0")} / ${index === 0 ? "Selected" : "Alternative"}`;
      const title = document.createElement("strong");
      title.textContent = candidate;
      row.append(label, title);
      return row;
    });
    document.getElementById("trace-candidates").replaceChildren(...rows);
    document.getElementById("trace-announcement").textContent = `${example.title} ${example.action.replace("\n", " ")} ${example.reason}`;
  });
}
