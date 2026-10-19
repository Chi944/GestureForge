# GF-P19: laptop-A target validation follow-up, 19 October 2026

Operator: Javier, on his existing Windows laptop A. Runtime source:
`d200947692253ede0c264755152e4419530147a3`, continuing the same Studio
session identified in the trusted-app/restore record. Later documentation
commits do not change that runtime attribution. Earlier environment observations
identify Windows 11 Home build 26200 and Python 3.11.9; neither was remeasured here.
Screenshots show Preview and Camera off. No full Practice or LIVE gesture grant
was obtained for this check.

These are AI-guided human observations, supported by supplied screenshots,
a private summary export and Javier's confirmation. Javier operated Windows;
GPT inspected the supplied evidence and matching source, not the physical device.

## Save-time validation and recovery

The separate draft ID was `invalid-cmd-test`, display label `Invalid CMD test`.
Existing working targets and their three slot selections remained visible.
No Test selected target or gesture request was instructed during this sequence.

| Case | Input/procedure | Supplied outcome | Evidence boundary |
| --- | --- | --- | --- |
| App trust confirmation | App target pointing at the project's existing run-studio.cmd, trust checkbox unticked | Cannot save target: confirm that the selected application is trusted | Demonstrates the trust guard only; does not establish App-mode executable-extension rejection. |
| Unsupported reference file | Changed that draft to File, retaining run-studio.cmd | Cannot save target: reference files must be PDF, TXT, PNG or JPEG | Demonstrates .cmd rejection as a reference file; not a native launch failure. |
| HTTP website | Website with http://example.com | Cannot save target: invalid HTTPS URL | Separate screenshot shows Website and the exact HTTP value; the subsequent status screenshot shows rejection. |
| Credential-containing HTTPS | Guided input https://testuser:testpass@example.com, using fictional credentials | Subsequent screenshot shows Cannot save target: invalid HTTPS URL | Input entry is guided operator evidence; this screenshot shows status only, not the full submitted URL. |
| Device path | Folder with the guided device-prefixed Windows directory path | Cannot save target: network/device paths are not permitted | Guided input and status-only screenshot; exact submitted editor value is not jointly captured. |
| UNC path | Folder with guided value `\\\\example.invalid\\share` | Cannot save target: network/device paths are not permitted | Guided input and status-only screenshot; no share availability or mapped-drive coverage is claimed. |
| Valid save after rejection | New ID validation-recovery-test, label Validation recovery test, Website with guided https://example.com | Target configured. Test it explicitly; returning requires Resume. The new label/ID appears in the library. | Save/configuration recovery only. No browser-launch retry was performed or needed for this check. |

An intermediate HTTP screenshot showed the older Bindings changed status.
It was not counted as a pass; the operator then supplied the input fields,
clicked Save target and supplied the actual invalid-HTTPS message.

Javier subsequently confirmed that nothing opened during these checks.
Saving the valid HTTPS target also did not automatically open a browser.
The existing Harbor Camera and trusted-app slot assignments remained visible;
the valid recovery entry was not shown bound to a gesture slot.

## Private evidence and summary reconciliation

Raw screenshots and JSON stay private; they are not committed with this note.

- Trust rejection: image(20261019-092238).png.
- Reference-file rejection: image(20261019-092433).png.
- HTTP fields/result: image(20261019-093027).png and image(20261019-093148).png.
- Credential URL result: image(20261019-093240).png.
- Device/UNC results: image(20261019-093341).png and image(20261019-093445).png.
- Valid configuration recovery: image(20261019-093605).png.
- Export: laptop-A-validation-2026-10-19.json.

The export identifies Harbor workspace `harbor-onboarding-standard`, revision
`a9e529dd-6f3f-4c62-adbf-7c2a4e31facc`. Every count is zero, outcomes/trials
and completed stages are empty. Parsed comparison shows it is object-for-object
identical to laptop-A-after-session-restore-2026-10-19.json from the earlier
restore record. Do not count it as another disjoint segment or add its totals.

Save-time validation errors are widget feedback, not dispatcher outcomes;
zero failed/rejected counts do not mean those checks were absent. The unchanged
summary supports no added dispatch activity; screenshots and the operator's
confirmation supply the separate save-time and no-opening observations.

## Verification and limits

GPT parsed and compared the two summary objects, checked zero counts/empty
events and inspected QuickActionsWidget's status placement/save handler in the
matching source archive. Report formatting was checked. No production code was
changed; no new Ruff/mypy/pytest or independent Windows run is claimed.

This follow-up does not complete the entire invalid-input matrix: App-mode
extension/interpreter rejection, .lnk/.url and mapped network paths were not
newly verified. Missing association remains NOT RUN without an isolated setup;
existing associations were not modified. Preserve accepted missing-target and
other earlier evidence without repeating unchanged cases.

Active-capture Camera remains NOT RUN because the genuine current-session full
Practice grant is absent. Hau Jie operates laptop B; his observations and
GF-P23 fresh-install/offline/thirty-minute/shutdown evidence remain separate.
No full GF-P19/GF-P23 acceptance, gesture recognition repair or task-completion
claim follows from these configuration checks.

Separately, Javier reported sending the verified private P03 development ZIP
to the team after the handoff steps. Recipient receipt/content review and any
recognition repair are for Deston and Hau Jie; no private data are included here.
