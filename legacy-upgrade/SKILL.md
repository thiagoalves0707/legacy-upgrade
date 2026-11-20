---
name: legacy-upgrade
description: Safely upgrade legacy codebases in any language - runtime, framework and dependency version bumps (e.g. Rails 5 to 7, Python 2 to 3, Django 1.x to 5, Java 8 to 21, Spring Boot 2 to 3, Node 12 to 22, .NET Framework to modern .NET, PHP 7 to 8, Go and Rust toolchain/edition bumps). Use when the user asks to upgrade, migrate, modernize or update an old project, move off an end-of-life runtime, fix outdated or vulnerable dependencies, or verify that an upgrade really preserved behavior beyond "the tests pass". Enforces behavior snapshots before any change, one-hop-at-a-time upgrades, a workaround ledger, and a human sign-off checklist.
---

# Legacy Upgrade

**Core principle: green tests are not proof.** Legacy test suites are often thin,
outdated, or assert the bug. Your job is to *prove* that behavior was preserved,
and to be explicit about everything you could not prove. An upgrade that "passes"
while silently returning different data is worse than one that fails loudly.

## 1. Pick an operating mode first

Decide which mode you are in and say so in your first message. Do not assume a
specific editor or IDE: use whatever file and terminal tools the host gives you.

| Mode | When | How you work |
|---|---|---|
| **A - Autonomous** | You can run shell commands | Execute every phase yourself. |
| **B - Assisted** | You can read/edit files but cannot run commands (or each run needs manual approval) | Give the exact commands, ask the user to paste the output, continue from it. Batch commands to save round trips. |
| **C - Advisory** | Chat only, no repository access | Ask for the manifest, lockfile, runtime version and CI config. Produce the plan, the risk list and the checklists. |

If the project runs in Docker, docker-compose or a devcontainer, run every command
**inside** that environment, not on the host.

## 2. Non-negotiable rules

1. **Snapshot before you touch.** Record the current behavior (Phase 2) before changing any version.
2. **One hop at a time.** Never jump several majors at once. One runtime *or* framework *or* major dependency bump per hop.
3. **Every hop ends green:** builds, tests pass, snapshots match, app boots. Do not start the next hop on a red state.
4. **Never weaken a test to make it pass.** If a test must change (it asserted an old-version artifact), log it in the ledger with before/after and the reason.
5. **Every workaround goes in the ledger.** Pins, monkey patches, silenced warnings, `--legacy-peer-deps`, `--add-opens`, skipped tests, disabled linters, compatibility shims, old framework defaults kept on. Nothing is hidden.
6. **Do not invent versions, APIs or flags.** Check the real package registry, changelog and official upgrade guide. If you are offline or unsure, say so and ask.
7. **Never declare the job "done".** The final state is "ready for human verification", with the checklist from Phase 6.
8. **Work on a branch and commit once per hop** (if the project uses version control), so any hop can be reverted or bisected.
9. **Ask before irreversible actions:** migrations on real data, deleting files, force pushes, touching production config or secrets.
10. **Stop instead of stacking workarounds.** If a hop still fails after a few honest attempts, stop, record what you tried, and ask.

## 3. Workflow

Keep a running `MIGRATION_REPORT.md` at the repo root from Phase 1 onward
(template: `references/report-template.md`).

### Phase 0 - Scope
Confirm the current and target versions, *why* (end of life, CVE, feature, hosting),
constraints (API contract must not change, DB schema frozen, deadline), and what
"done" means for the user. Check that the **target** is still supported upstream
(e.g. on endoflife.date or the project's maintenance policy). If not, propose a newer target.

### Phase 1 - Inventory
- Detect the ecosystem (table in section 4) and open the matching file in `references/ecosystems/`.
- Record versions of: runtime, framework, build tool, package manager, OS/base image, database, every direct dependency.
- Run the ecosystem's "outdated" and "audit" commands.
- Flag risks: unpinned dependencies, abandoned packages (archived, no release in years), forks and vendored code, monkey patches, native extensions and system libraries, code generators, custom build steps.
- **Static scan for removed APIs.** Grep the code for every module, class, function and config key that the *target* versions remove (the "removed" sections of each release's notes, plus the list in the ecosystem file). Do not rely on deprecation warnings alone: shims, vendored copies, filters and lazy imports hide them (e.g. setuptools' `distutils` shim silences the Python `distutils` warning entirely). Every hit becomes a to-do item for Phase 4.

### Phase 2 - Baseline (before any change)
1. **Make it run as-is.** Old base images and removed package mirrors often break first. Fix only what is needed to run the *current* version and log it.
2. Run the full test suite. Record pass/fail/skip counts and duration. Pre-existing failures are recorded, not silently fixed.
3. Turn deprecation warnings on and save them to a file. Together with the Phase 1 static scan, they are your to-do list. An empty warnings file is not proof that nothing is deprecated.
4. **Record behavior snapshots** of the running system: see `references/behavior-snapshots.md`. For HTTP APIs use `scripts/snapshot.py`.
5. Run the snapshots twice against the unchanged app. Any difference is non-determinism: add it to the ignore list *now*, not later.
6. Cover error paths too (malformed input, wrong content type, missing fields). If you find an uncovered case later, record its baseline from the **original** commit (see "Adding a case after the upgrade has started" in `references/behavior-snapshots.md`), never from the current hop.
7. If critical paths have no tests, write **characterization tests** that assert *current* behavior, even when it looks wrong. Flag suspicious behavior in the report. Do not fix it during the upgrade.

### Phase 3 - Plan the path
- Build the hop sequence from the compatibility matrix. Runtime and framework usually have to be interleaved (e.g. bump the framework until it supports the newer runtime, then bump the runtime).
- For each hop, read the official upgrade guide and list the known **silent behavior changes** (see the ecosystem file).
- Show the plan to the user. In Mode A, wait for an OK before large changes unless the user already approved the whole job.

### Phase 4 - Execute, one hop at a time
For each hop:
1. Fix the deprecation warnings of the *current* version first.
2. Bump exactly one thing. Update the lockfile.
3. Install/resolve, fix the build.
4. Run the tests. Fix the code, not the tests (rule 4).
5. Run `snapshot.py compare` (or the equivalent) against the Phase 2 baseline. Every difference is either fixed, or explained and accepted by the user, and logged.
6. Boot the app and run a smoke check.
7. Update the ledger and commit: `upgrade: <thing> <from> -> <to>`.

### Phase 5 - Verify
- Full test suite, snapshot comparison against the **original** baseline (not the previous hop).
- Security audit of the final dependency tree.
- Boot in production-like mode: production env settings, asset build, migrations run on a *copy* of real data if available.
- Scan logs for new warnings and errors.
- Optional: a quick performance comparison of the snapshot requests (old vs new timings).

### Phase 6 - Report and hand-off
Finish `MIGRATION_REPORT.md` with: hops performed, final versions, test and snapshot
results, the **workaround ledger**, accepted behavior differences, remaining
deprecations, what was **not** verified, and a **human verification checklist**
(manual end-to-end flows, integrations, background jobs, scheduled tasks, emails,
file uploads, payments, auth, reporting). End with the status
"Ready for human verification", never "Done".

## 4. Ecosystem detection

| File(s) present | Ecosystem | Reference |
|---|---|---|
| `Gemfile`, `*.gemspec`, `.ruby-version` | Ruby / Rails | `references/ecosystems/ruby.md` |
| `requirements*.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | Python / Django / Flask | `references/ecosystems/python.md` |
| `package.json` | Node.js / JS / TS frontends | `references/ecosystems/node.md` |
| `pom.xml`, `build.gradle(.kts)` | Java / Kotlin / Spring | `references/ecosystems/java.md` |
| `composer.json` | PHP / Laravel / Symfony | `references/ecosystems/php.md` |
| `*.csproj`, `*.sln`, `packages.config`, `global.json` | .NET | `references/ecosystems/dotnet.md` |
| `go.mod`, `Gopkg.toml` | Go | `references/ecosystems/go.md` |
| `Cargo.toml` | Rust | `references/ecosystems/rust.md` |

Several may apply (e.g. a Rails app with a Node frontend): treat each as its own
track and never bump two tracks in the same hop.

**Ecosystem not listed** (Elixir, Scala, Swift, Dart, Perl, COBOL...): the method in
sections 2 and 3 still applies unchanged. Find the official release notes and
upgrade guide for each hop, the ecosystem's outdated/audit tooling, and search
the changelogs for "breaking", "removed", "default changed" and "behavior change".

## 5. Files in this skill

- `references/behavior-snapshots.md` - what to snapshot for APIs, web apps, CLIs, libraries, jobs and databases; normalization and determinism.
- `references/report-template.md` - the `MIGRATION_REPORT.md` template.
- `references/troubleshooting.md` - when a *tool* fails (Windows long paths, ports in use, old packages that will not install). A failing tool is never a reason to skip a check.
- `references/ecosystems/*.md` - per-ecosystem commands, hop strategy, tools, silent behavior changes, common workarounds.
- `scripts/snapshot.py` - record and compare HTTP API snapshots (Python 3.8+, standard library only).
