# Javier implementation delivery

Integration update, 1 October 2026: the focused source has been reviewed and corrected on the real repository. See [Deston’s delivery review](../project/JAVIER_DELIVERY_REVIEW.md) for current verification and remaining gates. The account below describes the original delivery environment; PR/video drafts are kept in the local original package, not committed.

This is a substantial review implementation, not a claim that every task is Done.
The original kickoff archive and existing reports/logs are unchanged.

## Coverage and remaining acceptance

| Task | Supplied now | Still required before Done |
|---|---|---|
| GF-P05 | Isolated native Windows button probe using the EXISTING capture worker; evidence recording and observer confirmations | Run on actual Windows; Calculator/Camera/file/folder/HTTPS, focus and Camera release/resume evidence |
| GF-P08 | Validated 1–100-card decks; NEXT/PREVIOUS; idempotent bookmarks/review/removal; atomic saved position/bookmarks; assignment defaults preserved | Deston's project-shell attachment and review |
| GF-P09 | Strict bounded portable workspace schema, transactional import/export, semantic slots, optional deck/runbook | Shared schema review and integrated import/activation test |
| GF-P29 | Ordered-stage model, create/edit/reorder/delete widget, authored instructions, manual continue/finish/previous; routing-reset acknowledgement; paused restoration | Deston's real configure/neutral/readiness integration and six-stage system run |
| GF-P13 | Twelve-target local registry/editor, native opening adapters, shared bounded duplicate gate, immediate validation and Camera acknowledgement/recheck | Real Windows errors/handoff, current readiness callback and shell integration |
| GF-P31 | Numeric measured Trial and Outcome adapters, retries/explicit completion, session-review widget and private-path-free export | Hau Jie's actual measured events/readiness integration and end-to-end count trace review |
| GF-P34 | Three visible Quick Actions bindings, empty-content startup/reload, local target controls and focus-loss signal | GF-P10 shared shell attachment, real target tests and readiness/focus integration |
| GF-P19 | Both-laptop evidence procedure and runnable recording probe | Both laptops' ACTUAL integrated checks; no device evidence fabricated |
| GF-P22 | Regression fixes found while building, affected software tests | Defects revealed by future Windows/system acceptance and those regressions |
| GF-P25 | Accurate component user-guide draft and complete recording storyboard/narration | Guide-only second-Windows installation, final screenshots/build updates and actual full demo recording |

The supplied fictional six-stage workspace is `assets/harbor_workspace.json`. It
uses the existing ten-card corporate deck and named local resource slots. It contains
no local paths, URL bindings, private samples, credential fields or executable code.
The review preview starts without data/models. Real live OS launch remains outside
the assignment/Studio shell until Deston integrates and approves the callbacks.

## Review files

- `viewer.py` is the only modified existing production file. Its default `apply`
  retains NEXT-only assignment behaviour; project controls use typed actions.
- New modules: `storage`, `workspace`, `runbook`, `shortcuts`, `dispatcher`,
  `session_summary`, `javier_widgets`, plus the isolated `javier_preview` harness.
- New tests: `test_javier_lane.py` and `test_javier_widgets.py`.
- New script: `scripts/windows_launch_probe.py`.
- New content/docs: the fictional workspace and this `docs/javier` directory.
- `app.py`, `__main__.py`, `contracts.py`, `controller.py`, `routing.py`, capture,
  recognition/profile modules and their existing tests are untouched.

Read `INTERFACE_PROPOSAL.md` before attaching widgets. Simulation dispatch never
calls an OS adapter, changes a viewer or enters a runbook stage; the separate preview
provides clearly labelled manual content inspection. Real manual and gesture
requests share the same final duplicate gate. Failed callbacks cannot be retried
with the same ID. Restoring state or changing configuration opens nothing.

## Actual software evidence

See `software-checks.json` for exact commands, outputs, environment and limitations.
It records Linux/Python 3.12 development checks, not Windows 3.11 deployment.
`pytest` uses fake launch adapters and offscreen Qt. Native adapter mocks verify
argument-safe requests and mapped-network rejection; they do not prove visible
application opening. Offscreen smoke tests do not establish real display/device
performance or thirty-minute stability. The original assignment and Studio smoke
checks are also rerun.

## Git delivery and integration

The archive identifies published base
`a331d5815b9c0b671601935b06cda8b804798d2c`. Git clone was attempted but GitHub required
authentication in this environment. No remote source history was fetched; no push,
PR, reviewer request or merge has occurred. A local `codex/javier-shortcuts` review
branch was created from the supplied snapshot, with a clearly marked synthetic
baseline commit. DO NOT push that synthetic history over the repository.

The delivery includes a focused patch containing ONLY this implementation, relative
to the supplied snapshot. It is not the obsolete project-foundation kickoff patch.
On a GitHub-authenticated computer, clone/fetch the real repository, preserve existing
work, create/switch `codex/javier-shortcuts` from `origin/main`, check the patch, apply
it, run checks, review and commit on that branch. The exact procedure is in the outer
`START_HERE.md`. If the remote has advanced or the branch already contains work,
`git apply --check` must succeed; resolve differences with Deston instead of forcing
an old snapshot over shared work. Push ONLY Javier's branch and open a PR into main
for Deston's review. Leave it unmerged. No force-push.

`PR_DRAFT.md` supplies the focused review body; `INTERFACE_PROPOSAL.md` is the message
proposal for Deston. Neither has been posted or sent through an account.
