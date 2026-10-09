import test from "node:test";
import assert from "node:assert/strict";
import {
  LABELS,
  clearDraft,
  importZip,
  validateFormForExport,
  SAMPLE_OFFSETS,
  SampleScheduler,
  cameraLoopActive,
  collectionFileName,
  completedTrialIds,
  crc32,
  makeCollection,
  makeStoredZip,
  makeTrialPlan,
  readOwnCollectionZip,
  stampRecords,
  startCamera,
  validateParticipantId,
} from "../participant/collector.mjs";

const trial = { split: "train", label: "NEXT", trial_id: "train-NEXT-01" };
const landmarks = Array.from({ length: 21 }, (_, i) => [i, i + 0.1, i + 0.2]);

test("export requires consent and clearing a draft removes the old person's agreement", () => {
  const el = Object.fromEntries([
    "participantId", "trainConditions", "validationConditions", "numericConsent", "accessConsent",
    "detail", "progress", "progressText",
  ].map(key => [key, { value: "notes", checked: true, disabled: false, textContent: "" }]));
  el.participantId.value = "P04";
  const state = { records: [], sessionStartedAt: {}, frameId: 5, stream: null };
  el.numericConsent.checked = false;
  assert.equal(validateFormForExport(el, state), false);
  el.numericConsent.checked = true;
  el.accessConsent.checked = false;
  assert.equal(validateFormForExport(el, state), false);
  el.accessConsent.checked = true;
  assert.equal(validateFormForExport(el, state), true);
  const removed = [];
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { removeItem: key => removed.push(key) };
  try {
    clearDraft(el, state);
    assert.equal(removed.length, 1);
    assert.equal(el.participantId.value, "");
    assert.equal(el.numericConsent.checked, false);
    assert.equal(el.accessConsent.checked, false);
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }
});

test("trial plan has train, validation and required unknown trials", () => {
  const plan = makeTrialPlan();
  assert.equal(plan.length, 104);
  assert.equal(plan.filter((row) => row.split === "train").length, 48);
  assert.equal(plan.filter((row) => row.split === "validation").length, 48);
  assert.equal(plan.filter((row) => row.split === "validation_negative").length, 8);
  for (const label of LABELS) {
    assert.equal(plan.filter((row) => row.split === "train" && row.label === label).length, 12);
    assert.equal(plan.filter((row) => row.split === "validation" && row.label === label).length, 12);
  }
});

test("scheduler fills missed slots and refuses stale observations", () => {
  const scheduler = new SampleScheduler(trial, 10);
  scheduler.due(10.25, {
    timestamp: 9.9,
    frame_id: 1,
    hand_count: 1,
    hand: "Right",
    landmarks,
    validity_reason: "ok",
  });
  assert.equal(scheduler.records[0].validity_reason, "stale_observation");
  scheduler.finalize("paused_before_sample");
  assert.equal(scheduler.records.length, SAMPLE_OFFSETS.length);
  assert.equal(scheduler.records.at(-1).validity_reason, "paused_before_sample");
});

test("scheduler does not backfill old scheduled slots with a late frame", () => {
  const scheduler = new SampleScheduler(trial, 0);
  const observation = {
    timestamp: 1.01,
    frame_id: 7,
    hand_count: 1,
    hand: "Right",
    landmarks,
    validity_reason: "ok",
  };
  scheduler.due(1.01, observation);
  assert.equal(scheduler.records.length, 3);
  assert.equal(scheduler.records[0].validity_reason, "stale_observation");
  assert.equal(scheduler.records[1].validity_reason, "stale_observation");
  assert.equal(scheduler.records[2].validity_reason, "");
  assert.equal(scheduler.records[2].frame_id, 7);
});

test("collection contract keeps records in one JSON payload", () => {
  assert.equal(validateParticipantId("P04"), true);
  assert.equal(validateParticipantId("-bad"), false);
  const records = stampRecords(new SampleScheduler(trial, 0).finalize("missed_slot"), "P04");
  const collection = makeCollection({
    participantId: "P04",
    trainConditions: "desk lighting",
    validationConditions: "same room",
    recordedAt: "2026-10-08T00:00:00.000Z",
    sessionStartedAt: { train: "2026-10-08T00:00:00.000Z" },
    records,
  });
  assert.equal(collection.protocol, "gestureforge-browser-development-v1");
  assert.equal(collection.hand, "Right");
  assert.equal(collection.records.length, 5);
  assert.deepEqual([...completedTrialIds(records)], ["P04-train/train-NEXT-01"]);
  assert.match(collectionFileName("P04", []), /^EMAIL_THIS_P04_PARTIAL_development\.zip$/);
});

test("stored zip has one collection.json entry and valid crc", () => {
  const content = JSON.stringify({ ok: true });
  const zip = makeStoredZip({ "collection.json": content });
  const decoder = new TextDecoder();
  assert.equal(decoder.decode(zip.slice(0, 4)), "PK\u0003\u0004");
  assert.equal(decoder.decode(zip.slice(-22, -18)), "PK\u0005\u0006");
  assert.equal(zip[8], 0);
  assert.equal(zip[9], 0);
  assert.equal(zip[10], 0);
  assert.equal(zip[11], 0);
  assert.equal(crc32(new TextEncoder().encode(content)), 0xa7d45f90);
  assert.ok(decoder.decode(zip).includes("collection.json"));
});

test("own zip reader restores collection and rejects extra files", () => {
  const collection = makeCollection({
    participantId: "P04",
    trainConditions: "desk lighting",
    validationConditions: "same room",
    recordedAt: "2026-10-08T00:00:00.000Z",
    sessionStartedAt: { train: "2026-10-08T00:00:00.000Z" },
    records: stampRecords(new SampleScheduler(trial, 0).finalize("missed_slot"), "P04"),
  });
  const zip = makeStoredZip({ "collection.json": JSON.stringify(collection) });
  assert.equal(readOwnCollectionZip(zip).participant_id, "P04");

  const extra = makeStoredZip({ "collection.json": JSON.stringify(collection), "notes.txt": "no" });
  assert.throws(() => readOwnCollectionZip(extra), /exactly one file/);
});

test("importing UNKNOWN before VALIDATION restores notes from validation_negative", async () => {
  const trainRecords = stampRecords(new SampleScheduler(trial, 0).finalize("missed_slot"), "P04");
  const unknownTrial = { split: "validation_negative", label: "UNKNOWN", trial_id: "validation_negative-UNKNOWN-01" };
  const unknownRecords = stampRecords(new SampleScheduler(unknownTrial, 3).finalize("missed_slot"), "P04");
  const collection = makeCollection({
    participantId: "P04",
    trainConditions: "desk lighting",
    validationConditions: "same room unknown prompts",
    recordedAt: "2026-10-08T00:00:00.000Z",
    sessionStartedAt: {
      train: "2026-10-08T00:00:00.000Z",
      validation_negative: "2026-10-08T00:08:00.000Z",
    },
    records: [...trainRecords, ...unknownRecords],
  });
  const zip = makeStoredZip({ "collection.json": JSON.stringify(collection) });
  const el = fakeImportElements(zip);
  const state = {
    collecting: false,
    cameraStarting: false,
    generation: 2,
    records: [],
    sessionStartedAt: {},
    stream: null,
    frameId: 0,
  };
  const stored = [];
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { setItem: (key, value) => stored.push([key, JSON.parse(value)]) };
  try {
    await importZip(el, state);
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }

  assert.equal(el.validationConditions.value, "same room unknown prompts");
  assert.equal(state.validationConditions, "same room unknown prompts");
  assert.equal(el.validationConditions.disabled, true);
  assert.deepEqual(state.sessionStartedAt, {
    train: "2026-10-08T00:00:00.000Z",
    validation_negative: "2026-10-08T00:08:00.000Z",
  });
  assert.deepEqual(state.records, collection.records);
  assert.equal(stored.at(-1)[1].validationConditions, "same room unknown prompts");
  assert.equal(validateFormForExport(el, state), true);
  const exportedAgain = makeCollection({
    participantId: state.participantId,
    trainConditions: state.trainConditions,
    validationConditions: state.validationConditions,
    recordedAt: state.consentRecordedAt,
    sessionStartedAt: state.sessionStartedAt,
    records: state.records,
  });
  assert.equal(readOwnCollectionZip(makeStoredZip({ "collection.json": JSON.stringify(exportedAgain) })).sessions.length, 2);
});

test("validation session notes take precedence over validation_negative on import", async () => {
  const collection = makeCollection({
    participantId: "P04",
    trainConditions: "desk lighting",
    validationConditions: "current validation notes",
    recordedAt: "2026-10-08T00:00:00.000Z",
    sessionStartedAt: {
      train: "2026-10-08T00:00:00.000Z",
      validation: "2026-10-08T00:05:00.000Z",
      validation_negative: "2026-10-08T00:10:00.000Z",
    },
    records: [],
  });
  collection.sessions.find((row) => row.split === "validation_negative").conditions = "older unknown notes";
  const el = fakeImportElements(makeStoredZip({ "collection.json": JSON.stringify(collection) }));
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { setItem() {} };
  try {
    await importZip(el, {
      collecting: false,
      cameraStarting: false,
      generation: 1,
      records: [],
      sessionStartedAt: {},
      stream: null,
      frameId: 0,
    });
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }

  assert.equal(el.validationConditions.value, "current validation notes");
});

test("camera loop guard rejects stale callbacks after pause or restart", () => {
  const state = { stream: {}, paused: false, generation: 4 };
  assert.equal(cameraLoopActive(state, 4), true);
  assert.equal(cameraLoopActive(state, 3), false);
  state.paused = true;
  assert.equal(cameraLoopActive(state, 4), false);
  state.paused = false;
  state.stream = null;
  assert.equal(cameraLoopActive(state, 4), false);
});

test("camera startup cancellation cannot enable collection", async (t) => {
  for (const phase of ["video.play", "model load"]) {
    await t.test(`paused during ${phase}`, async () => {
      await runCancelledStartup(phase);
    });
  }
});

function deferred() {
  let resolve;
  const promise = new Promise((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

async function runCancelledStartup(phase) {
  const navigatorDescriptor = Object.getOwnPropertyDescriptor(globalThis, "navigator");
  const animationFrameDescriptor = Object.getOwnPropertyDescriptor(globalThis, "requestAnimationFrame");
  const mediaCalls = [];
  const frameCallbacks = [];
  const playGate = phase === "video.play" ? deferred() : null;
  const modelGate = deferred();
  const modelEntered = deferred();
  const streams = [fakeStream("first"), fakeStream("second")];
  const el = fakeCameraElements({ play: playGate ? () => playGate.promise : async () => {} });
  const state = {
    generation: 0,
    cameraStarting: false,
    collecting: false,
    cameraReady: true,
    paused: true,
    latest: { frame_id: 99 },
    stream: null,
    handLandmarker: null,
    createLandmarker: () => {
      modelEntered.resolve();
      return modelGate.promise;
    },
  };

  Object.defineProperty(globalThis, "navigator", {
    configurable: true,
    value: { mediaDevices: { getUserMedia: async () => mediaCalls.push(streams.shift()) && mediaCalls.at(-1) } },
  });
  Object.defineProperty(globalThis, "requestAnimationFrame", {
    configurable: true,
    value: (callback) => frameCallbacks.push(callback),
  });

  try {
    const starting = startCamera(el, state);
    if (playGate) {
      await until(() => mediaCalls[0]?.tracks[0].onended);
      mediaCalls[0].tracks[0].onended();
      playGate.resolve();
    } else {
      await modelEntered.promise;
      assert.equal(mediaCalls.length, 1);
      mediaCalls[0].tracks[0].onended();
    }
    modelGate.resolve({ detectForVideo: () => ({}) });
    await starting;

    assert.equal(state.cameraReady, false);
    assert.equal(state.paused, true);
    assert.equal(state.stream, null);
    assert.equal(state.latest, null);
    assert.equal(el.startCollection.disabled, true);
    assert.equal(el.pause.disabled, true);
    assert.equal(frameCallbacks.length, 0);

    await startCamera(el, state);
    modelGate.resolve({ detectForVideo: () => ({}) });
    assert.equal(state.cameraReady, true);
    assert.equal(state.paused, false);
    assert.equal(state.stream.name, "second");
    assert.equal(el.startCollection.disabled, false);
    assert.equal(el.pause.disabled, false);
    assert.equal(frameCallbacks.length, 1);

    state.collecting = true;
    await startCamera(el, state);
    assert.equal(mediaCalls.length, 2);
  } finally {
    restoreGlobalProperty("navigator", navigatorDescriptor);
    restoreGlobalProperty("requestAnimationFrame", animationFrameDescriptor);
  }
}

function restoreGlobalProperty(name, descriptor) {
  if (descriptor) Object.defineProperty(globalThis, name, descriptor);
  else delete globalThis[name];
}

async function until(ready) {
  while (!ready()) await Promise.resolve();
}

function fakeCameraElements({ play = async () => {} } = {}) {
  return {
    cameraSelect: { value: "" },
    startCamera: { disabled: false },
    startCollection: { disabled: false },
    pause: { disabled: true },
    cameraStatus: { textContent: "" },
    instruction: { textContent: "" },
    detail: { textContent: "" },
    preview: { width: 0, height: 0 },
    video: {
      videoWidth: 640,
      videoHeight: 480,
      play,
    },
  };
}

function fakeStream(name) {
  const tracks = [{ onended: null, stop() {} }];
  return {
    name,
    tracks,
    getTracks: () => tracks,
    getVideoTracks: () => tracks,
  };
}

function fakeImportElements(zip) {
  return {
    importZip: { files: [{ size: zip.byteLength, arrayBuffer: async () => zip.buffer.slice(zip.byteOffset, zip.byteOffset + zip.byteLength) }], value: "return.zip" },
    participantId: { value: "", disabled: false },
    trainConditions: { value: "", disabled: false },
    validationConditions: { value: "", disabled: false },
    numericConsent: { checked: false },
    accessConsent: { checked: false },
    progress: { value: 0 },
    progressText: { textContent: "" },
    detail: { textContent: "" },
  };
}
