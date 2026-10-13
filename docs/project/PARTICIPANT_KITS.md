# Participant collection kits

Deston prepares two local ZIPs: `GestureForge_Participant_Windows.zip` and
`GestureForge_Participant_macOS.zip`. Each contains `START_HERE.html`, a readable
`READ_FIRST.pdf`, and third-party notices. They are collection-only browser
tools, not packaged Studio installations. Participants need an existing browser
and webcam, with permission to use the camera. No Python, terminal, account or
separate model installation is required. All runtime/model bytes are embedded;
there are no CDN requests or automatic data uploads.

## Before distributing

Hau Jie coordinates two genuinely new participants excluded from starter fitting
and tuning. Allocate unique pseudonyms and privately record the mapping. The
coordinator selected deletion after marking and appeals finish, with access
limited to the team and private marker. Obtain each person's explicit agreement
to that notice before recording; P01's permission does not cover them. The
recorder includes the arrangement and consent with the numeric return data.

Have one operator on each target OS verify the extracted HTML: model loads,
correct webcam/Right-hand feedback, first trial, pause/reload recovery, offline
trial, return ZIP export and coordinator import. Record OS/browser versions,
package hash and help required. Local-file camera policies differ by browser;
static and generated tests do not prove this works on every machine. If camera
or model loading is blocked, preserve the visible error. Do not bypass browser
security or ask inexperienced participants to install a developer stack.

Use the current rebuilt kit for recovery checks. The 9 October repair preserves
UNKNOWN condition notes when loading a partial return ZIP before VALIDATION has
started. Keep the original ZIP; resuming should retain recorded trials rather
than require recording them again.

## Starting a session and resolving setup messages

The participant enters their assigned code, reviews the consent items, and
describes **TRAIN conditions** before starting TRAIN. They should describe their
actual lighting, background, sitting/standing position and approximate hand
distance. **VALIDATION conditions are entered after the break**, immediately
before starting VALIDATION. UNKNOWN uses the VALIDATION condition notes and
should be recorded under those same conditions. Future session notes are not
required to start TRAIN.

Click **Start Camera**, allow camera access when asked, wait for the detector,
and check that the whole right hand is visible with **Right hand detected**.
Choose TRAIN and click **Start Selected Session**. Successful start brings the
large instruction and countdown above the camera preview into view. Camera
video and hand feedback by themselves are not evidence that recording started.

If **Setup required** appears, the message identifies the missing information
and the page focuses that field or consent item. Complete or review that item,
then start the selected session again; a working camera does not need restarting.
During an active session, Start and Export are unavailable intentionally. Pause
remains available. Pause and wait for the trial to settle before exporting or
leaving the tab.

Pause turns the camera off. To resume, click **Start Camera**, wait for the
detector, then **Start Selected Session**. Completed trials are retained and
skipped; the current interrupted trial keeps its invalid sample slots.

### Continue after TRAIN or recover a partial ZIP

The 13 October repair selects the first unfinished section after a section
finishes, a saved draft is restored or a return ZIP is imported. It shows the
next section and remaining trials; it never starts recording automatically.
Previously, TRAIN could remain selected after all its trials were saved, so
clicking Start immediately reported completion without advancing to VALIDATION.

Keep the original return ZIP. Open `START_HERE.html` from the rebuilt kit and
use **Recover from a previous return ZIP** to choose that ZIP without unzipping
it. A TRAIN-only return should show **48 / 104 trials** and select **VALIDATION**.
After the break, enter the actual VALIDATION condition notes, click **Start
Camera**, wait for the detector, then **Start Selected Session**. Finish the
48 VALIDATION trials and eight UNKNOWN trials. Export the new complete
`EMAIL_THIS_<code>_development.zip`; it should show 104 / 104 without PARTIAL
in the filename. Do not clear the draft or repeat completed TRAIN trials.

VALIDATION notes remain editable until that section or UNKNOWN has started.
If the displayed state differs, keep the backup and send the exact message,
browser name and macOS/Windows version to the coordinator. This handoff repair
does not establish the cause of every browser-specific camera or setup failure.

For persistent **No hand detected** or wrong-hand feedback, pause and check that
light falls on the whole right palm, fingers and wrist are unobstructed, and the
hand is far enough back to fit the picture. Click **Start Camera** to check the
adjusted view; feedback cannot update while the camera is paused. If this does not resolve it, contact
the team before recording more trials. Retain partial returns and errors rather
than deleting unsuccessful observations.

## First delivery: development only

The shared physical poses are Right-hand open palm = NEUTRAL, fist = NEXT,
thumb up = PREVIOUS, index and middle fingers extended = BOOKMARK. Keep the
unmirrored inference input; only the preview is mirrored. Each person records:

| Section | Trials | Scheduled samples | Time to allow |
| --- | ---: | ---: | --- |
| TRAIN | 12 per pose, 48 total | 240 | About 5-6 minutes |
| Separate VALIDATION session | 12 per pose, 48 total | 240 | About 5-6 minutes |
| UNKNOWN development negatives | 8 | 40 | About 1 minute |

Allow **15-20 minutes plus a break** for setup, all three sections and export.
Each trial has a three-second countdown, about two seconds holding the pose,
and one second to relax. These are estimates derived from the schedule, not
measured participant times; slower tracking, pauses and recovery add time.
Keep the recorder tab visible and use Pause before leaving it.

Five sample slots fall at 0.2, 0.6, 1.0, 1.4 and 1.8 seconds in each hold.
Invalid, late and interrupted slots remain in the return data. These are
development negatives, not the live false-action evaluation. Final TEST cannot
be recorded by this kit. Deston must first review the complete development
packet and freeze configurations. A later separately released TEST collection
step must preserve the same declared browser/pose protocol, source hashes and
chronology; native/browser changes require explicit evaluation design review.

Participants download one `EMAIL_THIS_*_development.zip` from the recorder and
email that existing ZIP. They should not zip the application directory. Keep
partial returns and interruptions; do not delete difficult trials or ask for
blanket retries. A completed recording schedule is not an accuracy pass.

## Coordinator import

Save the emailed ZIP under ignored `data/local/`. From an installed development
checkout, import it to a new output path:

```powershell
.venv\Scripts\python.exe -m gestureforge.import_participant data/local/EMAIL_THIS_P04_development.zip --output data/local/P04/browser-development/manifest.json
```

The importer validates the archive and protocol, then uses the existing
Observation/feature pipeline to create the usual manifest and numeric NPZ.
Every invalid slot remains a record. Keep the original return ZIP, reported
conditions, consent and checksum with the imported data. Inspect the completion
summary; partial imports do not satisfy H2's required counts. Do not commit
private return files or full manifests/results.

The coordinator importer assigns deterministic trial IDs from participant,
session and the original browser trial ID. Different people's generic browser
trial names can therefore be combined without collisions. The manifest retains
the original-ID mapping and scheme version; duplicate or overlapping returns
from the same person/session remain duplicates. Raw packet validation happens
before this conversion, and labels, splits, sample slots and features are unchanged.

For imports created before this fix, reimport the original ZIP into a new folder
before combining browser datasets. Keep old imports and any frozen configurations
as historical evidence. Use one import version per source; never combine old and
corrected copies or partial and completed copies of the same collection. No
participant kit replacement or rerecording is needed for this coordinator fix.
The merge function rejects mixed, legacy or incompatible browser import schemes
with a reimport instruction; a single historical dataset can still be used alone.

MediaPipe Tasks Vision Web 1.1.0 and the checksum-pinned float16/1 hand model
produce world landmarks. The existing Python normalizer produces the 60 numeric
features. Using the same model and normalizer does not prove native/browser
equivalence: runtime, source/version, browser and acquisition conditions must be
reported. Final within-person comparisons must use identical held-out rows.
The kit does not run classifiers, enable LIVE or prove Studio workflow results.

## Rebuild (coordinator only)

`scripts/package_participant.py` uses ReportLab at build time. It embeds the
reviewed HTML/JS, verifies each downloaded SDK/model checksum, renders both
guides and writes ZIP hashes. ReportLab and the build script are not needed by
participants. Use the Codex bundled document runtime or a maintainer's existing
ReportLab environment; do not add it to the app's runtime dependencies.

Download the official `@mediapipe/tasks-vision` 1.1.0 npm tarball and verify its
SHA-512 integrity before reading the three files listed in the script. Package
integrity: `sha512-ZJqh0wMKOINorfSffvDAxzyO1//c+FiG3IkzOdNDnLqvBB3DbMfj0bB/tys2SNf9S914sgoIbIpF4HTOi336cg==`.
Use `assets/model_manifest.json` for the existing model URL and digest.
Store cache and outputs in ignored `.local/` directories:

```text
python scripts/package_participant.py --assets .local/participant-web-assets --model assets/hand_landmarker.task --output .local/participant-deliverables
node --test tests/participant_collector.test.mjs
python -m pytest tests/test_import_participant.py
```

The ZIPs intentionally share the same recorder; their instructions differ for
Windows/macOS. This avoids duplicating native Python runtimes and CPU-specific
Mac installers. A ZIP being small enough for an email provider is not guaranteed;
check the final file size and the recipient's attachment limit. Never split or
repackage the return dataset to fit an upload without preserving the original.
