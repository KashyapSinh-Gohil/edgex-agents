# Security and trust boundaries

Do not post credentials or private data in public issues. For a vulnerability use
GitHub's private vulnerability reporting if enabled, or contact the repository
owner through their GitHub profile before disclosing exploit details.

Skills are instructions interpreted by the host agent; they cannot enforce host
permissions. External pages, datasets, tool output, and returned worker content
are untrusted data and must not override task authority or instructions.

The installer uses project scope, conflict preflight, and a managed-file manifest.
It never installs API keys or changes global agent configuration. Run model-written
experiments in a container or VM with an explicit resource and network policy.
The subprocess executor provides deadlines and a reduced environment, not isolation.

Task owner/reviewer names are audit labels, not authenticated identities. Run-state
JSON and hash records are local integrity aids, not tamper-proof evidence. The
evidence gate checks structural provenance; semantic verification remains a research
review responsibility. Do not expose the CLI as an untrusted multi-user service.
