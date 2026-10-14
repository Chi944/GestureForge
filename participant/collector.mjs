export const PROTOCOL = "gestureforge-browser-development-v1";
export const TEST_PROTOCOL = "gestureforge-browser-test-v1";
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

export function validateTestTicket(ticket) {
  const keys = ["schema_version", "protocol", "paired_protocol", "target_participant", "config_fingerprint", "frozen_integrity_sha256", "pose_set_id", "hand"];
  if (!ticket || typeof ticket !== "object" || Object.keys(ticket).sort().join() !== keys.sort().join() ||
      ticket.schema_version !== 1 || ticket.protocol !== TEST_PROTOCOL ||
      ticket.paired_protocol !== "gf-p18-positive-test-v1" || ticket.pose_set_id !== "standard-v1" ||
      ticket.hand !== "Right" || typeof ticket.target_participant !== "string" || !validateParticipantId(ticket.target_participant) ||
      typeof ticket.config_fingerprint !== "string" || typeof ticket.frozen_integrity_sha256 !== "string" ||
      !/^[a-f0-9]{64}$/.test(ticket.config_fingerprint) || !/^[a-f0-9]{64}$/.test(ticket.frozen_integrity_sha256)) {
    throw new Error("Invalid frozen TEST ticket.");
  }
  return ticket;
}

function ticketsMatch(found, expected) {
  return found && Object.keys(found).length === Object.keys(expected).length &&
    Object.keys(expected).every((key) => found[key] === expected[key]);
}

export function draftStorageKey(ticket = null) {
  return ticket ? `${STORE_KEY}_test_${ticket.target_participant}_${ticket.config_fingerprint}_${ticket.frozen_integrity_sha256}` : STORE_KEY;
}

export function makeTrialPlan(ticket = null) {
  if (ticket) validateTestTicket(ticket);
  const trials = [];
  for (const split of ticket ? ["test"] : ["train", "validation"]) {
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
  if (!ticket) UNKNOWN_PROMPTS.forEach((prompt, index) => {
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

export function sessionId(participantId, split, ticket = null) {
  return `${participantId}-${split}${ticket ? `-${ticket.config_fingerprint.slice(0, 32)}` : ""}`;
}

export function makeSessions(participantId, trainConditions, validationConditions, sessionStartedAt = {}, ticket = null) {
  const conditions = {
    train: trainConditions,
    validation: validationConditions,
    validation_negative: validationConditions,
    test: trainConditions,
  };
  return (ticket ? ["test"] : ["train", "validation", "validation_negative"])
    .filter((split) => sessionStartedAt[split])
    .map((split) => ({
      session_id: sessionId(participantId, split, ticket),
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
  testTicket = null,
}) {
  if (testTicket) {
    validateTestTicket(testTicket);
    if (participantId !== testTicket.target_participant) throw new Error("Participant does not match the frozen TEST ticket.");
  }
  return {
    schema_version: 1,
    protocol: testTicket ? TEST_PROTOCOL : PROTOCOL,
    ...(testTicket ? { test_ticket: testTicket } : {}),
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
    sessions: makeSessions(participantId, trainConditions, validationConditions, sessionStartedAt, testTicket),
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

export function stampRecords(records, participantId, ticket = null) {
  return records.map((record) => ({
    ...record,
    session_id: sessionId(participantId, record.split, ticket),
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

export function collectionComplete(records, ticket = null) {
  return completedTrialIds(records).size >= makeTrialPlan(ticket).length;
}

export function collectionFileName(participantId, records, ticket = null) {
  const purpose = ticket ? "test" : "development";
  return collectionComplete(records, ticket)
    ? `EMAIL_THIS_${participantId}_${purpose}.zip`
    : `EMAIL_THIS_${participantId}_PARTIAL_${purpose}.zip`;
}

function firstUnfinishedSplit(participantId, records, ticket = null) {
  const done = completedTrialIds(records);
  return (ticket ? ["test"] : ["train", "validation", "validation_negative"]).find((split) => {
    return makeTrialPlan(ticket)
      .some((trial) => trial.split === split && !done.has(`${sessionId(participantId, split, ticket)}/${trial.trial_id}`));
  }) ?? null;
}

function splitLabel(split) {
  if (split === "validation_negative") return "UNKNOWN";
  return split.toUpperCase();
}

function selectResumeSplit(el, state) {
  const split = firstUnfinishedSplit(state.participantId, state.records, state.testTicket);
  if (split) el.sessionSelect.value = split;
  return split;
}

function remainingTrialCount(participantId, records, split = null, ticket = null) {
  const done = completedTrialIds(records);
  return makeTrialPlan(ticket).filter((trial) => {
    return (!split || trial.split === split) && !done.has(`${sessionId(participantId, trial.split, ticket)}/${trial.trial_id}`);
  }).length;
}

function resumeMessage(state, nextSplit, prefix) {
  if (!nextSplit) return `All ${makeTrialPlan(state.testTicket).length} trials are complete. Export the return ZIP.`;
  const action = state.testTicket
    ? state.cameraReady ? `Resume ${remainingTrialCount(state.participantId, state.records, "test", state.testTicket)} trials` : "Open camera, check your preview, then resume the trials"
    : state.cameraReady ? "Start Selected Session" : "Start Camera and Start Selected Session";
  const section = splitLabel(nextSplit);
  const sectionRemaining = remainingTrialCount(state.participantId, state.records, nextSplit, state.testTicket);
  const totalRemaining = remainingTrialCount(state.participantId, state.records, null, state.testTicket);
  if (nextSplit === "validation" && !state.sessionStartedAt.validation && !state.sessionStartedAt.validation_negative) {
    return `${prefix}. ${sectionRemaining} ${section} trials remaining (${totalRemaining} total). After a break, enter actual VALIDATION notes, then ${action}.`;
  }
  return `${prefix}. ${sectionRemaining} ${section} trials remaining (${totalRemaining} total). ${action} to continue ${section}.`;
}

function recoveryPrefix(state, nextSplit) {
  if (nextSplit === "validation" && state.sessionStartedAt.validation) return "Recovered VALIDATION";
  if (nextSplit === "validation" && state.sessionStartedAt.train) return "Recovered TRAIN";
  if (nextSplit === "validation_negative" && state.sessionStartedAt.validation_negative) return "Recovered UNKNOWN";
  if (nextSplit === "validation_negative" && state.sessionStartedAt.validation) return "Recovered VALIDATION";
  return "Recovered draft";
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

export function readOwnCollectionZip(bytesLike, ticket = null) {
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
  return validateCollection(JSON.parse(new TextDecoder().decode(data)), ticket);
}

export function validateCollection(value, ticket = null) {
  if (!value || typeof value !== "object") throw new Error("collection.json must be an object.");
  if (value.schema_version !== 1 || value.protocol !== (ticket ? TEST_PROTOCOL : PROTOCOL)) throw new Error("Unsupported collection protocol.");
  if (ticket) {
    validateTestTicket(ticket);
    if (!ticketsMatch(value.test_ticket, ticket) || value.participant_id !== ticket.target_participant) {
      throw new Error("Collection does not match this frozen TEST ticket.");
    }
  } else if (value.test_ticket !== undefined) throw new Error("Development collections cannot contain a TEST ticket.");
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
  const splits = new Set(ticket ? ["test"] : ["train", "validation", "validation_negative"]);
  if (!Array.isArray(value.sessions) || value.sessions.length < 1 || value.sessions.length > splits.size) {
    throw new Error("Collection sessions are incomplete.");
  }
  const sessionSplits = new Set();
  for (const session of value.sessions) {
    if (!splits.has(session.split) || session.session_id !== sessionId(value.participant_id, session.split, ticket) || sessionSplits.has(session.split)) {
      throw new Error("Collection session identity is invalid.");
    }
    if (typeof session.conditions !== "string" || !session.conditions.trim()) throw new Error("Session conditions are missing.");
    sessionSplits.add(session.split);
  }
  if (!Array.isArray(value.records)) throw new Error("Collection records must be an array.");
  const slots = new Set();
  const frames = new Set();
  const trialCounts = new Map();
  const testPlan = ticket ? new Map(makeTrialPlan(ticket).map((trial) => [trial.trial_id, trial.label])) : null;
  let previousTimestamp = -Infinity;
  for (const record of value.records) {
    validateRecord(record, value.participant_id, splits, sessionSplits, ticket);
    if (testPlan && testPlan.get(record.trial_id) !== record.intended_label) throw new Error("Record does not match the frozen TEST trial plan.");
    trialCounts.set(record.trial_id, (trialCounts.get(record.trial_id) ?? 0) + 1);
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
  if (ticket && [...trialCounts.values()].some((count) => count !== SAMPLE_OFFSETS.length)) {
    throw new Error("TEST trials must preserve all five sample slots, including invalid slots.");
  }
  return value;
}

function validateRecord(record, participantId, splits, sessionSplits, ticket = null) {
  if (!record || typeof record !== "object") throw new Error("Record must be an object.");
  if (!splits.has(record.split) || record.session_id !== sessionId(participantId, record.split, ticket)) {
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
  const ticketText = document.getElementById("testTicket")?.textContent;
  const testTicket = ticketText ? Object.freeze(validateTestTicket(JSON.parse(ticketText))) : null;
  const state = {
    testTicket,
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
  if (testTicket) {
    el.participantId.value = testTicket.target_participant;
    state.participantId = testTicket.target_participant;
  }
  restoreDraft(el, state);
  el.startCamera.onclick = () => startCamera(el, state);
  el.startCollection.onclick = () => startCollection(el, state);
  if (el.quickStart) el.quickStart.onclick = () => quickStart(el, state);
  el.pause.onclick = () => pause(el, state, "Paused.");
  el.exportZip.onclick = () => exportZip(el, state);
  el.clearDraft.onclick = () => clearDraft(el, state);
  el.importZip.onchange = () => importZip(el, state);
  el.cameraSelect.onchange = () => changeCamera(el, state);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pause(el, state, "Paused because the tab was hidden.");
  });
  renderProgress(el, state);
  void listCameras(el, state);
}

function ids() {
  const out = {};
  for (const id of [
    "participantId", "trainConditions", "validationConditions", "numericConsent",
    "accessConsent", "cameraSelect", "sessionSelect", "startCamera", "startCollection", "pause", "exportZip", "clearDraft", "importZip",
    "preview", "video", "cameraStatus", "collectionStatus", "instruction", "detail", "progress", "progressText", "quickStart",
  ]) out[id] = document.getElementById(id);
  return out;
}

async function listCameras(el, state) {
  const generation = state.generation;
  const devices = await navigator.mediaDevices?.enumerateDevices?.().catch(() => []) ?? [];
  if (state.generation !== generation) return;
  const cameras = devices.filter((device) => device.kind === "videoinput");
  if (!cameras.length) return;
  const selected = state.stream?.getVideoTracks?.()[0]?.getSettings?.().deviceId || el.cameraSelect.value;
  el.cameraSelect.innerHTML = "";
  const automatic = document.createElement("option");
  automatic.value = "";
  automatic.textContent = "Default camera";
  el.cameraSelect.append(automatic);
  cameras.forEach((camera, index) => {
    const option = document.createElement("option");
    option.value = camera.deviceId;
    option.textContent = camera.label || `Camera ${index + 1}`;
    el.cameraSelect.append(option);
  });
  el.cameraSelect.value = cameras.some(camera => camera.deviceId === selected) ? selected : "";
}

export function changeCamera(el, state) {
  if (state.testTicket) pause(el, state, "Camera selection changed.");
}

export function renderQuickStart(el, state) {
  if (!el.quickStart || !state.testTicket) return;
  const remaining = remainingTrialCount(state.testTicket.target_participant, state.records, "test", state.testTicket);
  el.quickStart.disabled = !remaining || Boolean(state.cameraStarting || state.collecting || state.importing);
  el.quickStart.textContent = !remaining ? "All 48 trials complete"
    : state.cameraStarting ? "Opening camera..."
    : state.collecting ? "Recording..."
    : state.importing ? "Recovering recording..."
    : !state.cameraReady ? "Open camera"
    : remaining === 48 ? "Start 48 trials" : `Resume ${remaining} trials`;
}

export async function quickStart(el, state) {
  if (!state.testTicket || state.cameraStarting || state.collecting || state.importing ||
      !remainingTrialCount(state.testTicket.target_participant, state.records, "test", state.testTicket)) return;
  if (state.cameraReady) await startCollection(el, state);
  else await startCamera(el, state);
}

export async function startCamera(el, state) {
  if (state.cameraStarting || state.collecting || state.importing) return;
  if (state.testTicket && (!el.numericConsent.checked || !el.accessConsent.checked)) {
    return fail(el, "Tick both consent boxes before opening the camera.", el.numericConsent.checked ? el.accessConsent : el.numericConsent);
  }
  const generation = state.generation + 1;
  state.generation = generation;
  state.cameraStarting = true;
  state.cameraReady = false;
  state.latest = null;
  el.startCollection.disabled = true;
  el.startCamera.disabled = true;
  renderQuickStart(el, state);
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
    if (state.testTicket) {
      el.instruction.textContent = "Check your camera preview";
      el.detail.textContent = "Keep your whole right hand visible. Click the blue button to start or resume the trials when ready.";
    }
    requestAnimationFrame(() => cameraLoop(el, state, generation));
    void listCameras(el, state);
  } catch (error) {
    stopCamera(state);
    state.cameraReady = false;
    el.cameraStatus.textContent = `Camera unavailable: ${error.message}`;
  } finally {
    state.cameraStarting = false;
    el.startCamera.disabled = false;
    renderQuickStart(el, state);
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
  if (state.collecting || state.cameraStarting || state.importing) return;
  if (!validateForm(el, state)) return;
  const split = el.sessionSelect.value;
  const done = completedTrialIds(state.records);
  const plan = makeTrialPlan(state.testTicket).filter((trial) => {
    return trial.split === split && !done.has(`${sessionId(state.participantId, trial.split, state.testTicket)}/${trial.trial_id}`);
  });
  if (plan.length === 0) {
    const next = selectResumeSplit(el, state);
    renderProgress(el, state);
    el.detail.textContent = resumeMessage(state, next, `${splitLabel(split)} is already complete`);
    return;
  }
  state.paused = false;
  state.collecting = true;
  el.startCollection.disabled = true;
  el.exportZip.disabled = true;
  el.importZip.disabled = true;
  el.clearDraft.disabled = true;
  scrollToStatus(el);
  const generation = state.generation;
  state.sessionStartedAt[split] ??= new Date().toISOString();
  renderProgress(el, state);
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
  renderQuickStart(el, state);
  if (!state.paused && state.generation === generation) {
    const next = selectResumeSplit(el, state);
    el.instruction.textContent = "Session complete";
    el.detail.textContent = resumeMessage(state, next, `${splitLabel(split)} complete`);
  }
}

function validateForm(el, state) {
  state.participantId = el.participantId.value.trim();
  state.trainConditions = el.trainConditions.value.trim();
  state.validationConditions = el.validationConditions.value.trim();
  const split = el.sessionSelect.value;
  if (state.testTicket && (state.participantId !== state.testTicket.target_participant || split !== "test")) {
    return fail(el, "Use the participant and TEST session assigned by this kit.", el.participantId);
  }
  if (!validateParticipantId(state.participantId)) return fail(el, "Enter a pseudonym such as P04 using letters, digits, hyphen or underscore.", el.participantId);
  if (split === "train" && !state.trainConditions) {
    return fail(el, `Enter ${split.toUpperCase()} session condition notes before starting this section.`, el.trainConditions);
  }
  if (split !== "train" && split !== "test" && !state.validationConditions) {
    return fail(el, "Enter VALIDATION session condition notes before starting this section.", el.validationConditions);
  }
  if (!el.numericConsent.checked || !el.accessConsent.checked) {
    return fail(el, "Tick both consent boxes before collecting.", el.numericConsent.checked ? el.accessConsent : el.numericConsent);
  }
  if (!state.cameraReady) return fail(el, state.testTicket ? "Open the camera first." : "Start the camera first.", el.quickStart ?? el.startCamera);
  if (state.testTicket && !state.trainConditions) {
    state.trainConditions = "Not provided by participant.";
    el.trainConditions.value = state.trainConditions;
  }
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
  state.records.push(...stampRecords(records, state.participantId, state.testTicket));
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
  el.detail.textContent = state.testTicket
    ? `${message} To resume, click Open camera, check your preview, then start or resume the remaining trials.`
    : `${message} To resume, click Start Camera, wait for the detector, then Start Selected Session.`;
  stopCamera(state);
  state.cameraReady = false;
  state.importing = false;
  el.pause.disabled = true;
  el.startCollection.disabled = true;
  renderQuickStart(el, state);
}

function renderProgress(el, state) {
  const complete = completedTrialIds(state.records).size;
  const total = makeTrialPlan(state.testTicket).length;
  el.progress.value = complete / total;
  el.progressText.textContent = `${complete} / ${total} trials complete`;
  lockSettings(el, state);
  renderQuickStart(el, state);
}

function lockSettings(el, state) {
  el.participantId.disabled = Boolean(state.testTicket) || Object.keys(state.sessionStartedAt).length > 0 || state.records.length > 0;
  el.trainConditions.disabled = Boolean(state.sessionStartedAt.train || state.sessionStartedAt.test);
  el.validationConditions.disabled = Boolean(state.sessionStartedAt.validation || state.sessionStartedAt.validation_negative);
}

function autosave(el, state) {
  try {
    localStorage.setItem(draftStorageKey(state.testTicket), JSON.stringify({
      testTicket: state.testTicket ?? null,
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

export function restoreDraft(el, state) {
  try {
    const raw = localStorage.getItem(draftStorageKey(state.testTicket));
    if (!raw) return;
    const draft = JSON.parse(raw);
    if (state.testTicket) {
      if (!ticketsMatch(draft.testTicket, state.testTicket) || draft.participantId !== state.testTicket.target_participant ||
          Object.keys(draft.sessionStartedAt ?? {}).some((split) => split !== "test")) {
        throw new Error("Draft does not match this frozen TEST kit.");
      }
      if (draft.records?.length) validateCollection(makeCollection({
        ...draft, recordedAt: draft.consentRecordedAt,
      }), state.testTicket);
    } else if (draft.testTicket) throw new Error("TEST draft cannot be opened in a development kit.");
    el.participantId.value = draft.participantId || "";
    el.trainConditions.value = draft.trainConditions || "";
    el.validationConditions.value = draft.validationConditions || "";
    state.participantId = el.participantId.value;
    state.trainConditions = el.trainConditions.value;
    state.validationConditions = el.validationConditions.value;
    state.sessionStartedAt = draft.sessionStartedAt || {};
    state.consentRecordedAt = draft.consentRecordedAt || "";
    state.records = Array.isArray(draft.records) ? draft.records : [];
    state.frameId = maxFrameId(state.records);
    const split = selectResumeSplit(el, state);
    renderProgress(el, state);
    el.detail.textContent = resumeMessage(state, split, recoveryPrefix(state, split));
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
    testTicket: state.testTicket,
  });
  if (state.testTicket && state.records.length) validateCollection(collection, state.testTicket);
  const zip = makeStoredZip({ "collection.json": JSON.stringify(collection, null, 2) });
  const blob = new Blob([zip], { type: "application/zip" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = collectionFileName(state.participantId, state.records, state.testTicket);
  link.click();
}

export async function importZip(el, state) {
  const file = el.importZip.files?.[0];
  if (!file) return;
  if (state.collecting || state.cameraStarting) return fail(el, "Pause and wait for the current trial to finish before importing.");
  if (state.stream) pause(el, state, "Paused before importing a backup ZIP.");
  const generation = state.generation + 1;
  state.generation = generation;
  state.importing = generation;
  renderQuickStart(el, state);
  try {
    if (file.size > 10 * 1024 * 1024) throw new Error("Return ZIP is larger than 10 MB.");
    const buffer = await file.arrayBuffer();
    if (state.generation !== generation) return;
    const collection = readOwnCollectionZip(buffer, state.testTicket);
    el.participantId.value = collection.participant_id;
    el.numericConsent.checked = collection.consent.numeric_data;
    el.accessConsent.checked = collection.consent.team_and_marker_access;
    el.trainConditions.value = collection.sessions.find((row) => row.split === (state.testTicket ? "test" : "train"))?.conditions ?? "";
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
    const split = selectResumeSplit(el, state);
    renderProgress(el, state);
    el.startCollection.disabled = !state.cameraReady;
    el.detail.textContent = resumeMessage(state, split, recoveryPrefix(state, split));
  } catch (error) {
    if (state.generation !== generation) return;
    el.detail.textContent = `Could not import ZIP: ${error.message}`;
  } finally {
    if (state.generation === generation) el.importZip.value = "";
    if (state.importing === generation) state.importing = false;
    renderQuickStart(el, state);
  }
}

export function clearDraft(el, state) {
  if (state.collecting || state.cameraStarting) return fail(el, "Pause and wait for the current trial to finish before clearing.");
  if (state.records.length > 0 && !confirm("Only clear this after exporting a backup ZIP. Delete this local draft from this browser?")) return;
  if (state.stream) pause(el, state, "Paused before clearing the local draft.");
  try {
    localStorage.removeItem(draftStorageKey(state.testTicket));
  } catch {
    return fail(el, "Browser storage is unavailable. Keep your return ZIP, then close this page to discard the in-memory recording.");
  }
  state.generation += 1;
  state.importing = false;
  state.records = [];
  state.sessionStartedAt = {};
  state.consentRecordedAt = "";
  state.frameId = 0;
  el.numericConsent.checked = false;
  el.accessConsent.checked = false;
  el.participantId.value = state.testTicket?.target_participant ?? "";
  state.participantId = el.participantId.value;
  el.trainConditions.value = "";
  el.validationConditions.value = "";
  el.importZip.value = "";
  renderProgress(el, state);
  el.detail.textContent = "Local draft cleared from this browser.";
}

export function validateFormForExport(el, state) {
  if (state.collecting || state.cameraStarting) return fail(el, "Pause and wait for the current trial to finish before exporting.");
  state.participantId = el.participantId.value.trim();
  state.trainConditions = el.trainConditions.value.trim() || (state.testTicket ? "Not provided by participant." : "");
  state.validationConditions = el.validationConditions.value.trim();
  if (!validateParticipantId(state.participantId)) return fail(el, "Enter a valid pseudonym before exporting.");
  if (state.testTicket && state.participantId !== state.testTicket.target_participant) return fail(el, "Participant does not match this frozen TEST kit.");
  if (!el.numericConsent.checked || !el.accessConsent.checked) return fail(el, "Tick both consent boxes before exporting.");
  if (state.records.length > 0 && makeCollection({
    participantId: state.participantId,
    trainConditions: state.trainConditions,
    validationConditions: state.validationConditions,
    recordedAt: new Date().toISOString(),
    sessionStartedAt: state.sessionStartedAt,
    records: state.records,
    testTicket: state.testTicket,
  }).sessions.length === 0) return fail(el, "Start at least one session before exporting collected records.");
  return true;
}

function showFatal(error) {
  const target = document.getElementById("detail") || document.body;
  target.textContent = `Collector failed to start: ${error.message}`;
}
