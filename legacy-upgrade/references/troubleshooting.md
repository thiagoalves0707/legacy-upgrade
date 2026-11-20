# Troubleshooting tooling problems

Tooling failures are not project failures. Fix the tool, note it in the report under
"Not verified" or the ledger if it changed anything, and move on. Never skip a check
(audit, tests, snapshots) because its tool failed: find another way to run it.

## Windows: paths too long
**Symptoms:** `ImportError: DLL load failed ... The filename or extension is too long`
(localized messages too, e.g. "O nome do arquivo ou a extensão é muito grande"),
`FileNotFoundError` on files that exist, `npm`/`pip`/`git` errors in deep `node_modules`
or virtualenv folders.

**Cause:** the project sits in a deep folder and tool paths exceed the classic 260-character limit.

**Fixes, least invasive first:**
1. Install the tool in a short path outside the project, e.g. a virtualenv in `%LOCALAPPDATA%\Temp\pa`, and run it from there against the project (`pip-audit -r <project>/requirements.txt`).
2. Work from a short path: `subst X: <long path>` or a short junction (`mklink /J C:\w <long path>`).
3. `git config core.longpaths true` for git operations.
4. Enabling Windows long paths system-wide is a system setting: ask the user, do not change it yourself.

## Ports already in use
Run the old and new app on different ports (e.g. 5101 baseline, 5102 hops). Kill
servers you start; leftover servers make later comparisons hit the wrong version.

## Old dependencies will not install
- No wheels for the current platform/interpreter (old `MarkupSafe`, `psycopg2`, `nokogiri`, `node-sass`): use the runtime version the project originally targeted for the baseline (a Docker image or an older interpreter), not a newer one.
- Removed package mirrors or registries: check for a mirror or vendored copy; never silently substitute a different version. Log what you used.

## Comparing against the wrong code
If snapshot results look too good or too bad, confirm which version is actually
serving: print the framework version at startup or hit a version endpoint, and check
that only one server runs on the port.
