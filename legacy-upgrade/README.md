# legacy-upgrade

A portable skill for AI coding agents that upgrades legacy codebases **safely** in any
language: runtime, framework and dependency version bumps (Rails 5 to 7, Python 2 to 3,
Java 8 to 21, Spring Boot 2 to 3, Node 12 to 22, .NET Framework to .NET, PHP 7 to 8,
Go and Rust toolchains, and anything else).

Its main idea: **green tests are not proof.** The agent snapshots real behavior
before touching anything, upgrades one hop at a time, compares behavior after every
hop, logs every workaround, and hands off with a human verification checklist
instead of claiming "done".

## Contents

```
legacy-upgrade/
├── SKILL.md                         main instructions (the skill itself)
├── references/
│   ├── behavior-snapshots.md        what and how to snapshot
│   ├── report-template.md           MIGRATION_REPORT.md template
│   └── ecosystems/                  ruby, python, node, java, php, dotnet, go, rust
├── scripts/
│   └── snapshot.py                  record/compare HTTP API snapshots (stdlib Python)
└── adapters/
    ├── RULES.md                     condensed rules for tools without skill support
    └── cursor/legacy-upgrade.mdc    Cursor rule file
```

## Install

### Claude Code (terminal, desktop app, VS Code, JetBrains)
Copy the whole folder to one of:
- `~/.claude/skills/legacy-upgrade/` - available in all your projects
- `<repo>/.claude/skills/legacy-upgrade/` - shared with the team through git

Claude loads it automatically when you ask for an upgrade, or invoke it with `/legacy-upgrade`.

### Other agents that support the Agent Skills format (SKILL.md)
Several coding agents now read `SKILL.md` folders. Copy this folder into that
tool's skills directory (check the tool's docs for the exact path). Nothing in the
skill depends on Claude.

### Tools that use a rules / instructions file
Paste or reference `adapters/RULES.md` in the file your tool reads, for example:
- `AGENTS.md` at the repo root (read by many agents)
- `.github/copilot-instructions.md` (GitHub Copilot)
- `.cursor/rules/legacy-upgrade.mdc` (Cursor - use `adapters/cursor/legacy-upgrade.mdc`)
- your company's internal assistant's system prompt or project rules

Keep the full folder in the repo (e.g. `tools/legacy-upgrade/`) so the agent can
open the ecosystem references and run `scripts/snapshot.py`.

### Chat-only assistants (no repo access)
Paste `SKILL.md` (and the relevant `references/ecosystems/*.md`) into the chat or a
project's instructions. The skill switches to Mode C: plan, risks and checklists,
with you running the commands.

## Example prompts
- "Upgrade this API from Rails 5.2 / Ruby 2.7 to Rails 7.2 / Ruby 3.3."
- "We're on Java 8 and Spring Boot 2.3. Plan the upgrade to Java 21 and Boot 3."
- "Our Node 14 backend has 40 audit warnings. Modernize it safely."
- "Kimi/Claude upgraded this and the tests pass - verify it actually behaves the same."

## The snapshot script
```bash
python scripts/snapshot.py record  --base-url http://localhost:3000 --cases cases.json --out snapshots/baseline
python scripts/snapshot.py compare --base-url http://localhost:3000 --cases cases.json --baseline snapshots/baseline --report snapshots/diff.md
```
See `references/behavior-snapshots.md` for the `cases.json` format.

## Limits
- It structures the work; it does not make a weak model strong.
- Projects with no tests need characterization tests first - more work, but the skill guides it.
- Offline or private-registry environments need a human to confirm available versions.
- Ecosystem notes are a starting checklist. Official upgrade guides remain the source of truth.
