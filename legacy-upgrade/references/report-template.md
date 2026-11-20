# MIGRATION_REPORT.md template

Copy this to the repository root at the start of Phase 1 and keep it updated
after every hop. Write facts, not reassurance.

```markdown
# Migration report: <project>

**Status:** In progress | Ready for human verification
**Branch:** <branch>   **Started:** <date>   **Last update:** <date>
**Operating mode:** A (autonomous) | B (assisted) | C (advisory)

## Goal
- From: <runtime x.y, framework x.y>
- To:   <runtime x.y, framework x.y>
- Reason: <EOL / CVE / feature / hosting>
- Constraints: <API contract frozen, DB schema frozen, deadline...>
- Target support status checked: <source + date>

## Inventory (before)
| Component | Version | Notes (pinned? abandoned? fork? native?) |
|---|---|---|

Risks found:
- ...

## Baseline (before any change)
- Tests: <passed>/<total>, <failed> failing, <skipped> skipped, <duration>
- Pre-existing failures: <list, untouched>
- Deprecation warnings captured: <count> (file: <path>)
- Snapshots: <n> cases in <path>, determinism check: <pass / fields ignored>
- Characterization tests added: <list>
- Suspicious current behavior (not fixed): <list>

## Upgrade path
| # | Hop | Status | Commit | Tests | Snapshot diffs |
|---|---|---|---|---|---|
| 1 | Rails 5.2 -> 6.0 | done | abc123 | 45/45 | 0 |

## Workaround ledger
Every pin, patch, silenced warning, skipped test, shim or old default kept.
| # | Hop | What | Why | Risk | How to remove later |
|---|---|---|---|---|---|

## Test changes
| Test | Before | After | Reason |
|---|---|---|---|

## Accepted behavior differences
Differences found by snapshots that the user explicitly accepted.
| Case | Difference | Accepted by / when | Reason |
|---|---|---|---|

## Final state
- Versions: ...
- Tests: ...
- Snapshot comparison vs original baseline: ...
- Security audit: ...
- Remaining deprecation warnings: ...

## Not verified
Be explicit: integrations not reachable, production data not available, jobs not exercised, etc.

## Human verification checklist
- [ ] Login / logout / password reset
- [ ] Main business flows end to end: <list the real ones>
- [ ] Payments / billing (sandbox)
- [ ] Emails and notifications are sent and render correctly
- [ ] File upload / download
- [ ] Background jobs and scheduled tasks run
- [ ] Reports and exports match the old version
- [ ] External integrations / webhooks
- [ ] Dates, time zones, money and decimals display correctly
- [ ] Logs show no new errors or warnings in a staging run
- [ ] Rollback plan tested
```
