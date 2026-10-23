# GestureForge problem evidence and product positioning

Research completed 23 October 2026. This is secondary research, selected by
Deston in place of the proposed trainer interviews. It supports the problem,
design rationale and related work for GF-P26. It does not represent interviews
conducted by this team, customer approval or observed GestureForge performance.

## Conclusion and problem statement

GestureForge fits a prepared Windows demonstration that combines presentation
material, applications and reference resources. The problem is coordinating the
next resource and maintaining the demonstration's place while explaining a
process and responding to interruptions. The proposed solution is a reusable
runbook with visible actions, optional personal gestures, manual controls and
saved progress that restores without replaying launches.

The value to investigate is fewer resource-selection and recovery mistakes with
acceptable setup effort. Gesture input is one part of that proposition. The
current product does not automate tasks inside another application or control
PowerPoint. It cannot prevent external software crashes or make unreliable
recognition suitable for release. Published evidence below supports investigating
this problem; the effect of gesture input still requires the existing workflow evaluation.

## Research method and strength of evidence

We searched for live software-demonstration difficulties, application switching,
interruption recovery, mid-air fatigue, accidental gestures and current control
alternatives. Searches included `live software demonstration presenter survey`,
`task centric application switching`, `mid air interaction fatigue` and
`webcam custom gestures application launch`. We followed primary papers and
official product documentation rather than relying on generic productivity blogs.

The retained evidence comprises six research papers and seven official product
or documentation pages. Relevant methods, findings and limitations were inspected
for the papers. DemoWiz's survey subsection and Table 1 were checked using its
Microsoft-hosted paper after intermittent author-site failures. Product pages
establish advertised capabilities, not independently benchmarked reliability.
This is a focused review, not a systematic review or an exhaustive novelty search.
Older papers supply design evidence; their participants are not current market
samples. Versions of a paper are counted once. No competitor was installed or
purchased, and no source is treated as a GestureForge user test.

## Published needs and constraints

**Remembering the demonstration while speaking.** Chi, Lee and Drucker's DemoWiz
survey received 73 responses from a software company and university lab, including
60 respondents who had presented a software demo. Reported concerns included forgotten features,
timing and unexpected system problems. This is directly relevant to demonstrations,
although the historical convenience sample does not establish corporate demand.
Visible stages and rehearsal are our design response. [S1, survey and Table 1]

**Working across tools is sometimes necessary.** Jahanlou and colleagues
interviewed 15 knowledge workers and 11 people across five product teams.
Participants described tool-selection and learning difficulties, but also reasons
to retain different applications. GestureForge should organise access to existing
resources rather than claim that all switching is waste. These are qualitative
self-reports, not measured trainer productivity. [S2, sections 3, 5 and 8]

**Plans must tolerate questions and deviations.** Su and Wang studied live
programming instruction using TA interviews and lecturer observation. Prepared
notes, deviations and multitasking difficulties motivate visible steps and
explicit recovery. This is adjacent educational evidence, not corporate-trainer
validation. The manuscript's lecturer count and demographic table differ, so we
do not derive a combined participant total. [S3, sections 3–5]

**Recovery cues need testing in context.** Altmann and Trafton's four experiments
involved 96 undergraduates using an interrupted simulation. Cue effects depended
on preparation time; they were not uniformly beneficial. We therefore test
correct-stage recovery and actual timing rather than borrow their laboratory
effect size or promise a universal productivity gain. [S4, methods and results]

**Gestures can impose effort.** Hincapié-Ramos and colleagues evaluated arm fatigue
with 16 participants and then compared pointing conditions with 12 participants.
Their results favour some lower, bent-arm arrangements over extended positions.
This motivates intermittent commands and manual fallback. It does not validate
our poses, hold duration or accessibility for a particular person. [S5, validation,
interaction study and limitations]

**Ordinary movement can resemble commands.** Freeman and colleagues recorded 52
people in thirteen simulated living-room groups. Their recogniser analysis found
conflicts with background movement. That supports testing explanatory pointing
and movement as negatives, alongside deliberate arming and pause. Their sensor,
recogniser and setting differ from ours; their error rates are not our results.
[S6, sections 3, 4 and 6; author preprint]

## Existing alternatives

The last column is our interpretation of documented capabilities, not a measured
comparison. An absent feature on a reviewed page is not proof a product lacks it.

| Alternative | What the official source documents | Implication for GestureForge |
|---|---|---|
| PowerPoint Presenter View [S7] | Current/next slide, notes, timer and slide navigation. | Visible context already exists. Justifying another slide controller is weak. |
| Logitech Spotlight [S8] | Presentation navigation, pointing/highlighting and configurable functions, including gesture controls through its software. | Do not portray all clickers as NEXT/PREVIOUS only. A familiar remote may suit slide-only work. |
| Elgato Stream Deck Multi Actions [S9] | Ordered actions including app launching, delays and preparation/rehearsal of sequences. | Multi-application automation is established. Our emphasis is explicit demonstration stages and deliberate individual actions. |
| Stream Deck profiles [S10] | Reusable/shareable actions, hotkeys and multi-actions with device, OS and plugin requirements. | Profiles and reuse are not inventions here. Report our own rebinding and setup costs equally. |
| Windows Voice Access [S11] | App switching/opening and other voice controls on supported Windows 11, working offline after setup. | Hands-free and local operation are not exclusive benefits. Silent commands during narration are a hypothesis worth testing. |
| Touchless [S12] | Vendor advertises custom static/motion webcam gestures and keypress/app/voice mappings. | Close overlap rules out a custom-gesture/app-launch novelty claim. Product quality and adoption were not independently checked. |
| UCL MotionInput [S13] | Webcam-based Windows input, with lecturer PowerPoint use explicitly described. | Established presentation-control prior art. The versioned institutional page is historical, not a full inventory of today's spin-out product. |

## Commercial fit and limits

The plausible users are corporate software trainers, customer-onboarding
presenters and sales engineers repeating a configured walkthrough. A training or
enablement lead is a possible buyer; an author prepares the runbook and a
presenter operates it. These are proposed roles, not interviewed customers.

The potential organisational value is reusable preparation, consistent resource
selection and recoverable demonstrations. Local processing and semantic resource
slots may help teams reuse content while binding each laptop privately. They do
not establish security certification, regulatory compliance, willingness to pay
or measured savings. No market-size or revenue estimate is asserted.

The best-fit hypothesis is an occasional, rehearsed command between explanation
steps, within reliable camera framing, with manual control immediately available.
Slide-only talks, precision cursor work, sustained arm movement, poor camera
conditions and people unable to perform the poses comfortably may be better
served by existing controls. A commercial release would also need reliable
recognition, support and installation evidence that this development build does
not yet have. Do not add a chatbot, macro engine or analytics service to address
these gaps.

## From problem evidence to existing requirements

These are traceable design hypotheses, not proof the requirements are met. Their
pass rules remain those in [PROJECT_PLAN.md](PROJECT_PLAN.md).

| Need or constraint | Existing response | Evidence that can establish value or safety |
|---|---|---|
| Remember the next resource [S1–S3] | Visible stage/action legend and authored resource bindings; R07/R16/R21. | Correct six-stage outcomes; wrong-resource requests, help and retries in GF-P16/GF-P20. |
| Resume after an interruption [S3/S4] | Explicit paused restore and preserved progress/bookmarks; R05/R11/R16. | Correct restored position, no replayed launch, observed recovery under the existing task. |
| Avoid unexpected commands [S6] | Rejection, NEUTRAL/hold/latch, pause and simulation; R04/R11. | Existing long-hold/negative tests, live unwanted actions and same-stream replay. |
| Keep control comfortable [S5] | Optional personal poses, manual fallback and pause; R01/R13. | Existing comfort ratings, help, retries and fallback retained in outcome records. |
| Reuse a demonstration across laptops [S2/S10] | Portable semantic workspace with private local binding; R06/R12/R21. | Recipient rebinding, guide-only installation and actual resource outcomes. |

GF-P20 remains **M = Studio manual controls, S = standard starter gestures,
P = personal gestures** on the same supplied scenario. It isolates input choices
within Studio; it cannot independently establish that the runbook is better than
ordinary Windows navigation. It is not a clicker, Voice Access or Stream Deck
benchmark. Do not relabel conditions or add a new compulsory study. Report setup,
readiness and task time separately, preserve failed/unavailable conditions and
retain the original 900-second limit. A missing qualifying starter remains
unavailable. Optional observations about finding resources or recovery belong in
the existing observer notes, without inventing new timing data.

## Completed work and acceptance boundary

Completed: the secondary-research rationale, alternatives comparison and
need-to-requirement mapping. The local Word report and team instructions now use
this method. Trainer interviews are no longer assigned. This addresses the
problem-justification part of the marker feedback while explicitly leaving
direct stakeholder elicitation unperformed.

GF-P20 still needs actual workflow/hold/negative/latency evidence and its original
dependencies; GF-P26 still needs final release, report, video, declaration and
presentation review. Original weights and scoring remain unchanged. No remaining
whole task is closed by desk research alone: **151/223 (67.7%), 19/29 tasks**.

## Sources and inspected sections

All sources accessed 23 October 2026. Product claims are vendor/institutional
documentation. Publication years below belong to the papers, not search-engine
crawl dates.

- **S1** Chi, P.-Y., Lee, B., and Drucker, S. M. (2014). [DemoWiz](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/11/re-performing-software-demonstrations-for-a-live-presentation.pdf). CHI, pp. 1581–1590; DOI 10.1145/2556288.2557254. Survey subsection and Table 1; separate system-evaluation results are not used here.
- **S2** Jahanlou, A., Vermeulen, J., Grossman, T., Chilana, P. K., Fitzmaurice, G., and Matejka, J. (2023). [Task-Centric Application Switching](https://www.research.autodesk.com/app/uploads/2024/02/Task-Centric-Application-Switching_GI23.pdf). Graphics Interface. Methods §3, challenges §5, implications §7 and limitations §8.
- **S3** Su, X., and Wang, A. Y. (2025). [Live Coding in Programming Classes](https://arxiv.org/html/2506.03402v1). Author manuscript v1, 3 June; CHI EA DOI 10.1145/3706599.3719993. Methods §3, findings §4 and limitations §5.2.
- **S4** Altmann, E. M., and Trafton, J. G. (2004). [Task Interruption and Resumption Cues](https://www.interruptions.net/literature/Altmann-CogSci04.pdf). Cognitive Science Society proceedings. Four experiments and cue-availability discussion.
- **S5** Hincapié-Ramos, J. D., Guo, X., Moghadasian, P., and Irani, P. (2014). [Consumed Endurance](https://blog.jhincapie.com/wp-content/uploads/2010/02/ga-final.pdf). CHI, pp. 1063–1072; DOI 10.1145/2556288.2557130. Metric validation, pointing experiment and limitations.
- **S6** Freeman, D., Jota, R., Vogel, D., Wigdor, D., and Balakrishnan, R. (2015). [Naturally Occurring Background Activity](https://arxiv.org/html/1509.06109). Author preprint. Gesture conflicts §3, collection §4 and recogniser analysis §6.
- **S7** Microsoft. [Use Presenter View in PowerPoint](https://support.microsoft.com/en-us/powerpoint/training/use-presenter-view-in-powerpoint). Official feature documentation.
- **S8** Logitech. [Spotlight presentation remote](https://www.logitech.com/en-us/shop/p/spotlight-presentation-remote). Product controls and software-dependent functions.
- **S9** Elgato. [How to use Multi Actions](https://www.elgato.com/tw/en/explorer/products/stream-deck/how-to-use-multi-actions/). Official guide, updated 17 June 2026.
- **S10** Elgato. [Stream Deck profiles](https://docs.elgato.com/stream-deck/profiles/getting-started/). Profile capabilities, distribution and prerequisites.
- **S11** Microsoft. [Get started with Voice Access](https://support.microsoft.com/en-us/accessibility/windows/voice-access/get-started-with-voice-access). Windows 11 22H2+ support and offline operation.
- **S12** Touchless. [Official product page](https://touchless-control.com/). Advertised v1.1.9.2 custom gestures/actions; demonstrations are marked forthcoming in several sections.
- **S13** UCL. [Touchless computing with UCL MotionInput](https://www.ucl.ac.uk/engineering/computer-science/collaborate/ucl-industry-exchange-network-ucl-ixn/touchless-computing-ucl-motioninput-3). Versioned institutional description including lecturer use; not a current release benchmark.
