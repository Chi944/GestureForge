# Clean source installation

On 23 September 2026, the source ZIP was extracted into `.cache/release-smoke/gestureforge`. A new Python 3.11.16 environment was created at `.cache/release-env`, installed from the extracted `requirements.lock`, then installed the extracted application with `--no-deps -e`.

The updated source ZIP was extracted again after the model-v2 correction and tested using that isolated environment. The extracted copy passed lint, type checking, all 55 automated tests, offscreen GUI startup/shutdown and synthetic classifier evaluation. Exact commands and output are in `clean-install-verification.json`. Dependencies were unchanged; this rerun reused the separately installed environment rather than claiming another fresh dependency installation.

This verifies installation in a fresh environment on the development computer. It does not establish second-computer compatibility, physical camera operation, participant recognition performance or successful execution of the complete PowerShell setup script on another machine. The model asset is downloaded separately by setup; the source ZIP excludes local participant data and environments.
