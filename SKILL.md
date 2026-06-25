---
name: autore-codex
description: Use for reverse-engineering challenges and crackmes, including PE/ELF/APK triage, packed or protected binaries, license/login bypass analysis, protocol or auth-chain reconstruction, GUI main-window entry tasks, Frida/x64dbg/IDA workflows, evidence collection, and reproducible RE writeups. Trigger when Codex is asked to analyze an RE problem, compare prior RE methods, coordinate static and dynamic analysis, design hooks/patches/fake responses, or produce a structured writeup.
---

# AutoRE Codex

## Operating Model

Treat every RE task as an evidence-driven workflow with one controller.

Separate work into roles, but keep live target mutation serialized:

- Read-only work may run in parallel when subagents are available.
- Dynamic work must have exactly one controller for the target process, debugger, Frida session, GUI clicks, state cleanup, process killing, patching, and screenshots.
- If subagents are unavailable or inappropriate, simulate the same roles sequentially in the main agent.

For detailed role boundaries, read `references/agent-roles.md`.

## Default Workflow

1. Define the success condition precisely.
   Examples: flag printed, true main program window, specific functional page, decrypted secret, stable authenticated state. Exclude login pages, splash screens, error pages, empty manually constructed containers, and unrelated child modules.

2. Create or reuse a case analysis folder.
   Recommended layout:
   ```text
   <case>analysis/
     code/
     logs/
     screenshots/
     dumps/
     WRITEUP_<case>.md
   ```
   Use `scripts/new_re_case.py` when a clean folder skeleton is useful.

3. Record target identity.
   Include path, size, SHA256, architecture, subsystem, packer/protector clues, launch chain, and child processes.

4. Run static triage.
   Inspect strings, imports, resources, endpoints, UI titles, crypto and JSON helpers, request wrappers, local state paths, anti-debug/date checks, and likely success/failure branches.

5. Run dynamic triage.
   Observe process tree, windows, network/file/registry activity, exceptions, exits, message boxes, and runtime module bases. Keep raw logs.

6. Choose a bypass or reconstruction strategy from evidence.
   Prefer restoring the natural success path over constructing isolated UI objects. Common strategies include fake server responses, request-wrapper hooks, decrypt-result hooks, branch patches, local-state edits, date/anti-debug bypasses, or valid-input reconstruction.

7. Verify with proof.
   Collect logs and screenshots showing the exact success condition. For GUI tasks, record window class, title, PID, visibility, and why it is the real target UI.

8. Write the report.
   Use `references/writeup-template.md` for the final structure.

For a compact task checklist, read `references/case-checklist.md`.

## Subagent Pattern

Use this split for complex tasks:

- Recon: file identity, protection, launch behavior, success condition.
- Static: functions, strings, xrefs, decompiler output, key RVAs.
- Protocol: requests, response schema, crypto, heartbeat, device binding, local state.
- Dynamic: the only live-process controller.
- Patch: hook/patch/fake-data plan based on collected evidence.
- Evidence: screenshot/log/proof validation.
- Writeup: final reproducible report.

Ask for or create subagents only when the current environment supports them. Do not assign live dynamic control to more than one worker.

## Dynamic Safety

Before mutating a live target:

- State which process, file, or local state will be touched.
- Kill only known target/helper processes.
- Back up or clear only known challenge state.
- Keep each run tagged with unique log and screenshot names.
- Avoid combining multiple debuggers or Frida controllers on one target process.
- Prefer staged runs: baseline observation first, then targeted hooks.

## Common Patterns

For license/login GUI challenges:

- Find the request wrapper and decrypt/parse helper.
- Record endpoint order.
- Fake the minimum valid object for each endpoint.
- Keep heartbeat/session hooks alive after success.
- Prove the real main UI, not an empty container or unrelated module.

For packed PE challenges:

- Distinguish outer launcher from unpacked child.
- Use child-gating or attach after child creation.
- Dump runtime modules when disk image RVAs do not match.
- Base final RVAs on the runtime image used by the proof run.

For GUI main-window tasks:

- Record class, title, PID, and screenshot.
- Compare login, splash, child module, empty container, and true main window.
- Prefer natural construction through the program's normal flow.
- Manually call constructors only after proving the natural flow is blocked.

## Output Contract

At completion, provide:

- Final status and whether the success condition was reached.
- Key scripts and commands.
- Logs/screenshots/dumps used as evidence.
- Important addresses and why they matter.
- Remaining risks or unstable parts.
