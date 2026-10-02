# Javier track — 4 October checkpoint

Updated 2 October 2026. Current work is on `codex/javier-shortcuts` only.

Latest reviewed main `a6fe7b6e59b5ba91dd38651c3350862f4602164e` was merged into this branch as `10340890899af911ceff0059d709effa049a81dd`. Existing branch history and the earlier review ZIP remain intact; the ZIP patch was not reapplied. Deston owns the Studio shell, whose manual deck navigation, bookmarks, progress, runbook editing and session summaries are retained.

The sync retains main's dispatch rechecks, widget focus-filter lifecycle, interpreter exclusion and acknowledged shutdown on close, plus Javier's newer preview workspace replacement, transactional target edits, typed action selection and regressions. Shared shell, routing, contracts and recognition files match reviewed main.

- [4 October checkpoint and next steps](OCT4_CHECKPOINT.md)
- [Actual Windows procedure](WINDOWS_EVIDENCE.md)
- [Shared starter collection guide](../project/STARTER_COLLECTION_GUIDE.md)
- [Existing P03 checkpoint](../project/STARTER_EVALUATION_CHECKPOINT.md)
- [This sync's exact software results](oct4-software-checks.json)

Linux/Python 3.12 offscreen verification: 373 tests passed; Ruff and mypy passed; assignment, Studio, full preview and Quick Actions startup smokes passed. These are software checks, not Windows/hardware results. New P03 recording/transfer and real Windows checks were NOT RUN here. Previous delivery documents and `software-checks.json` are historical and do not describe the newly integrated main.
