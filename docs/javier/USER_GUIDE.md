# Javier component guide — review build

This build supplies viewer, workspace/runbook, target library, dispatcher and
session-review components. It preserves the original assignment and simulation
Studio entry points. Deston still needs to attach the new widgets to the shared
shell and Hau Jie's readiness/profile workflow. It is not the accepted final release.

## Install and inspect on Windows

Use 64-bit Python 3.11, as required by the team guide. Extract the delivered archive,
open the `source` folder in PowerShell and run:

```powershell
.\setup.cmd
.\.venv\Scripts\python.exe -m gestureforge.javier_preview
```

The original commands remain `run.cmd` for the assignment and `run.cmd --studio`
for Deston's simulation preview. The new component preview needs no dataset,
trained model, camera or enrolment. Setup still needs internet for dependencies and
the landmark asset. The software checks shipped with this package used Linux and
Python 3.12; they do not establish a Windows 3.11 install or live-camera result.

For standalone empty-content Quick Actions inspection:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.javier_preview --quick-only
```

The preview is labelled **simulation only**. Shortcut tests record a would-be
request and do not open applications. Viewer/runbook inspection buttons let you
browse fictional content manually; this is an inspection harness, not gesture
recognition or a readiness check. Local targets are never exported in the workspace.

## Quick Actions

1. Click **New**. Enter a unique opaque ID and a display label. The ID must contain
   1–64 ASCII letters/digits or `_ . : -` and start with a letter/digit.
2. Select a type: Builtin (`calculator` / `camera`), existing trusted local `.exe`,
   reference file (PDF/TXT/PNG/JPEG), existing local folder, or HTTPS website.
3. Browse for file/folder/app targets. Confirm trust only for an installed app.
   Shells, interpreters, scripts, arguments, links, network/device paths and embedded
   URL credentials are rejected. Selection is a trust decision, not a malware scan.
4. Click **Save target**. The local library allows twelve named targets, with labels
   up to eighty characters. Select up to three targets in the visible gesture slots.
5. Use **Test selected target**. In the preview this remains simulated. For actual
   Windows opening use the isolated probe described below, then repeat target tests
   in the integrated shell after Deston enables it. Test on each laptop separately.

Unavailable targets remain visible. Rebind a moved file or choose a valid default
application; never hide a failure by declaring completion. Loading local state or
changing a mapping opens nothing. In the preview, local bindings save beneath
`.local/javier-preview/targets.json`. Keep that file private; do not share it.

## Viewer and runbook

The supplied fictional Harbor Desk workspace contains ten cards and six ordered
stages. The Viewer inspection tab has Next/Previous, Bookmarks and explicit removal.
There is no wrap at either boundary. Repeating Bookmark keeps one saved bookmark.
Activate a bookmark entry to review its card; removal uses a separate button.

The runbook tab shows authored instructions, the current gesture meanings and manual
buttons, including Previous stage and Continue/Finish. Entering a stage only shows
content; it never opens resources. Completion uses **I completed this stage’s task**.
Opening Calculator does not prove you calculated 240 credits.

The Stage editor can create, edit, reorder or delete up to twelve stages. Each has
an opaque ID, title, authored instruction, optional valid card reference, up to three
single action mappings, and a nonempty Continue label. The last stage has a visible
Finish button. No scripts, loops, chains or arbitrary target paths are supported.
Edits reset and pause the preview routing context. Real attachment must follow
`INTERFACE_PROPOSAL.md`.

A portable workspace uses schema version 1 and at most 1 MiB of JSON. Its content is
only the deck, stages, semantic shortcut IDs/labels and gesture action mappings.
`WorkspaceWidget` provides validated import/export for shell attachment. The supplied
preview reads `assets/harbor_workspace.json`; save-progress also exports the current
edited content to `.local/javier-preview/workspace.json`. Other JSON imports can be
staged through `WorkspaceWidget.import_path` or `WorkspaceStore.import_file`; their
shell activation remains Deston's integration work. Every field is validated before
replacement. Unknown fields/actions, duplicate IDs, broken references and incompatible
schemas are rejected. Optional decks/runbooks may be absent for Quick Actions.

## Save, restore and review

**Save progress** saves the current stage, card and bookmarks atomically. **Restore
paused** validates the entire saved session before changing content and keeps gesture
routing paused. No shortcut is replayed. Resume is an explicit operation. In the
preview, the state is `.local/javier-preview/session.json`; keep its matching workspace
when reopening authored edits. A corrupt or mismatched file leaves prior content
unchanged. An interrupted atomic replacement leaves the prior file intact; recover
by selecting a valid workspace/state copy or start afresh. Temporary files are not
silently promoted to state.

Session Review distinguishes simulated requests, actual OS launch requests,
failures, duplicates, viewer changes, retries and user-acknowledged completion.
Correct/wrong/missed trial counts appear only when real measured Trial records are
supplied by Hau Jie's integration. Zero means none recorded, not a passed study.
UNKNOWN predictions count as misses. Results export omits paths, URL values and raw
video. A retry is counted when explicitly reported, not guessed from a launch.

## Actual Windows opening and Camera handoff probe

Run the isolated manual probe in a separate session, with the assignment app closed:

```powershell
.\.venv\Scripts\python.exe -m scripts.windows_launch_probe --laptop-id laptop-A --output .local\laptop-A-probe.json
```

Configure/test Calculator, Camera, a permitted reference file, a folder and HTTPS.
For Camera, first click **Start / resume capture explicitly** and wait for the
actual frame-received message. Testing Camera pauses routing, requests shutdown of
the existing capture worker, waits for its acknowledgement and only then requests
Windows Camera. A timeout/refusal opens nothing. The wait is bounded; it is not a
sleep used as proof of release. Observe the actual visible application and press the
appropriate confirmation button. OS acceptance alone is labelled `launch_requested`.

Return manually; close Windows Camera if it holds the device; click explicit resume
to reacquire capture. Focus loss pauses routing, and focus gain never resumes it.
No classifier action launches anything in this probe. Repeat on laptop-B with a
separate output filename. See `WINDOWS_EVIDENCE.md` for the required actual checks.

## Recovery and operating limits

- Missing landmark asset: run setup / `python scripts/download_model.py`.
- Camera unavailable: check Windows camera permission, selected index and competing
  consumers. No Camera opening is allowed without confirmed capture shutdown.
- Missing/moved target: restore the selected test resource or rebind it, then issue
  a NEW manual request. Failed and duplicate event IDs are never retried automatically.
- No default file association: set a default app in Windows or use manual opening.
- Invalid target/scheme: choose a permitted existing local target or credential-free
  HTTPS URL. Portable imports cannot install local bindings.
- Export/atomic write failure: choose a writable directory and retain the old state;
  do not treat an unsuccessful write as saved.
- Capacity reached: export recorded outcomes and start a new application session;
  the dispatcher fails closed rather than evicting event IDs.

Core content/storage works offline after setup. A website still needs internet/site
access. GestureForge opens resources; it does not control their internal UI, operate
in the background, authenticate profile owners or offer universal recognition.
Real Windows 3.11, second-laptop install, live recognition, thirty-minute stability
and full demo recording still require evidence before release.
