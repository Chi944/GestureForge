# Run GestureForge Studio on Apple Silicon

This guide is for a marker or user with **Apple Silicon, macOS 13 Ventura or newer,
and native Python 3.11**. The marker's processor is confirmed; their macOS version
still needs checking. Intel Macs and Rosetta are outside this setup path.

The source ZIP includes the setup and launch scripts, **not Python or a bundled
application**. First setup requires internet and installs dependencies locally.
A Windows virtual environment cannot be used on a Mac.

The pinned dependencies passed a Windows-hosted
[Mac wheel-resolution check](project/macos-compatibility.json). That is dependency
resolution evidence, not a successful Mac installation or camera test. Native Mac
installation, camera operation and performance remain unverified.

## 1. Install and launch

Extract the source ZIP into a writable folder. Open Terminal in the folder
containing `pyproject.toml`, then check the operating system and Python:

```bash
sw_vers -productVersion
python3.11 -c 'import platform; print(platform.machine())'
```

The macOS version must be 13 or later and the Python command must print `arm64`.
If Python 3.11 is missing, install native Python 3.11. With
[Homebrew](https://formulae.brew.sh/formula/python@3.11) already installed, use
`brew install python@3.11`. Do not launch Terminal using Rosetta.

```bash
python3.11 scripts/setup_macos.py
bash run-studio.command
```

Setup creates `.venv`, installs the pinned dependencies, checks their consistency,
downloads the checksum-verified hand model and runs blank-image landmark inference.
It briefly opens and closes both application windows to check native Qt startup.
It does not open the camera or collect data. Run setup in an ordinary graphical
Terminal session, without setting `QT_QPA_PLATFORM=offscreen`.

If setup fails, retain the error and fix its reported cause before retrying. An
incompatible existing `.venv` must be renamed before setup; it is not deleted by
the script. Once setup succeeds, Finder can open `run-studio.command`. Use
`bash run-studio.command` in Terminal when you need to retain an error message.
The launcher handles folders containing spaces. `bash run.sh --studio` is equivalent.

## 2. Begin with the manual walkthrough

Studio opens in **Guest/manual** and **Preview**. No profile or webcam is required
to inspect the supplied deck, runbook or simulated actions.

1. Click **Open Setup**. Use **Load deck...** for
   `assets/corporate_demo_deck.json`, or **Load workspace...** for
   `assets/harbor_workspace.json` and its six-stage runbook.
2. Preview and Rehearsal simulate typed actions. To change cards or advance stages
   manually, select **Live** in **Studio action mode**, then **Apply and pause**.
3. Use **Manual browse / bookmarks** for Next, Previous and Bookmark, and
   **Runbook** for the stage instructions and Continue/Finish controls.
4. Use **Save session...** to save workspace progress. Load the same workspace
   before **Restore session...**. Restoring returns to paused Preview and does not
   replay launches; select Live explicitly again for manual actions.

**External application, file, folder and website launches are Windows-only in this
build.** On macOS, Preview/Rehearsal can simulate their requests; Live external
requests report an unsupported-platform reason. Internal cards, bookmarks and
runbook navigation are the Mac compatibility target. Do not present simulated
Calculator or Camera requests as native Mac launches.

## 3. Camera and personal gesture setup

**A connected camera alone does not enable Start camera control.** That button
needs a loaded recogniser. For a new user, **Open Enrolment → Request collection** starts
the collection camera without a recogniser. These are separate workflows.

First check the camera from the same Terminal used to launch Studio:

```bash
.venv/bin/python scripts/check_environment.py --camera --camera-index 0
```

Allow camera access if macOS asks. If access was denied, use **System Settings →
Privacy & Security → Camera** to enable the launching application shown there,
then quit and reopen it. Close FaceTime, Zoom and other camera applications before
retrying. This check processes five frames without saving images; a zero hand count
is not a successful recognition check.

Start with camera index **0**. If it selects the wrong camera, try **1**. In Studio,
set **Camera index**, then click **Use camera and pause** to apply it. Editing the
number alone does not apply it. Do not assume the Windows computer's camera index
matches the Mac.

For an existing consenting user's data, choose **Load personal dataset...** and
select their TRAIN `manifest.json`, or create/load a saved profile in **Profiles**.
Loading trains locally and leaves control paused. The source ZIP excludes private
P01 data. A supplied personal dataset can reproduce numeric results, but its model
is not qualified for a different person's hand.

For a new consenting user:

1. Click **Open Enrolment**. Enter a participant pseudonym, selected hand, TRAIN session,
   actual collection conditions and three distinct action poses plus NEUTRAL.
   The defaults are fist, thumb up, two fingers and open palm, stored as
   G1/G2/G3/NEUTRAL. Keep the default **12 trials per pose**.
2. Read and select the local numeric-data consent checkbox if you agree. Click
   **Request collection**, check the preview, then use **Begin trial** and follow
   the countdown/hold prompts. A complete session contains 48 trials.
3. After TRAIN, take a break and make a separate VALIDATION request with the same
   participant, hand and poses. Each request saves a new session folder under
   `data/local/enrolment/`; preserve both manifests and invalid detections.
4. In **Profiles**, enter a profile name and use **Browse dataset…** to select the
   completed TRAIN `manifest.json`. Check the selected hand, classifier and displayed
   rejection settings, confirm **Dataset permission confirmed**, then click
   **Create and load personal profile**. Do not select the VALIDATION manifest for
   training. Collection does not create or qualify a profile automatically; review
   validation separately before relying on that model.

Keep Studio and Enrolment in front while collecting. Leaving the tab, losing focus,
Pause or Esc stops collection. If saving fails, leave Studio open and use **Retry
save** after resolving folder access. Only numeric features and metadata are saved;
no photos or video are recorded. See the [user guide](USER_GUIDE.md#collect-in-studio)
for the complete collection and recovery workflow.

The marker can use this same route to create their own profile; no team member's
private data is required. Allow time for **48 TRAIN + 48 VALIDATION trials**, a
break and Practice, rather than treating the edited video as the full setup time.
Guest/manual remains available if personal recognition does not pass. The
[new-user demo segment](project/DEMO_SCENARIO.md#new-user-enrolment-showcase)
shows which steps to demonstrate and where to label time cuts.

## 4. Practice before personal Live control

With the recogniser loaded, Preview allows a simulated gesture check: explicitly
Start, show NEUTRAL until READY, then hold an action pose and return to NEUTRAL
before repeating. Confirm the displayed action mapping; gesture IDs do not always
mean the same action in every runbook stage.

**Open Practice** runs the measured personal check. It uses three trials for each
of the three action poses and NEUTRAL, plus ten negative/transition windows:
**22 five-second windows**, with preparation time in addition. Follow the
[Practice instructions](USER_GUIDE.md#personal-practice), including numeric-outcome
consent and the on-screen preparation prompts.

Only a complete, saved, reconciled pass in the current app session grants personal
Live eligibility. The short six-action readiness check and an imported old result
do not grant it. Practice always simulates. After a pass, explicitly select Live,
apply it, Start and show NEUTRAL. Changing the model, camera or action mappings can
expire eligibility; restarting Studio requires a fresh Practice pass. External
launches remain unsupported on Mac even after a pass.

## 5. Verify the destination Mac

After setup, optional reproducible software checks are:

```bash
.venv/bin/python -m pip check
.venv/bin/python scripts/check_environment.py --model
.venv/bin/python scripts/verify.py
```

The last command writes a fresh timestamped report under ignored
`experiments/local/`. It runs offscreen software checks, not a physical camera or
live-performance test. Keep its actual result and the Mac model/macOS version.

Before describing Mac operation as verified, check the normal graphical app:

- Manual cards, bookmarks, runbook navigation and save/restore behave as described.
- The intended camera produces a moving preview; pause/restart and close release it.
- Personal collection, loading and Practice work with the consenting user's data.
- A qualifying personal Live internal action occurs once per hold and needs NEUTRAL
  before repeating. Failed or interrupted Practice is recorded as such.
- After successful setup, internal viewer/camera operation works offline.
- A sustained session remains responsive. Record its duration and any errors;
  do not substitute Windows measurements for Mac results.

Until these checks are performed on an actual Mac, provide the marker with the
Windows demonstration video and recorded evidence alongside this source path,
without claiming equivalent native Mac verification.

References: [Qt macOS requirements](https://doc.qt.io/qt-6/macos.html),
[MediaPipe Python setup](https://developers.google.com/edge/mediapipe/solutions/setup_python),
[Apple camera permissions](https://support.apple.com/guide/mac-help/control-access-to-your-camera-mchlf6d108da/mac).
