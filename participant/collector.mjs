export const PROTOCOL = "gestureforge-browser-development-v1";
export const MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1";
export const SOURCE_VERSION = "1.1.0";
export const RETENTION = "Delete after marking and appeals finish; team and private marker access only";
export const SAMPLE_OFFSETS = [0.2, 0.6, 1.0, 1.4, 1.8];
export const LABELS = ["NEUTRAL", "NEXT", "PREVIOUS", "BOOKMARK"];
export const UNKNOWN_PROMPTS = [
  "Keep both hands out of view.",
  "Show both hands at the same time.",
  "Show one index finger only.",
  "Show relaxed curled fingers.",
  "Show the back of your hand with bent fingers.",
  "Show ring and little fingers only.",
  "Move one curled hand slowly left and right.",
  "Rotate a curled hand away from the camera.",
];

const TRIALS_PER_LABEL = 12;
const ID_RE = /^[A-Za-z0-9][A-Za-z0-9_-]{0,23}$/;
const STORE_KEY = "gestureforge_participant_collector_v1";

export function validateParticipantId(value) {
  return ID_RE.test(value);
}

export function makeTrialPlan() {
  const trials = [];
  for (const split of ["train", "validation"]) {
    for (const label of LABELS) {
      for (let index = 1; index <= TRIALS_PER_LABEL; index += 1) {
        trials.push({
          split,
          label,
          trial_id: `${split}-${label}-${String(index).padStart(2, "0")}`,
          instruction: instructionFor(label),
        });
      }
    }
  }
  UNKNOWN_PROMPTS.forEach((prompt, index) => {
    trials.push({
      split: "validation_negative",
      label: "UNKNOWN",
      trial_id: `validation_negative-UNKNOWN-${String(index + 1).padStart(2, "0")}`,
      instruction: prompt,
    });
  });
  return trials;
}

export function instructionFor(label) {
  if (label === "NEUTRAL") return "Show an open palm.";
  if (label === "NEXT") return "Make a fist.";
  if (label === "PREVIOUS") return "Show a thumb up.";
  if (label === "BOOKMARK") return "Show index and middle fingers.";
  return "Avoid the enrolled action poses.";
}

export function sessionId(participantId, split) {
  return `${participantId}-${split}`;
}

export function makeSessions(participantId, trainConditions, validationConditions, sessionStartedAt = {}) {
  const conditions = {
    train: trainConditions,
    validation: validationConditions,
    validation_negative: validationConditions,
  };
  return ["train", "validation", "validation_negative"]
    .filter((split) => sessionStartedAt[split])
    .map((split) => ({
      session_id: sessionId(participantId, split),
      split,
      started_at: sessionStartedAt[split],
      conditions: conditions[split],
    }));
}

export function makeCollection({
  participantId,
  trainConditions,
  validationConditions,
  recordedAt,
  sessionStartedAt,
  records = [],
}) {
  return {
    schema_version: 1,
    protocol: PROTOCOL,
    participant_id: participantId,
    hand: "Right",
    source: {
      runtime: "mediapipe-tasks-vision-web",
      version: SOURCE_VERSION,
      model_sha256: MODEL_SHA256,
    },
    consent: {
      numeric_data: true,
      team_and_marker_access: true,
      retention: RETENTION,
      recorded_at: recordedAt,
    },
    sessions: makeSessions(participantId, trainConditions, validationConditions, sessionStartedAt),
    records,
  };
}

export function completedTrialIds(records) {
  const counts = new Map();
  for (const record of records) {
    const key = `${record.session_id}/${record.trial_id}`;
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return new Set([...counts].filter(([, count]) => count >= SAMPLE_OFFSETS.length).map(([key]) => key));
}

function maxFrameId(records) {
  return records.reduce((max, record) => Math.max(max, record.frame_id ?? 0), 0);
}

function nowSeconds() {
  return performance.timeOrigin / 1000 + performance.now() / 1000;
}

export class SampleScheduler {
  constructor(trial, startedSeconds) {
    this.trial = trial;
    this.startedSeconds = startedSeconds;
    this.records = [];
    this.usedFrames = new Set();
  }

  due(nowSeconds, observation, maxAgeSeconds = 0.2) {
    const elapsed = nowSeconds - this.startedSeconds;
    for (let index = this.records.length; index < SAMPLE_OFFSETS.length; index += 1) {
      if (elapsed < SAMPLE_OFFSETS[index]) break;
      this.records.push(this.#record(index, nowSeconds, observation, maxAgeSeconds));
    }
    return this.records;
  }

  finalize(reason = "missed_slot", finalSeconds = null) {
    while (this.records.length < SAMPLE_OFFSETS.length) {
      this.records.push(this.#invalid(this.records.length, reason, finalSeconds));
    }
    return this.records;
  }

  #record(sampleIndex, nowSeconds, observation, maxAgeSeconds) {
    const scheduledAt = this.startedSeconds + SAMPLE_OFFSETS[sampleIndex];
    if (!observation) return this.#invalid(sampleIndex, "no_observation");
    if (
      !Number.isFinite(observation.timestamp) ||
      nowSeconds - observation.timestamp > maxAgeSeconds ||
      Math.abs(observation.timestamp - scheduledAt) > maxAgeSeconds
    ) {
      return this.#invalid(sampleIndex, "stale_observation");
    }
    if (observation.frame_id != null && this.usedFrames.has(observation.frame_id)) {
      return this.#invalid(sampleIndex, "frame_already_used");
    }
    if (observation.frame_id != null) this.usedFrames.add(observation.frame_id);
    const landmarks = normalizeLandmarks(observation.landmarks);
    if (!landmarks) return this.#invalid(sampleIndex, observation.validity_reason || "invalid_landmarks");
    return {
      ...this.#base(sampleIndex, observation),
      landmarks,
      validity_reason: "",
    };
  }

  #invalid(sampleIndex, reason, timestamp = null) {
    const scheduledAt = this.startedSeconds + SAMPLE_OFFSETS[sampleIndex];
    return {
      ...this.#base(sampleIndex, null),
      timestamp: timestamp == null ? scheduledAt : Math.min(scheduledAt, timestamp),
      landmarks: null,
      validity_reason: reason,
    };
  }

  #base(sampleIndex, observation) {
    return {
      session_id: sessionId("PENDING", this.trial.split),
      trial_id: this.trial.trial_id,
      intended_label: this.trial.label,
      split: this.trial.split,
      sample_index: sampleIndex,
      timestamp: observation?.timestamp ?? Number.NaN,
      frame_id: observation?.frame_id ?? null,
      hand_count: observation?.hand_count ?? 0,
      hand: observation?.hand ?? null,
    };
  }
}

export function stampRecords(records, participantId) {
  return records.map((record) => ({
    ...record,
    session_id: sessionId(participantId, record.split),
    timestamp: Number.isFinite(record.timestamp) ? record.timestamp : 0,
  }));
}

export function normalizeLandmarks(landmarks) {
  if (!Array.isArray(landmarks) || landmarks.length !== 21) return null;
  const rows = landmarks.map((point) => {
    const row = Array.isArray(point) ? point : [point?.x, point?.y, point?.z];
    if (row.length !== 3 || !row.every(Number.isFinite)) return null;
    return row.map((value) => Number(value));
  });
  return rows.every(Boolean) ? rows : null;
}

export function collectionComplete(records) {
  return completedTrialIds(records).size >= makeTrialPlan().length;
}

export function collectionFileName(participantId, records) {
  return collectionComplete(records)
    ? `EMAIL_THIS_${participantId}_development.zip`
    : `EMAIL_THIS_${participantId}_PARTIAL_development.zip`;
}

export function cameraLoopActive(state, generation) {
  return Boolean(state.stream) && !state.paused && state.generation === generation;
}

const CRC_TABLE = new Uint32Array(256).map((_, n) => {
  let c = n;
  for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});

export function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

export function makeStoredZip(files) {
  const encoder = new TextEncoder();
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const [name, content] of Object.entries(files)) {
    const nameBytes = encoder.encode(name);
    const data = typeof content === "string" ? encoder.encode(content) : content;
    const crc = crc32(data);
    const local = concat(
      u32(0x04034b50), u16(20), u16(0), u16(0), u16(0), u16(0), u32(crc),
      u32(data.length), u32(data.length), u16(nameBytes.length), u16(0), nameBytes, data,
    );
    const central = concat(
      u32(0x02014b50), u16(20), u16(20), u16(0), u16(0), u16(0), u16(0), u32(crc),
      u32(data.length), u32(data.length), u16(nameBytes.length), u16(0), u16(0), u16(0),
      u16(0), u32(0), u32(offset), nameBytes,
    );
    locals.push(local);
    centrals.push(central);
    offset += local.length;
  }
  const centralBytes = concat(...centrals);
  const end = concat(
    u32(0x06054b50), u16(0), u16(0), u16(centrals.length), u16(centrals.length),
    u32(centralBytes.length), u32(offset), u16(0),
  );
  return concat(...locals, centralBytes, end);
}

export function readOwnCollectionZip(bytesLike) {
  const bytesIn = bytesLike instanceof Uint8Array ? bytesLike : new Uint8Array(bytesLike);
  const end = findSignature(bytesIn, 0x06054b50, Math.max(0, bytesIn.length - 66000));
  if (end < 0) throw new Error("ZIP end record was not found.");
  const entryCount = get16(bytesIn, end + 10);
  const centralOffset = get32(bytesIn, end + 16);
  if (entryCount !== 1) throw new Error("Return ZIP must contain exactly one file.");
  if (get32(bytesIn, centralOffset) !== 0x02014b50) throw new Error("Invalid ZIP central directory.");
  const method = get16(bytesIn, centralOffset + 10);
  const crc = get32(bytesIn, centralOffset + 16);
  const size = get32(bytesIn, centralOffset + 24);
  const nameLength = get16(bytesIn, centralOffset + 28);
  const extraLength = get16(bytesIn, centralOffset + 30);
  const commentLength = get16(bytesIn, centralOffset + 32);
  const localOffset = get32(bytesIn, centralOffset + 42);
  const name = new TextDecoder().decode(bytesIn.slice(centralOffset + 46, centralOffset + 46 + nameLength));
  if (name !== "collection.json") throw new Error("Return ZIP must contain collection.json only.");
  if (method !== 0) throw new Error("Compressed return ZIPs are not supported.");
  if (commentLength !== 0 || extraLength > 1024) throw new Error("Unexpected ZIP metadata.");
  if (get32(bytesIn, localOffset) !== 0x04034b50) throw new Error("Invalid ZIP local header.");
  const localNameLength = get16(bytesIn, localOffset + 26);
  const localExtraLength = get16(bytesIn, localOffset + 28);
  const dataStart = localOffset + 30 + localNameLength + localExtraLength;
  const data = bytesIn.slice(dataStart, dataStart + size);
  if (data.length !== size || crc32(data) !== crc) throw new Error("Return ZIP checksum failed.");
  return validateCollection(JSON.parse(new TextDecoder().decode(data)));
}

export function validateCollection(value) {
  if (!value || typeof value !== "object") throw new Error("collection.json must be an object.");
  if (value.schema_version !== 1 || value.protocol !== PROTOCOL) throw new Error("Unsupported collection protocol.");
  if (!validateParticipantId(value.participant_id) || value.hand !== "Right") throw new Error("Invalid participant or hand.");
  if (
    value.source?.runtime !== "mediapipe-tasks-vision-web" ||
    value.source?.version !== SOURCE_VERSION ||
    value.source?.model_sha256 !== MODEL_SHA256
  ) {
    throw new Error("Collection source does not match this collector.");
  }
  if (
    value.consent?.numeric_data !== true ||
    value.consent?.team_and_marker_access !== true ||
    value.consent?.retention !== RETENTION
  ) {
    throw new Error("Collection consent is incomplete.");
  }
  const splits = new Set(["train", "validation", "validation_negative"]);
  if (!Array.isArray(value.sessions) || value.sessions.length < 1 || value.sessions.length > 3) {
    throw new Error("Collection sessions are incomplete.");
  }
  const sessionSplits = new Set();
  for (const session of value.sessions) {
    if (!splits.has(session.split) || session.session_id !== sessionId(value.participant_id, session.split)) {
      throw new Error("Collection session identity is invalid.");
    }
    if (typeof session.conditions !== "string" || !session.conditions.trim()) throw new Error("Session conditions are missing.");
    sessionSplits.add(session.split);
  }
  if (!Array.isArray(value.records)) throw new Error("Collection records must be an array.");
  const slots = new Set();
  const frames = new Set();
  let previousTimestamp = -Infinity;
  for (const record of value.records) {
    validateRecord(record, value.participant_id, splits, sessionSplits);
    const slot = `${record.session_id}/${record.trial_id}/${record.sample_index}`;
    if (slots.has(slot)) throw new Error("Duplicate trial sample slot.");
    slots.add(slot);
    if (record.frame_id !== null) {
      const frame = `${record.session_id}/${record.frame_id}`;
      if (frames.has(frame)) throw new Error("Duplicate camera frame in records.");
      frames.add(frame);
    }
    if (record.timestamp < previousTimestamp) throw new Error("Record timestamps must be non-decreasing.");
    previousTimestamp = record.timestamp;
  }
  return value;
}

function validateRecord(record, participantId, splits, sessionSplits) {
  if (!record || typeof record !== "object") throw new Error("Record must be an object.");
  if (!splits.has(record.split) || record.session_id !== sessionId(participantId, record.split)) {
    throw new Error("Record split/session is invalid.");
  }
  if (!sessionSplits.has(record.split)) throw new Error("Record has no matching session.");
  if (!Number.isInteger(record.sample_index) || record.sample_index < 0 || record.sample_index >= SAMPLE_OFFSETS.length) {
    throw new Error("Record sample index is invalid.");
  }
  if (typeof record.trial_id !== "string" || typeof record.intended_label !== "string") {
    throw new Error("Record identity is incomplete.");
  }
  if (!Number.isFinite(record.timestamp) || !Number.isInteger(record.hand_count)) {
    throw new Error("Record timing/count is invalid.");
  }
  if (!(record.hand === "Right" || record.hand === "Left" || record.hand === null)) throw new Error("Record hand is invalid.");
  if (typeof record.validity_reason !== "string") throw new Error("Record validity reason is missing.");
  if (record.landmarks !== null && !normalizeLandmarks(record.landmarks)) throw new Error("Record landmarks are invalid.");
}

function u16(value) {
  return new Uint8Array([value & 0xff, (value >>> 8) & 0xff]);
}

function u32(value) {
  return new Uint8Array([value & 0xff, (value >>> 8) & 0xff, (value >>> 16) & 0xff, (value >>> 24) & 0xff]);
}

function get16(bytesIn, offset) {
  return bytesIn[offset] | (bytesIn[offset + 1] << 8);
}

function get32(bytesIn, offset) {
  return (bytesIn[offset] | (bytesIn[offset + 1] << 8) | (bytesIn[offset + 2] << 16) | (bytesIn[offset + 3] << 24)) >>> 0;
}

function findSignature(bytesIn, signature, start) {
  for (let offset = bytesIn.length - 4; offset >= start; offset -= 1) {
    if (get32(bytesIn, offset) === signature) return offset;
  }
  return -1;
}

function concat(...chunks) {
  const size = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const out = new Uint8Array(size);
  let cursor = 0;
  for (const chunk of chunks) {
    out.set(chunk, cursor);
    cursor += chunk.length;
  }
  return out;
}

if (typeof document !== "undefined") {
  boot().catch((error) => showFatal(error));
}

async function boot() {
  const el = ids();
  const state = {
    records: [],
    participantId: "",
    trainConditions: "",
    validationConditions: "",
    sessionStartedAt: {},
    consentRecordedAt: "",
    latest: null,
    frameId: 0,
    generation: 0,
    cameraStarting: false,
    collecting: false,
    lastVideoTime: -1,
    lastVideoChange: 0,
    paused: true,
    cameraReady: false,
    handLandmarker: null,
    stream: null,
  };
  restoreDraft(el, state);
  await listCameras(el);
  el.startCamera.onclick = () => startCamera(el, state);
  el.startCollection.onclick = () => startCollection(el, state);
  el.pause.onclick = () => pause(el, state, "Paused.");
  el.exportZip.onclick = () => exportZip(el, state);
  el.clearDraft.onclick = () => clearDraft(el, state);
  el.importZip.onchange = () => importZip(el, state);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pause(el, state, "Paused because the tab was hidden.");
  });
  renderProgress(el, state);
}

function ids() {
  const out = {};
  for (const id of [
    "participantId", "trainConditions", "validationConditions", "numericConsent",
    "accessConsent", "cameraSelect", "sessionSelect", "startCamera", "startCollection", "pause", "exportZip", "clearDraft", "importZip",
    "preview", "video", "cameraStatus", "collectionStatus", "instruction", "detail", "progress", "progressText",
  ]) out[id] = document.getElementById(id);
  return out;
}

async function listCameras(el) {
  const devices = await navigator.mediaDevices?.enumerateDevices?.().catch(() => []) ?? [];
  const cameras = devices.filter((device) => device.kind === "videoinput");
  el.cameraSelect.innerHTML = "";
  cameras.forEach((camera, index) => {
    const option = document.createElement("option");
    option.value = camera.deviceId;
    option.textContent = camera.label || `Camera ${index + 1}`;
    el.cameraSelect.append(option);
  });
}

export async function startCamera(el, state) {
  if (state.cameraStarting || state.collecting) return;
  const generation = state.generation + 1;
  state.generation = generation;
  state.cameraStarting = true;
  state.cameraReady = false;
  state.latest = null;
  el.startCollection.disabled = true;
  el.startCamera.disabled = true;
  try {
    stopCamera(state);
    if (!navigator.mediaDevices?.getUserMedia) throw new Error("This browser does not expose camera access from this page.");
    state.stream = await navigator.mediaDevices.getUserMedia({
      video: { deviceId: el.cameraSelect.value ? { exact: el.cameraSelect.value } : undefined },
      audio: false,
    });
    if (state.generation !== generation) {
      stopCamera(state);
      return;
    }
    state.stream.getVideoTracks().forEach((track) => {
      track.onended = () => pause(el, state, "Camera stopped. Completed records were kept.");
    });
    el.video.srcObject = state.stream;
    await el.video.play();
    if (state.generation !== generation || !state.stream) return;
    if (el.video.videoWidth && el.video.videoHeight) {
      el.preview.width = el.video.videoWidth;
      el.preview.height = el.video.videoHeight;
    }
    state.handLandmarker ??= await (state.createLandmarker?.() ?? createLandmarker());
    if (state.generation !== generation || !state.stream) return;
    state.lastVideoTime = -1;
    state.lastVideoChange = nowSeconds();
    state.cameraReady = true;
    state.paused = false;
    el.startCollection.disabled = false;
    el.pause.disabled = false;
    el.cameraStatus.textContent = "Camera ready. Keep your right hand in view when prompted.";
    requestAnimationFrame(() => cameraLoop(el, state, generation));
  } catch (error) {
    stopCamera(state);
    state.cameraReady = false;
    el.cameraStatus.textContent = `Camera unavailable: ${error.message}`;
  } finally {
    state.cameraStarting = false;
    el.startCamera.disabled = false;
  }
}

function stopCamera(state) {
  state.stream?.getTracks?.().forEach((track) => track.stop());
  state.stream = null;
  state.latest = null;
}

async function createLandmarker() {
  const { HandLandmarker } = await import(blobUrl("sdk", "text/javascript"));
  return HandLandmarker.createFromOptions(
    { wasmLoaderPath: blobUrl("loader", "text/javascript"), wasmBinaryPath: blobUrl("wasm", "application/wasm") },
    {
      baseOptions: { modelAssetBuffer: bytes("model"), delegate: "CPU" },
      runningMode: "VIDEO",
      numHands: 2,
    },
  );
}

function bytes(id) {
  return Uint8Array.from(atob(document.getElementById(id).textContent.trim()), (char) => char.charCodeAt(0));
}

function blobUrl(id, type) {
  return URL.createObjectURL(new Blob([bytes(id)], { type }));
}

function cameraLoop(el, state, generation) {
  if (!cameraLoopActive(state, generation)) return;
  if (el.video.currentTime === state.lastVideoTime) {
    if (nowSeconds() - state.lastVideoChange > 2) pause(el, state, "Camera paused because video frames stopped updating.");
    else requestAnimationFrame(() => cameraLoop(el, state, generation));
    return;
  }
  state.lastVideoTime = el.video.currentTime;
  state.lastVideoChange = nowSeconds();
  const ctx = el.preview.getContext("2d");
  ctx.drawImage(el.video, 0, 0, el.preview.width, el.preview.height);
  try {
    const capturedAt = nowSeconds();
    const result = state.handLandmarker.detectForVideo(el.video, performance.now());
    state.latest = observationFromResult(result, state.frameId += 1, capturedAt);
    el.cameraStatus.textContent = state.latest.hand_count === 1
      ? `${state.latest.hand ?? "Unknown"} hand detected${state.latest.hand === "Right" ? "." : " - use your right hand."}`
      : state.latest.hand_count > 1 ? "Multiple hands - keep only your right hand in view." : "No hand detected. Improve lighting and keep your whole right hand visible.";
  } catch (error) {
    pause(el, state, `Camera paused after tracking error: ${error.message}`);
    return;
  }
  requestAnimationFrame(() => cameraLoop(el, state, generation));
}

function observationFromResult(result, frameId, capturedAt) {
  const handCount = result.landmarks?.length ?? 0;
  const hand = result.handednesses?.[0]?.[0]?.categoryName ?? result.handedness?.[0]?.[0]?.categoryName ?? null;
  const worldLandmarks = handCount === 1 ? (result.worldLandmarks?.[0] ?? null) : null;
  return {
    timestamp: capturedAt,
    frame_id: frameId,
    hand_count: handCount,
    hand,
    landmarks: worldLandmarks,
    validity_reason: handCount === 1 && worldLandmarks ? "" : handCount === 0 ? "no_hand" : handCount > 1 ? "multiple_hands" : "missing_world_landmarks",
  };
}

export async function startCollection(el, state) {
  if (state.collecting) return;
  if (!validateForm(el, state)) return;
  state.paused = false;
  state.collecting = true;
  el.startCollection.disabled = true;
  el.exportZip.disabled = true;
  el.importZip.disabled = true;
  el.clearDraft.disabled = true;
  scrollToStatus(el);
  const generation = state.generation;
  const split = el.sessionSelect.value;
  state.sessionStartedAt[split] ??= new Date().toISOString();
  renderProgress(el, state);
  const done = completedTrialIds(state.records);
  const plan = makeTrialPlan().filter((trial) => {
    return trial.split === split && !done.has(`${sessionId(state.participantId, trial.split)}/${trial.trial_id}`);
  });
  for (const trial of plan) {
    if (state.paused || state.generation !== generation) break;
    await runTrial(el, state, trial, generation);
  }
  autosave(el, state);
  renderProgress(el, state);
  state.collecting = false;
  el.startCollection.disabled = !state.cameraReady;
  el.exportZip.disabled = false;
  el.importZip.disabled = false;
  el.clearDraft.disabled = false;
  if (!state.paused && state.generation === generation) {
    el.instruction.textContent = "Session complete";
    el.detail.textContent = "Select the next session when you are ready, or export the return ZIP.";
  }
}

function validateForm(el, state) {
  state.participantId = el.participantId.value.trim();
  state.trainConditions = el.trainConditions.value.trim();
  state.validationConditions = el.validationConditions.value.trim();
  const split = el.sessionSelect.value;
  if (!validateParticipantId(state.participantId)) return fail(el, "Enter a pseudonym such as P04 using letters, digits, hyphen or underscore.", el.participantId);
  if (split === "train" && !state.trainConditions) {
    return fail(el, "Enter TRAIN session condition notes before starting this section.", el.trainConditions);
  }
  if (split !== "train" && !state.validationConditions) {
    return fail(el, "Enter VALIDATION session condition notes before starting this section.", el.validationConditions);
  }
  if (!el.numericConsent.checked || !el.accessConsent.checked) {
    return fail(el, "Tick both consent boxes before collecting.", el.numericConsent.checked ? el.accessConsent : el.numericConsent);
  }
  if (!state.cameraReady) return fail(el, "Start the camera first.", el.startCamera);
  state.consentRecordedAt ||= new Date().toISOString();
  return true;
}

function fail(el, message, target = null) {
  el.detail.textContent = message;
  target?.focus?.();
  target?.scrollIntoView?.({ block: "center", behavior: "smooth" });
  return false;
}

function scrollToStatus(el) {
  el.collectionStatus?.scrollIntoView?.({ block: "start", behavior: "smooth" });
}

async function runTrial(el, state, trial, generation) {
  el.instruction.textContent = trial.instruction;
  el.detail.textContent = `${trial.split.toUpperCase()} ${trial.label}: get ready.`;
  await countdown(el, state, 3, generation);
  const scheduler = new SampleScheduler(trial, nowSeconds());
  el.detail.textContent = "Hold the pose steadily.";
  while (!state.paused && state.generation === generation && nowSeconds() - scheduler.startedSeconds < 2.05) {
    scheduler.due(nowSeconds(), state.latest);
    await sleep(40);
  }
  const records = scheduler.finalize(
    state.paused || state.generation !== generation ? "paused_before_sample" : "missed_slot",
    nowSeconds(),
  );
  state.records.push(...stampRecords(records, state.participantId));
  autosave(el, state);
  renderProgress(el, state);
  if (!state.paused && state.generation === generation) {
    el.detail.textContent = "Relax your hand.";
    await sleep(1000);
  }
}

async function countdown(el, state, seconds, generation) {
  for (let left = seconds; left > 0; left -= 1) {
    if (state.paused || state.generation !== generation) return;
    el.detail.textContent = `Starting in ${left}...`;
    await sleep(1000);
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function pause(el, state, message) {
  state.generation += 1;
  state.paused = true;
  el.instruction.textContent = "Paused";
  el.detail.textContent = message;
  stopCamera(state);
  state.cameraReady = false;
  el.pause.disabled = true;
  el.startCollection.disabled = true;
}

function renderProgress(el, state) {
  const complete = completedTrialIds(state.records).size;
  const total = makeTrialPlan().length;
  el.progress.value = complete / total;
  el.progressText.textContent = `${complete} / ${total} trials complete`;
  lockSettings(el, state);
}

function lockSettings(el, state) {
  el.participantId.disabled = Object.keys(state.sessionStartedAt).length > 0 || state.records.length > 0;
  el.trainConditions.disabled = Boolean(state.sessionStartedAt.train);
  el.validationConditions.disabled = Boolean(state.sessionStartedAt.validation || state.sessionStartedAt.validation_negative);
}

function autosave(el, state) {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify({
      participantId: el.participantId.value,
      trainConditions: el.trainConditions.value,
      validationConditions: el.validationConditions.value,
      sessionStartedAt: state.sessionStartedAt,
      consentRecordedAt: state.consentRecordedAt,
      records: state.records,
    }));
  } catch {
    el.detail.textContent = "Autosave unavailable. Export the ZIP before closing this page.";
  }
}

function restoreDraft(el, state) {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (!raw) return;
    const draft = JSON.parse(raw);
    el.participantId.value = draft.participantId || "";
    el.trainConditions.value = draft.trainConditions || "";
    el.validationConditions.value = draft.validationConditions || "";
    state.sessionStartedAt = draft.sessionStartedAt || {};
    state.consentRecordedAt = draft.consentRecordedAt || "";
    state.records = Array.isArray(draft.records) ? draft.records : [];
    state.frameId = maxFrameId(state.records);
    el.detail.textContent = "Recovered a local draft. Continue or export the current ZIP.";
  } catch {
    el.detail.textContent = "Local autosave could not be restored. Use a saved return ZIP, and download a backup before closing.";
  }
}

export function exportZip(el, state) {
  if (!validateFormForExport(el, state)) return;
  state.consentRecordedAt ||= new Date().toISOString();
  const recordedAt = state.consentRecordedAt;
  const collection = makeCollection({
    participantId: state.participantId,
    trainConditions: state.trainConditions,
    validationConditions: state.validationConditions,
    recordedAt,
    sessionStartedAt: state.sessionStartedAt,
    records: state.records,
  });
  const zip = makeStoredZip({ "collection.json": JSON.stringify(collection, null, 2) });
  const blob = new Blob([zip], { type: "application/zip" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = collectionFileName(state.participantId, state.records);
  link.click();
}

export async function importZip(el, state) {
  const file = el.importZip.files?.[0];
  if (!file) return;
  if (state.collecting || state.cameraStarting) return fail(el, "Pause and wait for the current trial to finish before importing.");
  if (state.stream) pause(el, state, "Paused before importing a backup ZIP.");
  const generation = state.generation + 1;
  state.generation = generation;
  try {
    if (file.size > 10 * 1024 * 1024) throw new Error("Return ZIP is larger than 10 MB.");
    const buffer = await file.arrayBuffer();
    if (state.generation !== generation) return;
    const collection = readOwnCollectionZip(buffer);
    el.participantId.value = collection.participant_id;
    el.numericConsent.checked = collection.consent.numeric_data;
    el.accessConsent.checked = collection.consent.team_and_marker_access;
    el.trainConditions.value = collection.sessions.find((row) => row.split === "train")?.conditions ?? "";
    el.validationConditions.value = (
      collection.sessions.find((row) => row.split === "validation") ??
      collection.sessions.find((row) => row.split === "validation_negative")
    )?.conditions ?? "";
    state.records = collection.records;
    state.participantId = collection.participant_id;
    state.trainConditions = el.trainConditions.value;
    state.validationConditions = el.validationConditions.value;
    state.sessionStartedAt = Object.fromEntries(collection.sessions.map((row) => [row.split, row.started_at]));
    state.consentRecordedAt = collection.consent.recorded_at;
    state.frameId = maxFrameId(state.records);
    autosave(el, state);
    renderProgress(el, state);
    el.detail.textContent = "Recovered records from the selected return ZIP.";
  } catch (error) {
    if (state.generation !== generation) return;
    el.detail.textContent = `Could not import ZIP: ${error.message}`;
  } finally {
    if (state.generation === generation) el.importZip.value = "";
  }
}

export function clearDraft(el, state) {
  if (state.collecting || state.cameraStarting) return fail(el, "Pause and wait for the current trial to finish before clearing.");
  if (state.records.length > 0 && !confirm("Only clear this after exporting a backup ZIP. Delete this local draft from this browser?")) return;
  if (state.stream) pause(el, state, "Paused before clearing the local draft.");
  try {
    localStorage.removeItem(STORE_KEY);
  } catch {
    return fail(el, "Browser storage is unavailable. Keep your return ZIP, then close this page to discard the in-memory recording.");
  }
  state.generation += 1;
  state.records = [];
  state.sessionStartedAt = {};
  state.consentRecordedAt = "";
  state.frameId = 0;
  el.numericConsent.checked = false;
  el.accessConsent.checked = false;
  el.participantId.value = "";
  el.trainConditions.value = "";
  el.validationConditions.value = "";
  el.importZip.value = "";
  renderProgress(el, state);
  el.detail.textContent = "Local draft cleared from this browser.";
}

export function validateFormForExport(el, state) {
  if (state.collecting || state.cameraStarting) return fail(el, "Pause and wait for the current trial to finish before exporting.");
  state.participantId = el.participantId.value.trim();
  state.trainConditions = el.trainConditions.value.trim();
  state.validationConditions = el.validationConditions.value.trim();
  if (!validateParticipantId(state.participantId)) return fail(el, "Enter a valid pseudonym before exporting.");
  if (!el.numericConsent.checked || !el.accessConsent.checked) return fail(el, "Tick both consent boxes before exporting.");
  if (state.records.length > 0 && makeCollection({
    participantId: state.participantId,
    trainConditions: state.trainConditions,
    validationConditions: state.validationConditions,
    recordedAt: new Date().toISOString(),
    sessionStartedAt: state.sessionStartedAt,
    records: state.records,
  }).sessions.length === 0) return fail(el, "Start at least one session before exporting collected records.");
  return true;
}

function showFatal(error) {
  const target = document.getElementById("detail") || document.body;
  target.textContent = `Collector failed to start: ${error.message}`;
}
