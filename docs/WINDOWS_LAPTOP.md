# Run GestureForge on another Windows laptop

## Studio project handoff

For current GF-P19/GF-P23 checks, use **gestureforge-studio-source.zip** and its
matching JSON checksum/commit record. The assignment archive named below is the
preserved earlier submission. Both source packages need Python and dependency
setup; the participant browser collection kits are different tools.

1. Extract the Studio ZIP into a fresh writable folder; follow the Python/setup
   instructions in section 2. Do not copy another laptop's environment or private
   profile/targets.
2. Open PowerShell in the extracted `gestureforge` folder and run
   `.\run.cmd --studio`. Double-clicking `run.cmd` without that option opens the
   assignment interface. For a software launch check use
   `.\run.cmd --studio --smoke-test`.
3. Use the [Studio controls](project/TEAM_GUIDE.md) and
   [Windows case procedure](evidence/WINDOWS_LAUNCH_PROCEDURE.md). Bind this
   laptop's local targets. Preview simulates; explicit Live permits manual
   actions. Live camera control requires the operator's valid current-session
   readiness grant. Do not repeat the assignment pilot collection below merely
   to run manual Studio cases.
4. Record the package hash, commit, operator/device and actual results using
   [Hau Jie's laptop-B brief](project/HAU_JIE_HANDOFF.md) and
   [Javier's device matrix](project/JAVIER_HANDOFF.md). Existing assignment/P02
   observations below do not establish a Studio release pass.

## Preserved assignment prototype instructions

Target: Intel/AMD Windows 10/11 with **64-bit Python 3.11**, a webcam and internet for first setup. [P02 feedback recorded in the consolidated results](evidence/RESULTS.md#p02-qualitative-feedback) reports successful ZIP use with a personal right-hand dataset on another laptop. On 29 September the user confirmed offline operation and camera pause/restart both passed. Exact package checksum, Windows version, camera index, dataset size and guide-only setup details are not recorded. Do not copy a `.venv` from another computer.

## 1. Transfer and extract

Copy `releases/gestureforge-assignment-source.zip` to the laptop, choose **Extract All**, and open the extracted `gestureforge` folder. Keep the entire folder together. A writable local folder such as `Documents\GestureForge` is suitable; spaces in its path are supported. Run from the extracted folder, not inside the ZIP.

Alternatively, clone the private repository's `main` branch using your own GitHub access. Git is not required to install or use the ZIP.

The source archive excludes private participant features, environments and downloaded model assets. Its JSON companion contains the archive's SHA256 for transfer verification. Compare it with:

```powershell
Get-FileHash .\gestureforge-assignment-source.zip -Algorithm SHA256
```

## 2. Install Python and dependencies

If Python 3.11 is already installed, check `py -3.11 --version`. Otherwise install the **Python Install Manager** from [Python's official Windows instructions](https://docs.python.org/3/using/windows.html), then use it to install the required runtime:

```powershell
pymanager install 3.11
py -3.11 -c "import sys, struct; print(sys.version); print(struct.calcsize('P') * 8)"
```

The output must show Python **3.11** and **64** bits. Newer Python minor versions are not the tested dependency combination.

Double-click **setup.cmd** in the extracted folder while online. It creates a local environment, installs pinned dependencies and downloads/checks the hand model with a blank-image native check before reporting success. Wait for `Setup complete`. It does not change the machine's persistent PowerShell execution policy.

If the Windows launcher cannot find Python, open PowerShell in the extracted folder and supply the real executable path:

```powershell
.\setup.cmd -PythonExe "C:\path\to\Python311\python.exe"
```

If installation fails, keep the displayed error and resolve it before continuing. Do not move or rename the folder after setup; virtual environments contain absolute paths. To install elsewhere, extract a fresh copy there and run setup again.

If setup reports an incompatible existing `.venv`, close GestureForge, rename that project-local folder to an unused name such as `.venv-old`, then rerun setup with the correct `-PythonExe`. Supplying a new executable does not replace an existing environment. Your `data` folder is separate and should be preserved.

If MediaPipe reports `get_runfiles_dir_helper.cc` or an inaccessible non-ASCII runtime path, keep the original folder and private files intact. Extract a fresh source copy to an ASCII-only writable destination such as `C:\GestureForge` and rerun setup there. Do not copy a `.venv` from the failing folder. Local review reproduced a native MediaPipe filename failure with Chinese characters in the old filename API; current model-byte loading and `check_environment.py --model` under a copied Chinese project folder both succeeded. The earlier fatal runtime error was not reproduced here and still needs a retest on Hau Jie's laptop.

## 3. Open and verify

Double-click **run.cmd**. The card viewer opens and supports manual Next/Pause controls. This first launch does not activate the camera because a source-only installation has no personal classifier data.

From PowerShell in the extracted folder, run the software and native-model checks:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_environment.py --model
.\.venv\Scripts\python.exe scripts/verify.py --timeout 1200 --output experiments/local/laptop-verification.json --synthetic-output experiments/local/laptop-synthetic.json
```

The model check runs real MediaPipe inference on a blank generated image without opening a webcam. The command above saves this laptop's checks under ignored `experiments/local/`, preserving the published historical records. Use a distinct filename for each date/device/run. `--timeout 1200` permits twenty minutes per check; a timeout is recorded as a failure with available output while later checks continue. The default is ten minutes per check. Synthetic evaluation is software evidence only.

## 4. Choose this laptop's webcam

Close Windows Camera, Teams, Zoom and other camera applications. Allow desktop camera access in Windows privacy settings and uncover the lens.

```powershell
.\.venv\Scripts\python.exe scripts/check_environment.py --camera --camera-index 0
```

If index 0 is unavailable or shows a different device, try index 1. Use the working index consistently below. The development computer used index 1; that is not a universal setting. A blank-image model pass does not prove the webcam works.

## 5. Enable personal gesture control

Gesture control requires genuine personal training data. The source ZIP intentionally does not include the locally consented P01 dataset. Do not upload participant features to GitHub. Existing participant data may only be transferred within its agreed permission; this package does not broaden that permission.

For fresh enrolment, follow [the collection protocol](DATA_COLLECTION.md). Obtain permission first. In the commands below choose the person's pseudonym, their hand and the verified camera index. `P02` is an example for a different participant; keep each person's data separate. The output folder must be new or already belong to that same person and hand.

```powershell
$camera = 0
$participant = 'P02'
$hand = 'Right'
.\.venv\Scripts\python.exe -m gestureforge.collect --camera $camera --split train --participant $participant --hand $hand --setup "laptop webcam, desk lighting, plain background" --consent --output data/local/pilot
.\.venv\Scripts\python.exe -m gestureforge.collect --camera $camera --split validation --participant $participant --hand $hand --setup "laptop webcam, separate validation session" --consent --output data/local/pilot
.\.venv\Scripts\python.exe -m gestureforge.collect --camera $camera --split validation_negative --participant $participant --hand $hand --setup "laptop webcam, unfamiliar poses" --consent --output data/local/pilot
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot-rejection.json --output experiments/local/laptop-pilot.json
.\run.cmd --dataset data/local/pilot/manifest.json --algorithm knn --multiplier 2 --margin 1.5 --camera $camera
```

Record eight trials per label in TRAIN and again in a separate VALIDATION session. The collection window guides each trial and saves numeric features only. Use clearly different, comfortable poses, for example open palm NEUTRAL and fist NEXT. Maintain the chosen hand and pose mapping in both sessions.

Multiplier 2 is the original P01 prototype setting, not an accuracy guarantee for another enrolment. Inspect the new validation results before relying on control; reject poor enrolment and improve its development data. Preserve the original assignment evidence separately. PREVIOUS and BOOKMARK remain recognition preview only.

Evaluation output files, including an optional verification `--synthetic-output`,
must use a new filename. An existing file is refused rather than replaced.
Omitting `--synthetic-output` keeps those software results in the verification report.

## 6. Physical laptop acceptance record

Record actual observations here or in a copy of this table against the exact package being accepted. P02's assisted-use report is qualitative evidence in `docs/evidence/RESULTS.md`; it lacks the package/environment details needed to complete this acceptance record. Do not mark these passed from the development computer or CI.

| Check | Observed result / date / tester |
| --- | --- |
| Laptop pseudonym, Windows version, CPU, Python version | Pending |
| ZIP checksum and clean setup using only these instructions | Pending |
| Manual viewer launch and first/last-card navigation | Pending |
| Dependency check, model check and automated verification | Pending |
| Working webcam index and chosen-hand detection | Pending |
| Personal dataset collected/available under permission; validation reviewed | Pending |
| Neutral arms; sustained NEXT hold advances exactly once | Pending |
| Neutral rearms; a second NEXT hold advances once | Pending |
| Pause/restart camera control | User confirmed passed on 29 September; exact test date and package not supplied |
| Camera released for another app and reacquired | Not separately reported |
| Offline runtime use after setup | User confirmed passed on 29 September; individual subchecks and package not supplied |

Initial setup requires internet. Runtime uses local assets/data; the disconnected-network row verifies that behaviour on the actual laptop. This is a source-based prototype, not an executable installer. Keep all November features and formal performance targets in the final-project plan.
