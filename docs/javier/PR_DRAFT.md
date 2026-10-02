# Proposed title

GF-P08/P09/P29/P13/P31/P34: Javier viewer, portable workspace and bounded shortcut components

# Proposed PR body

This change extends the assignment viewer with opt-in Studio navigation/bookmarks,
adds validated portable workspace/runbook components and supplies embeddable local
shortcut, Quick Actions and measured session-review widgets. Local target edits commit only after a successful atomic save. Workspace imports
replace deck/runbook/editor choices together while paused; editing an imported
stage preserves its typed actions. The assignment's
NEXT-only default and shared shell/routing/recognition files remain intact.

Real manual and routed actions share one bounded duplicate gate. Preview/rehearsal
records simulated actions without calling an OS adapter. Local targets are resolved
and validated immediately before opening; Camera requires acknowledged capture
shutdown and a fresh context/readiness check. Imports/restores never replay launches.
The supplied six-stage Harbor Desk workspace carries semantic slots, never local
target paths, URL bindings or profiles.

Validation: exact Linux/Python 3.12 commands, environment and results are in
`docs/javier/software-checks.json`. Tests include viewer/bookmark boundaries,
transactional import, atomic failure recovery, export privacy, independent local
bindings, target/URL rejection, stale/duplicate requests, readiness/callback failures,
Camera acknowledgement, no simulation/restore launch and offscreen empty Quick
Actions/widget checks. Assignment, Studio and owned preview smoke checks were run.

Acceptance limits: Windows 3.11 actual launch/focus/Camera/error evidence on BOTH
laptops is pending. GF-P10 shell/readiness attachment and Hau Jie's actual measured
trial stream are pending. `docs/javier/INTERFACE_PROPOSAL.md` proposes the attachment
boundary. GF-P25 includes a guide and full recording draft, not a finished video.
No real-device or new-user recognition result is claimed.

Please have Deston review the owned modules, strict schema and callback proposal
before shell integration. Leave this PR unmerged; Deston owns final integration.
