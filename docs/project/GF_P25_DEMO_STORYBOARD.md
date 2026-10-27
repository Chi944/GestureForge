# GestureForge presentation and demo storyboard

GF-P25 · Deston · 28 October 2026. The local PowerPoint now contains **14 core
slides and three hidden backup slides**, with a **600-second speaking plan** and
an embedded **60-second product highlight on slide 4**. The live product demo
follows the talk. The [Windows guide](GF_P25_WINDOWS_GUIDE_DRAFT.md) supplies the
full operating steps. PowerPoint and video deliverables stay local, not in Git.

The short highlight combines Javier's genuine 22 October manual walkthrough with
a labelled animation explaining gesture readiness. It shows request feedback and
post-restore state, not a new gesture qualification
or a complete release-matched demonstration. GF-P25 remains open until the
release dependency, guide review and final demonstration/playback review pass.

## The story

**A trainer has to keep explaining while moving between materials, applications
and audience questions. GestureForge keeps the prepared sequence, available
actions and return point visible, with optional personal gestures and manual
control.**

Suggested opening: “You are explaining a process. The next step needs Calculator,
then a reference file. Someone asks a question. When you return, what was next?
GestureForge puts that sequence and your place beside the demonstration.”

Make the payoff visible: prepare resources, personalise input, present, recover
and reuse. Custom gestures and application launching already exist elsewhere;
our take combines them with a contextual runbook and deliberate activation.
[Published research](RESEARCH_POSITIONING_2026_10_23.md) supports investigating
the problem. Customer demand, fewer mistakes and faster presentations are not
established product outcomes. There were no stakeholder interviews.

## Ten-minute presentation

The timings below match the current deck and total 600 seconds, including the
60-second narrated clip. Its slot allows five seconds of introduction. Slide
advances remain manual; the video starts automatically on slide 4. Gentle fades reveal content
without adding speaking clicks. Core scripts, longer answers and sources are in
speaker notes. Backup slides 15–17 are excluded from the timed talk.

Speaking roles below are a rehearsal proposal, not a contribution record or
completed attendance. Deston owns final direction, editing and review. Rehearse
the core to ten minutes as specified in the brief; keep the live demo separate.

| Time | Slide | Speaker and audience takeaway |
| --- | --- | --- |
| 0:00–0:20 | 1 · GestureForge Studio | **Deston:** introduce the presenter and the interrupted workflow. |
| 0:20–1:00 | 2 · The presenter loses the thread | **Deston:** explain resource coordination and recovery. Published research motivates the problem; it is not our customer survey. |
| 1:00–1:45 | 3 · A prepared route through the demo | **Deston:** connect the stage, linked resource and saved place to the pain point. |
| 1:45–2:50 | 4 · A one-minute product look | **Deston:** introduce genuine manual footage and the labelled gesture-readiness animation; let the embedded narration explain the visible actions. |
| 2:50–3:40 | 5 · Personal setup before gesture control | **Hau Jie:** explain Guest/manual, personal TRAIN/VALIDATION and Practice; no guaranteed pass for new users. |
| 3:40–4:35 | 6 · From camera frames to bounded actions | **Hau Jie:** attribute pretrained tracking and explain the team's features, classifiers and controller. |
| 4:35–5:25 | 7 · Two lightweight AI techniques | **Hau Jie:** compare kNN/SVM, shared preprocessing and session-separated selection. |
| 5:25–6:20 | 8 · Frozen TEST exposed recognition limits | **Hau Jie:** interpret each participant's starter/personal macro-F1 and retained misses. |
| 6:20–7:00 | 9 · Gesture readiness | **Javier:** show open palm/NEUTRAL for 300 ms until READY, fist/G1 for 400 ms, one action/LATCHED, then open palm to rearm. Explain explicit Start and current mode. |
| 7:00–7:45 | 10 · Protection reduced requests in replay | **Javier:** separate 0 versus 36 replay requests from the twenty-hold result and native launch evidence. |
| 7:45–8:30 | 11 · Useful responses, with visible limits | **Hau Jie:** show 16 responses/four misses and conditional latency without claiming a speed advantage. |
| 8:30–9:05 | 12 · Engineering a product that can recover | **Javier:** explain lifecycle, verification, recovery and remaining release evidence. |
| 9:05–9:35 | 13 · Three owners, one integration path | **Deston:** identify actual responsibilities and tools; each member can explain their own work. |
| 9:35–10:00 | 14 · The next step stays in view | **Deston:** return to the pain point and introduce the separate live demonstration. |

Hidden backups cover measurement boundaries, commercial fit/alternatives and
selected sources. They support questions rather than lengthening the core talk.

## The short highlight and separate live demonstration

The 60-second highlight gives 50 seconds to large genuine Studio footage.
Short captions and spoken explanation accompany the visible mode change, target
request feedback, restored summary, invalid HTTP rejection and correction to
HTTPS. A two-second opening and eight-second readiness illustration complete
the film. The UI fills most of the frame; paragraphs stay out of the video. The recorded source is manual operation. A separate, visibly labelled
readiness illustration shows NEUTRAL/READY, one command hold and neutral rearm.
The next slide and live demonstration explain the preceding personal profile,
Practice and explicit Live/Start steps. The supplied pose key remains open palm,
fist, thumb up and two raised fingers. This explains the workflow;
it does not claim a fresh recorded Practice pass. The clip does not show actual external
application openings or the restore click; captions and notes preserve those
limits. The clip includes local synthesized narration; its script and voice provenance
remain with the private edit files. Retain the
original footage and edit provenance privately. Do not use synthetic enrolment
footage as a real new-user recording.

After the talk, demonstrate the product directly using this sequence. Prepare
resources first and identify the actual build and runtime mode. The onboarding
step can be a guided explanation plus one real trial; full collection should not
consume the live presentation. Existing sessions and scores must be labelled.

| Live beat | What to show and explain |
| --- | --- |
| Personal onboarding | Start with Guest/manual, then show chosen hand, pose key, consent and actual conditions. Explain separate TRAIN/VALIDATION, saved profile and real Practice outcomes. |
| Deliberate input | Keep NEUTRAL/READY → command hold → one action/LATCHED → NEUTRAL continuous. Show the active mode and legend. |
| Resources in context | Navigate Harbor's six stages. Show actual Calculator, reference and folder openings, and separate task acknowledgements from launch requests. Answers: 240 credits and training coordinator. |
| Interruption and recovery | Bookmark a discussion point. Use only a disposable missing reference to demonstrate useful failure and explicit retry; never move genuine user files. |
| Resume without replay | Save and restore the session; show preserved stage/bookmark, paused Preview and no automatic launch. Re-enter Live explicitly if needed. |
| Beyond cards | Show Session summary, configured standalone Quick Actions and **Use Quick Actions**. Identify manual or gesture source for one safe approved request. |

The [Harbor scenario](DEMO_SCENARIO.md#six-stage-runbook) defines all six stages.
Show the three action poses, one held pose, rearm and pause where practical. If
recognition fails, use labelled manual controls and explain the limitation rather
than repeatedly retrying. A switch to recorded footage must be explicit. The
short highlight does not replace uncompleted device or release evidence.

### Enrolment footage and honest time cuts

The supplied pose key is **NEUTRAL = open palm; G1 = fist; G2 = thumb up;
G3 = index/middle fingers raised**. A custom profile uses its own recorded poses.
Show consent before collection and do not expose private identifiers or paths.

Caption the real full sessions: “TRAIN: 48 trials, 12 per pose” and, after an
actual break, “Separate VALIDATION: 48 trials, 12 per pose.” A few visible trials
do not replace the complete sessions. Create the profile from TRAIN. If showing
validation scores, show the retained offline evaluator report and label it
“Team-assisted offline validation”; Studio profile creation does not generate
this report automatically. Then show a real in-app Practice window and outcome.
The complete Practice protocol is 22 five-second windows plus preparation.
Do not edit separate attempts together or imply a new user is certain to pass.

Identify whether the demonstrated runtime uses an automated pass or **Manually
approved demo active**. Keep its mode visible. The selected P01 demonstration
has operator acceptance with an original automated **19/22** result; this is not
an automated 22/22 or transferable qualification for another user. A presenter
showing onboarding is not an independent new-user usability study.

## Feature and benefit on screen

| Feature | What makes the benefit visible |
| --- | --- |
| Contextual runbook | Show stage title, linked card and action legend together. “This stage offers the resource needed now.” Selecting a stage does not launch it. |
| Personal profiles | Show the selected name/hand and paused profile load. “Your examples configure recognition.” Do not imply it recognises every unenrolled user. |
| Deliberate activation | Keep the pose-to-action shot continuous. “Hold once, act once; neutral prepares the next request.” |
| Approved shortcuts | Show the request, actual opened app and human completion separately. Quick Actions demonstrates use without a deck/runbook. |
| Bookmark and restore | Return to the same discussion point, paused, without replay. This is the answer to the opening interruption. |
| Manual fallback | Show the visible button if recognition is unavailable; caption “Manual control.” The presenter can continue. |
| Local reuse | Diagram portable semantic workspace versus local targets/profile data. Do not display private numeric samples or claim security certification. |

## Evidence visuals

Use [GF-P20](P20_EVALUATION_2026_10_26.md) for these numbers and refresh the final
slides from accepted GF-P21/GF-P24 evidence before export.

- **Earlier twenty-hold recording:** 20 matching simulated actions, no extra or
  wrong commands. Keep it separate from the later capture; instruction cues did
  not establish physical onset.
- **Ten-minute non-command recording:** 0 protected actions versus 36 naive
  per-frame requests from the same recorded inputs. Label this replay/simulation,
  not proof of native-launch safety for every user.
- **Fresh visual recording:** show twenty tiles, **16 response / 4 miss**, with
  no duplicate/wrong commands. Never hide the misses behind a latency figure.
- **Successful-response p95:** show the **0.515–0.718 second interval**, labelled
  “16 successful attempts only; pose-frame onset to simulated dispatch.” Include
  camera timing uncertainty. This is not 95% of all attempts within one second.
- **Workflow:** M = 105.094 s and P = 165.844 s were assisted engineering
  walkthroughs with different builds, action counts and manual support. Do not
  use a racing bar chart or claim a paired speed advantage.

Use the verified methods report for classifier/frozen TEST figures. Keep
development validation, TEST, Practice and the demo's operator approval distinct.
No revenue, customer satisfaction or adoption numbers are inferred from footage.

## Visual and recording direction

Make real Studio footage the main visual. Use the application's navy, white and
mint palette, with amber for a limitation or recovery. Use one clear callout or
diagram per beat; enlarge relevant controls rather than showing a tiny desktop.
Keep mode, stage, prediction/action legend and outcome readable. Generated
illustrations can explain the problem, but cannot stand in for product evidence.

Explain intention before acting, then pause briefly for the audience to see the
outcome. Caption time cuts, simulation and manual actions. Keep gesture/response
shots uninterrupted; reserve edits for lengthy collection and setup. Use clear
narration and readable captions. Music is optional and must not obscure speech.
Avoid decorative animation that competes with the live action.

Prepare local targets and mappings before filming, test them manually and hide
unrelated windows/notifications. Obtain permission for identifiable people and
screens. Retain source/package identity, original footage and exported summaries
privately. Ordinary collection saves numeric data, not video. If a live attempt
fails, pause and use labelled manual control or recorded footage; briefly explain
the limitation instead of repeatedly retrying gestures on stage.

## What still completes GF-P25

The presentation, highlight and guide can be reviewed and rehearsed now.
Acceptance still needs GF-P23, the identified release's genuine demonstration
coverage, guide review and final playback review. Deston records/edits and approves the story. Hau Jie
checks recognition explanations/results; Javier checks Windows shortcut and
recovery explanations. Rehearse the speaking roles and ten-minute timing together.
No extra feature is required to tell this story; remaining work is verification,
recording and delivery.
