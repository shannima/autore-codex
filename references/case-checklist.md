# RE Case Checklist

Use this checklist to keep RE cases reproducible.

## Identity

- Target path
- File size
- SHA256
- Architecture and subsystem
- Packed/protected indicators
- Outer launcher vs child process
- Runtime module base and dumped image if needed

## Success Condition

- Exact target state
- False positives to reject
- Required screenshot/output/log proof
- Stability requirement

## Static Triage

- Strings and resources
- Imports and delay imports
- Network endpoints and HTTP paths
- JSON/cJSON/parser helpers
- Crypto/decrypt/hash/signature helpers
- Login/license/state functions
- UI titles, constructors, and factory functions
- Date checks and anti-debug checks
- Local files, registry keys, mutexes, services

## Dynamic Triage

- Process tree and child creation
- Window classes/titles
- Message boxes
- Network requests and responses
- File/registry state changes
- Exceptions and exit paths
- Thread/context of key calls
- Runtime RVAs vs disk RVAs

## Strategy Selection

- Valid input reconstruction
- Fake server or fake response
- Request-wrapper hook
- Decrypt-result hook
- Branch patch
- Local-state patch
- Date/anti-debug bypass
- Manual constructor call only if natural flow is blocked

## GUI Proof

- PID
- Window class
- Window title
- Visibility
- Screenshot
- Reason it is the real main UI
- Reason rejected windows are not enough

## Writeup Artifacts

- Scripts
- Logs
- Screenshots
- Dumps
- Commands
- Key addresses
- Final reproduction path
- Remaining caveats

## Resume And Handoff

- `case.json` target identity still matches the analyzed binary
- `STATE.md` records current controller, failed hypotheses and next action
- Each proof belongs to an identified run, target/module hash and PID when relevant
- Findings cite existing Evidence IDs; hypotheses remain labeled
- `case_evidence.py check <case-root> --strict` result is recorded
- Original files/state and specific rollback steps are preserved
- Clean-baseline reproduction is run, or explicitly marked not run with a reason
- Integrity checks are not substituted for proof of the requested behavior
