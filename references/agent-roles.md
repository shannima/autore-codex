# RE Agent Roles

Use these roles to divide a reverse-engineering task. Treat them as responsibilities, not necessarily separate processes.

## Main Controller

- Own the case goal, plan, and final decision.
- Decide which work can be parallelized.
- Keep the single source of truth for target path, hashes, logs, screenshots, and success criteria.
- Own all live dynamic execution unless explicitly delegating it to one Dynamic worker.

## Recon

- Identify file type, architecture, subsystem, imports, signatures, packer/protector clues, and launch behavior.
- Record target path, size, SHA256, and environment assumptions.
- Identify the likely success condition and false positives.

## Static

- Inspect strings, imports, resources, xrefs, functions, and decompiler output.
- Locate request wrappers, JSON helpers, crypto/decrypt routines, UI constructors, branch checks, local-state paths, anti-debug/date checks, and error handlers.
- Produce candidate addresses with confidence and evidence.

## Protocol

- Reconstruct auth or network flows, request order, parameters, response schema, signatures, encryption/decryption, heartbeat, device binding, and local cache/state.
- Compare with prior cases when available.
- Propose minimum fake objects or local state needed to satisfy checks.

## Dynamic

- Be the only role that runs or mutates the live target.
- Launch, attach, click UI, set breakpoints, hook Frida, operate x64dbg, clear local state, kill target/helper processes, and collect runtime logs.
- Tag every run with unique names.
- Preserve evidence before changing strategy.

## Patch

- Convert evidence into a bypass plan.
- Prefer high-level hooks over brittle branch patches when structure is understood.
- Prefer natural program flow over manual UI construction.
- Document each patch or hook with address, condition, expected effect, and rollback risk.

## Evidence

- Verify the result against the exact success condition.
- For GUI tasks, record PID, class, title, visibility, screenshot, and why it is not a false-positive page.
- For flag/algorithm tasks, record inputs, outputs, and reproduction command.
- For long-running auth bypasses, verify heartbeat/session stability.

## Writeup

- Produce a reproducible report.
- Include failed paths only when they explain the final method or prevent future mistakes.
- Link scripts, logs, screenshots, hashes, and key addresses.

## Parallelization Rules

- Safe to parallelize: static read-only analysis, historical writeup comparison, log review, protocol schema reading, offline dump inspection.
- Do not parallelize: running the same sample, attaching debugger/Frida, GUI clicking, clearing state, killing processes, modifying target files, writing final patches.
- If a subagent asks to perform live dynamic work while another controller is active, stop and reassign the task.

## Handoff Contract

Read-only workers return a compact packet: assigned question, target/module hash,
observed facts with artifact paths or Evidence IDs, hypotheses, failed attempts,
and the next proposed action. An address must state whether it is VA, RVA, or a
file offset and identify the image it belongs to.

Workers write separate scratch artifacts. The main controller alone merges
`case.json`, `evidence.json`, `STATE.md`, and the final report; evidence registration
is single-writer, not a concurrent append service.

To transfer live control, the old controller first stops issuing commands and
records PID, active debugger/hook sessions, outstanding breakpoints, modified
state, latest run ID and recovery steps. The new controller acknowledges the
handoff before acting. If session ownership is uncertain, inspect it before
attaching again. Do not infer that a timed-out worker released the target.
