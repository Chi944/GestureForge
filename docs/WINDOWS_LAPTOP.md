# Run GestureForge on another Windows laptop

Target: Intel/AMD Windows 10/11 with **64-bit Python 3.11**, a webcam and internet for first setup. [P02 feedback recorded on 26 September](evidence/P02_LAPTOP_TEST.md) reports successful assisted ZIP use with a personal right-hand dataset on another laptop. Exact package/environment details, guide-only installation, pause/restart, camera release/reopen and disconnected-network checks remain open. Do not copy a `.venv` from another computer.

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

Double-click **setup.cmd** in the extracted folder while online. It creates a local environment, installs pinned dependencies and downloads/checks the hand model. Wait for `Setup complete`. It does not change the machine's persistent PowerShell execution policy.

If the Windows launcher cannot find Python, open PowerShell in the extracted folder and supply the real executable path:

```powershell
.\setup.cmd -PythonExe "C:\path\to\Python311\python.exe"
```

If installation fails, keep the displayed error and resolve it before continuing. Do not move or rename the folder after setup; virtual environments contain absolute paths. To install elsewhere, extract a fresh copy there and run setup again.

If setup reports an incompatible existing `.venv`, close GestureForge, rename that project-local folder to an unused name such as `.venv-old`, then rerun setup with the correct `-PythonExe`. Supplying a new executable does not replace an existing environment. Your `data` folder is separate and should be preserved.

## 3. Open and verify

Double-click **run.cmd**. The card viewer opens and supports manual Next/Pause controls. This first launch does not activate the camera because a source-only installation has no personal classifier data.

From PowerShell in the extracted folder, run the software and native-model checks:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_environment.py --model
.\.venv\Scripts\python.exe scripts/verify.py
```

The model check runs real MediaPipe inference on a blank generated image without opening a webcam. `verify.py` writes `docs/evidence/verification.json` on this laptop. Keep a copy labelled with its date and computer pseudonym; synthetic evaluation is software evidence only.

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
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/laptop-pilot.json
.\run.cmd --dataset data/local/pilot/manifest.json --algorithm knn --multiplier 2 --camera $camera
```

Record eight trials per label in TRAIN and again in a separate VALIDATION session. The collection window guides each trial and saves numeric features only. Use clearly different, comfortable poses, for example open palm NEUTRAL and fist NEXT. Maintain the chosen hand and pose mapping in both sessions.

Multiplier 2 is the original P01 prototype setting, not an accuracy guarantee for another enrolment. Inspect the new validation results before relying on control; reject poor enrolment and improve its development data. Preserve the original assignment evidence separately. PREVIOUS and BOOKMARK remain recognition preview only.

## 6. Physical laptop acceptance record

Record actual observations here or in a copy of this table against the exact package being accepted. [P02's assisted-use report](evidence/P02_LAPTOP_TEST.md) is separate qualitative evidence; it lacks the package/environment details needed to complete this acceptance record. Do not mark these passed from the development computer or CI.

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
| Pause blocks gesture actions; reopening releases/reacquires camera | Pending |
| After setup, disconnect Wi-Fi/network and repeat viewer, model and live checks | Pending |

Initial setup requires internet. Runtime uses local assets/data; the disconnected-network row verifies that behaviour on the actual laptop. This is a source-based prototype, not an executable installer. Keep all November features and formal performance targets in the final-project plan.
