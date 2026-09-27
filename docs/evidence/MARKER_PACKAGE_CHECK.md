# Private marker package verification

Checked on 27 September 2026 on the development Windows computer. This is archive/reproduction verification, not another physical laptop test.

- Source-only and private marker archives opened without ZIP integrity errors and matched their SHA256 JSON companions.
- Source-only archive contained no `data/local` entries. Private archive added exactly two: the authorised P01 manifest and its referenced numeric NPZ sidecar. No environment, downloaded model asset, raw camera image/video or event log was added.
- Both included the report review PDF and the partial recovered prompt appendix. Human review, missing prompt history and signatures remain open.
- The private ZIP was extracted under a path containing spaces. A separate existing Python environment imported `gestureforge` from the extracted source directory, not the main checkout.
- Running `python -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json` from that extracted copy reproduced macro-F1 **0.9686274509803923** for both kNN and SVM, with the same 31/32 trial confusion and 25/40 negative command-label acceptance limitation.
- `python -m gestureforge --smoke-test` passed from the extracted copy with offscreen Qt. No webcam or new participant samples were used.

Archive names and their current transfer checksums are under `releases/`; rebuild after final edits using [the release instructions](../../releases/README.md). Local full output remains in `.cache/Marker Package Check 20260927` and is excluded from GitHub. These results do not establish guide-only installation, pause/restart, offline webcam use or a signed complete submission.
