# GestureForge Licences and Source Attribution

Status: submission attribution snapshot. Package licence entries below are taken from the installed `.venv` metadata and `requirements.lock`; the raw evidence is saved in `docs/evidence/dependency-attribution.json`.

## Runtime and Development Components

| Component | Use in GestureForge | Installed evidence | Licence metadata recorded |
| --- | --- | --- | --- |
| Python | Runtime | Python 3.11.16 from `.venv`; bundled licence file at `.python/cpython-3.11.16-windows-x86_64-none/LICENSE.txt` | Python Software Foundation License Version 2 |
| PySide6 | Desktop widgets | `PySide6==6.11.2` in `requirements.lock`; `importlib.metadata` name `PySide6`, version `6.11.2` | `License: LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; installed licence file `pyside6-6.11.2.dist-info/licenses/LicenseRef-Qt-Commercial.txt` |
| opencv-contrib-python | Camera capture and image conversion | `opencv-contrib-python==5.0.0.93`; metadata name/version match | `License: Apache 2.0`; classifier `License :: OSI Approved :: Apache Software License`; installed `LICENSE.txt` and `LICENSE-3RD-PARTY.txt` files |
| MediaPipe Python package | Hand landmark runtime package | `mediapipe==1.0.1`; metadata name/version match | `License: Apache 2.0`; classifier `License :: OSI Approved :: Apache Software License`; installed `LICENSE` and `NOTICE` files |
| NumPy | Numeric arrays | `numpy==2.4.6`; metadata name/version match | `License-Expression: BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`; installed licence files recorded in evidence JSON |
| scikit-learn | kNN, SVM, scaling, and metrics | `scikit-learn==1.9.1`; metadata name/version match | `License-Expression: BSD-3-Clause`; installed `COPYING` and related licence files recorded |
| pytest | Automated tests | `pytest==9.1.1`; metadata name/version match | `License-Expression: MIT`; installed `LICENSE` file recorded |

`requirements.lock` contains 41 pinned Python packages. The full installed metadata snapshot records each locked package name, locked version, installed version, licence fields, licence classifiers, and discovered licence/notice file paths.

## Model Asset Attribution

GestureForge uses the MediaPipe Hand Landmarker task asset downloaded by `scripts/download_model.py`.

Recorded local asset evidence:

| Field | Value |
| --- | --- |
| Asset | MediaPipe Hand Landmarker |
| Asset version | `float16/1` |
| Download URL | `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task` |
| Source page | `https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker` |
| SHA256 | `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1` |
| Bytes | `7819105` |
| Distribution note | Retrieved from upstream during setup; not tracked in Git |

The local model manifest and download script do not contain an asset-specific licence field. Keep the source URL and checksum attribution with the submission, and do not describe the task asset as separately licensed unless that is verified from an official upstream source.

## Research and Technical References

- Zhang, F. et al. (2020). MediaPipe Hands: On-device Real-time Hand Tracking. https://arxiv.org/abs/2006.10214
- Wobbrock, J. O., Wilson, A. D., and Li, Y. (2007). Gestures without libraries, toolkits or training: a $1 recognizer for user interface prototypes. https://depts.washington.edu/acelab/proj/dollar/index.html
- Cover, T. and Hart, P. (1967). Nearest Neighbor Pattern Classification. https://isl.stanford.edu/~cover/papers/transIT/0021cove.pdf
- Cortes, C. and Vapnik, V. (1995). Support-vector networks. https://doi.org/10.1007/BF00994018
- NASA. 3.0 NASA Program/Project Life Cycle. https://www.nasa.gov/reference/3-0-nasa-program-project-life-cycle/

## Confirmed

- Installed package versions match `requirements.lock` for the recorded dependency evidence.
- Direct licence metadata for the main GestureForge runtime/test packages is recorded from installed package metadata, not planned-use wording.
- Installed licence/notice file paths are recorded for the locked Python package set where present.
- The MediaPipe model asset URL, source page, SHA256 checksum, byte size, and distribution note are recorded from `assets/model_manifest.json` and `scripts/download_model.py`.

## Unresolved

- This file records attribution evidence only; it does not assert legal compliance or interpret licence obligations.
- The MediaPipe Hand Landmarker task asset licence is not established by the local manifest or download script.
- Full third-party licence text has not been copied into this document; package licence file paths are preserved in `docs/evidence/dependency-attribution.json`.
