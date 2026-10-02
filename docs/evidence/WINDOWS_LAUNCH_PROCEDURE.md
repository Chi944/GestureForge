# Windows verification procedure — GF-P05 and GF-P19

Status: prepared, NOT executed on either laptop in this environment. Do not mark
these cards Done from fake-adapter tests or Linux offscreen screenshots.

Use `python -m scripts.windows_launch_probe` from the [component guide](../COMPONENT_GUIDE.md). Preserve each
machine's actual JSON output under ignored `.local/`, along with pseudonymous
observer notes. Record source revision, `winver` result, Python version, actual
camera index, permissions, online/offline conditions, exact commands and visible
results. The probe records actual platform/package information, monotonic request
rows, shutdown acknowledgement, pause and observer confirmations. It does not
measure recogniser quality or total capture-frame throughput.

| Check, repeated on BOTH machines | Evidence required |
|---|---|
| Calculator | `launch_requested` plus the visible Calculator result; returning does not resume automatically |
| Camera | actual frame received first; worker interruption AND shutdown acknowledgement precede request; Camera visibly opens; manual return/close/resume reacquires capture |
| Reference file | permitted TXT or PDF opens in its associated app; launch acceptance and actual visible result recorded separately |
| Folder | configured existing local directory opens in File Explorer |
| HTTPS | configured credential-free HTTPS opens in default browser; online limitation and visible result recorded |
| Focus loss | launching/switching away pauses routing; returning remains paused; explicit resume succeeds |
| Missing target | bind a disposable TXT copy, move only that copy aside; clear failure, unchanged stage, restore/rebind and new manual request recover |
| Missing association | on an isolated test setup without the chosen permitted file association, record actual OS error and the manual/default-app recovery; do not change a user's existing associations merely for a test |
| Invalid input | `.cmd/.lnk/.url`, interpreter `.exe`, UNC/device/mapped network path, invalid scheme/credentials rejected without request |
| Camera timeout/error | if naturally encountered, record actual refusal and recovery; do not invent a timeout or treat an untested scenario as passed |
| Reload | local bindings and empty Quick Actions reload; no resource opens merely on load; progress/bookmarks restore paused in the integrated session |
| Duplicate/stale requests | use automated fake-adapter evidence; then verify long holds and stale context cancellation through the integrated shell, with all protections enabled |

Leave an unavailable check explicitly NOT RUN with a reason. OS codes differ by
association/device/configuration. Do not manufacture missing-association evidence
from a successful file opening. Observe whether Windows accepted a request but the
app subsequently failed; record both facts. Observer confirmations are self-report,
not an automatic application-ready test.

The isolated probe proves only the native/capture behaviour actually observed. It
does not complete GF-P10 shell integration, readiness, new-user recognition or the
six-stage system test. GF-P19 acceptance requires the integrated shell's current
snapshot, focus and recovery paths on both laptops, reviewed by Deston.
