# legacy-upgrade

A portable skill for AI coding agents that upgrades legacy codebases **safely**, in any
language: runtime, framework and dependency version bumps (Rails 5 to 7, Python 2 to 3,
Django 1.x to 5, Java 8 to 21, Spring Boot 2 to 3, Node 12 to 22, .NET Framework to .NET,
PHP 7 to 8, Go and Rust toolchains, and anything else).

> **Green tests are not proof.** Legacy test suites are thin. An AI can make them pass
> while the API silently returns different data. This skill makes the agent prove that
> behavior was preserved, and say clearly what it could not prove.

## What the agent does with it

1. **Snapshots real behavior before touching anything** (API responses, CLI output, schema dumps).
2. **Upgrades one hop at a time** (one runtime *or* framework *or* major dependency per step, one commit each).
3. **Compares behavior after every hop** against the original baseline, not just the tests.
4. **Logs every workaround** (pins, shims, silenced warnings, test changes) in a ledger.
5. **Never says "done"**: it hands off a `MIGRATION_REPORT.md` with a human verification checklist.

It works in three modes: the agent runs commands itself, the agent only suggests
commands (you run them), or chat-only advice.

## Proof: the demo in `examples/locadora-api`

A small Flask 1.1 / Python 3.11 rental-store API with realistic traps, upgraded to
Flask 3.1 / Python 3.14 by following the skill:

| | Naive upgrade ("make it boot") | With the skill |
|---|---|---|
| Tests | 7/7 green | 7/7 green |
| Endpoints with changed responses | **10 of 14** (prices `9.9` → `"9.90"`, dates `30/08/2002` → `"Fri, 30 Aug 2002 00:00:00 GMT"`, form posts → 400) | 0 contract changes (2 cosmetic error-page HTML diffs, flagged for approval) |
| Known vulnerabilities (pip-audit) | - | 15+ → 0 |

See [`examples/locadora-api/MIGRATION_REPORT.md`](examples/locadora-api/MIGRATION_REPORT.md)
and [`snapshots/counterfactual-naive.md`](examples/locadora-api/snapshots/counterfactual-naive.md).

## Install

Clone the repo, then copy the `legacy-upgrade/` folder (only that folder) where your tool expects it.

```bash
git clone https://github.com/thiagoalves0707/legacy-upgrade.git
```

- **Claude Code** (terminal, desktop app, VS Code, JetBrains): copy to `~/.claude/skills/legacy-upgrade/` (all projects) or `<repo>/.claude/skills/legacy-upgrade/` (shared with your team). Claude uses it automatically when you ask for an upgrade, or call it with `/legacy-upgrade`.
- **Other agents that support the Agent Skills format (`SKILL.md`)**: copy the folder into that tool's skills directory (see the tool's docs).
- **Tools that use a rules file** (`AGENTS.md`, `.github/copilot-instructions.md`, Cursor rules, internal company assistants): use [`legacy-upgrade/adapters/RULES.md`](legacy-upgrade/adapters/RULES.md); for Cursor, [`adapters/cursor/legacy-upgrade.mdc`](legacy-upgrade/adapters/cursor/legacy-upgrade.mdc). Keep the full folder in the repo so the agent can read the references and run the script.
- **Chat-only assistants**: paste `SKILL.md` and the relevant `references/ecosystems/*.md` file.

## Contents

```
legacy-upgrade/                 the skill
├── SKILL.md                    workflow and rules
├── references/
│   ├── behavior-snapshots.md   what and how to snapshot
│   ├── report-template.md      MIGRATION_REPORT.md template
│   ├── troubleshooting.md      when a tool fails
│   └── ecosystems/             ruby, python, node, java, php, dotnet, go, rust
├── scripts/snapshot.py         record/compare HTTP API snapshots (stdlib Python 3.8+)
└── adapters/                   rules for tools without skill support
examples/locadora-api/          worked example with report and snapshots
```

## Limits

- It structures the work; it does not make a weak model strong.
- Projects without tests need characterization tests first.
- Offline or private-registry environments need a human to confirm available versions.
- The ecosystem notes are a starting checklist; official upgrade guides remain the source of truth.

## License

[MIT](LICENSE) - free to use, modify and share, including in commercial and company projects.
