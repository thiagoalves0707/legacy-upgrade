# Legacy upgrade rules (condensed)

Use these rules for any task that upgrades a runtime, framework or dependency
version, or modernizes legacy code. If the full `legacy-upgrade` skill folder is
available in the repo (e.g. `.claude/skills/legacy-upgrade/` or `tools/legacy-upgrade/`),
read its `SKILL.md` and the matching `references/ecosystems/*.md` file first.

**Core principle: green tests are not proof.** Prove behavior was preserved, and
state clearly what you could not prove.

## Mode
State your mode first: A = you can run commands (do everything), B = you can edit
but not run (give exact commands, ask for output), C = chat only (plan and checklists).
If the project runs in Docker/devcontainer, run commands inside it.

## Rules
1. Snapshot current behavior **before** changing any version (API responses, CLI outputs, schema dumps, report files). Run the snapshot twice on the unchanged app to find non-deterministic fields.
2. One hop at a time: one runtime OR framework OR major dependency bump per step. Never skip several majors.
3. Every hop ends green: build, tests, snapshot comparison against the ORIGINAL baseline, app boots.
4. Never weaken or delete a test to make it pass. Log any necessary test change with reason.
5. Log every workaround in a ledger: pins, patches, silenced warnings, legacy flags, skipped tests, old framework defaults kept.
6. Do not invent versions, APIs or flags. Check the registry, changelog and official upgrade guide.
7. Fix deprecation warnings of the current version before bumping.
8. Commit once per hop on a branch.
9. Ask before irreversible actions (real-data migrations, deletes, force pushes, prod config).
10. If a hop keeps failing, stop and ask instead of stacking workarounds.
11. Never say "done". Finish with `MIGRATION_REPORT.md`: hops, final versions, tests, snapshot diffs, workaround ledger, accepted differences, what was not verified, and a human end-to-end verification checklist. Status: "Ready for human verification".

## Phases
0 Scope (targets, reasons, constraints, target still supported?) -> 1 Inventory (versions, outdated, audit, risky deps) -> 2 Baseline (run as-is, tests, deprecation log, behavior snapshots, characterization tests for untested critical paths) -> 3 Plan the hop path (compatibility matrix, silent behavior changes per hop, get OK) -> 4 Execute hop by hop -> 5 Verify (full suite, snapshots vs original baseline, audit, prod-like boot) -> 6 Report.

## Watch for silent changes
Framework default flags, date/time zone handling, JSON serialization of dates and
decimals, locale/number formatting, string comparison and sorting stability, charset
defaults, cookie/session/encryption formats, routing (trailing slashes), ORM
query translation, removed stdlib modules.
