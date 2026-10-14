import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  LABELS,
  clearDraft,
  exportZip,
  importZip,
  restoreDraft,
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
  startCollection,
  validateParticipantId,
  validateCollection,
  draftStorageKey,
} from "../participant/collector.mjs";

const trial = { split: "train", label: "NEXT", trial_id: "train-NEXT-01" };
const landmarks = Array.from({ length: 21 }, (_, i) => [i, i + 0.1, i + 0.2]);
const testTicket = {
  schema_version: 1, protocol: "gestureforge-browser-test-v1", paired_protocol: "gf-p18-positive-test-v1",
  target_participant: "P04", config_fingerprint: "a".repeat(64), frozen_integrity_sha256: "b".repeat(64),
  pose_set_id: "standard-v1", hand: "Right",
};

test("frozen TEST uses 48 positive trials and isolates every freeze from development", () => {
  const plan = makeTrialPlan(testTicket);
  assert.equal(plan.length, 48);
  assert.deepEqual([...new Set(plan.map(row => row.split))], ["test"]);
  for (const label of LABELS) assert.equal(plan.filter(row => row.label === label).length, 12);
  assert.notEqual(draftStorageKey(), draftStorageKey(testTicket));
  assert.notEqual(draftStorageKey(testTicket), draftStorageKey({ ...testTicket, config_fingerprint: "c".repeat(64) }));
  assert.notEqual(draftStorageKey(testTicket), draftStorageKey({ ...testTicket, target_participant: "P05" }));
  assert.throws(() => makeTrialPlan({ ...testTicket, hand: "Left" }), /ticket/);
});

test("TEST recovery retains invalid trials, finishes the plan, exports and restores only the same ticket", async () => {
  const initial = stampRecords(new SampleScheduler(makeTrialPlan(testTicket)[0], 0).finalize("paused_before_sample"), "P04", testTicket);
  const collection = makeCollection({
    participantId: "P04", trainConditions: "bright room", validationConditions: "", testTicket,
    recordedAt: "2026-10-14T00:00:00Z", sessionStartedAt: { test: "2026-10-14T00:00:01Z" }, records: initial,
  });
  const zip = makeStoredZip({ "collection.json": JSON.stringify(collection) });
  const el = { ...fakeCollectionElements({ split: "test", validationConditions: "" }), ...fakeImportElements(zip) };
  const state = { ...fakeCollectionState(), testTicket };
  const storageDescriptor = Object.getOwnPropertyDescriptor(globalThis, "localStorage");
  const saved = new Map();
  globalThis.localStorage = { getItem: key => saved.get(key), setItem: (key, value) => saved.set(key, value) };
  const restoreClock = installCollectionClock(10000);
  const restoreBrowser = installExportBrowser();
  try {
    await importZip(el, state);
    assert.equal(el.sessionSelect.value, "test");
    assert.equal(el.participantId.disabled, true);
    assert.equal(el.trainConditions.disabled, true);
    restoreClock.bind(state);
    await startCollection(el, state);
    assert.equal(state.records.length, 240);
    assert.deepEqual(state.records.slice(0, 5), initial);
    assert.match(el.progressText.textContent, /48 \/ 48/);
    assert.match(el.detail.textContent, /All 48 trials/);
    assert.equal(saved.has(draftStorageKey()), false);
    exportZip(el, state);
    const exported = await restoreBrowser.exportedZip();
    assert.equal(exported.name, "EMAIL_THIS_P04_test.zip");
    assert.equal(readOwnCollectionZip(exported.bytes, testTicket).records.length, 240);
    assert.throws(() => readOwnCollectionZip(exported.bytes), /protocol/);
    assert.throws(() => readOwnCollectionZip(exported.bytes, { ...testTicket, config_fingerprint: "c".repeat(64) }), /ticket/);
    const restored = { ...fakeCollectionState(), testTicket };
    restoreDraft(el, restored);
    assert.deepEqual(restored.records, state.records);
    const wrong = { ...fakeCollectionState(), testTicket: { ...testTicket, config_fingerprint: "c".repeat(64) } };
    saved.set(draftStorageKey(wrong.testTicket), saved.get(draftStorageKey(testTicket)));
    restoreDraft(el, wrong);
    assert.deepEqual(wrong.records, []);
    assert.match(el.detail.textContent, /could not be restored/);
    saved.set(draftStorageKey(), saved.get(draftStorageKey(testTicket)));
    const development = fakeCollectionState();
    restoreDraft(el, development);
    assert.deepEqual(development.records, []);
  } finally {
    restoreClock(); restoreBrowser(); restoreGlobalProperty("localStorage", storageDescriptor);
  }
});

test("TEST collection rejects relabelled development, wrong participant, mixed splits and omitted slots", () => {
  const records = stampRecords(new SampleScheduler(makeTrialPlan(testTicket)[0], 0).finalize(), "P04", testTicket);
  const collection = makeCollection({
    participantId: "P04", trainConditions: "notes", testTicket, recordedAt: "2026-10-14T00:00:00Z",
    sessionStartedAt: { test: "2026-10-14T00:00:01Z" }, records,
  });
  assert.equal(validateCollection(collection, testTicket), collection);
  for (const mutate of [
    value => { value.participant_id = "P05"; },
    value => { value.records[0].split = "train"; },
    value => { value.records[0].trial_id = "train-NEUTRAL-01"; },
    value => { value.records.pop(); },
  ]) {
    const changed = structuredClone(collection); mutate(changed);
    assert.throws(() => validateCollection(changed, testTicket));
  }
});

test("export requires consent and clearing a draft removes the old person's agreement", () => {
  const el = Object.fromEntries([
    "participantId", "trainConditions", "validationConditions", "numericConsent", "accessConsent",
    "detail", "progress", "progressText",
  ].map(key => [key, { value: "notes", checked: true, disabled: false, textContent: "" }]));
  el.participantId.value = "P04";
  el.importZip = { value: "return.zip" };
  const state = { records: [], sessionStartedAt: {}, frameId: 5, stream: null, generation: 0 };
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

test("TRAIN-only return ZIP resumes at VALIDATION without mutating saved samples", async () => {
  const trainRecords = completedRecordsForSplit("train", "P69");
  const collection = makeCollection({
    participantId: "P69",
    trainConditions: "desk, bright light",
    validationConditions: "",
    recordedAt: "2026-10-13T10:00:00.000Z",
    sessionStartedAt: { train: "2026-10-13T10:25:21.583Z" },
    records: trainRecords,
  });
  const el = fakeImportElements(makeStoredZip({ "collection.json": JSON.stringify(collection) }));
  const state = {
    collecting: false,
    cameraStarting: false,
    generation: 1,
    records: [],
    sessionStartedAt: {},
    stream: null,
    frameId: 0,
    cameraReady: false,
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

  assert.equal(el.sessionSelect.value, "validation");
  assert.equal(el.validationConditions.disabled, false);
  assert.equal(el.detail.textContent, "Recovered TRAIN. 48 VALIDATION trials remaining (56 total). After a break, enter actual VALIDATION notes, then Start Camera and Start Selected Session.");
  assert.equal(el.startCollection.disabled, true);
  assert.deepEqual(state.records, trainRecords);
  assert.equal(stored.at(-1)[1].records.length, 240);
});

test("TRAIN-only return ZIP can finish remaining sections without re-recording TRAIN", async () => {
  const restoreClock = installCollectionClock(200_000);
  const restoreBrowser = installExportBrowser();
  const trainRecords = completedRecordsForSplit("train", "P69");
  const collection = makeCollection({
    participantId: "P69",
    trainConditions: "desk, bright light",
    validationConditions: "",
    recordedAt: "2026-10-13T10:00:00.000Z",
    sessionStartedAt: { train: "2026-10-13T10:25:21.583Z" },
    records: trainRecords,
  });
  const el = fakeImportElements(makeStoredZip({ "collection.json": JSON.stringify(collection) }));
  const state = {
    collecting: false,
    cameraStarting: false,
    generation: 1,
    records: [],
    sessionStartedAt: {},
    stream: null,
    frameId: 0,
    cameraReady: true,
    paused: false,
  };
  state.latest = freshObservation(0, 0);
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { setItem() {} };
  try {
    restoreClock.bind(state);
    await importZip(el, state);
    el.validationConditions.value = "same room, after break";
    await startCollection(el, state);
    assert.equal(el.sessionSelect.value, "validation_negative");
    await startCollection(el, state);

    exportZip(el, state);
    const exported = await restoreBrowser.exportedZip();
    const exportedCollection = readOwnCollectionZip(new Uint8Array(exported.bytes));
    assert.equal(exported.name, "EMAIL_THIS_P69_development.zip");
    assert.equal(exportedCollection.records.length, 520);
    assert.equal(completedTrialIds(exportedCollection.records).size, 104);
    assert.deepEqual(exportedCollection.records.slice(0, 240), trainRecords);
  } finally {
    restoreClock();
    restoreBrowser();
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }
});

test("partial VALIDATION recovery continues the locked validation session", async () => {
  const trainRecords = completedRecordsForSplit("train", "P69");
  const validationTrial = makeTrialPlan().find((row) => row.split === "validation");
  const validationRecords = stampRecords(new SampleScheduler(validationTrial, 200).finalize("missed_slot"), "P69");
  const collection = makeCollection({
    participantId: "P69",
    trainConditions: "desk, bright light",
    validationConditions: "same room, after break",
    recordedAt: "2026-10-13T10:00:00.000Z",
    sessionStartedAt: {
      train: "2026-10-13T10:25:21.583Z",
      validation: "2026-10-13T10:40:21.583Z",
    },
    records: [...trainRecords, ...validationRecords],
  });
  const el = fakeImportElements(makeStoredZip({ "collection.json": JSON.stringify(collection) }));
  const state = {
    collecting: false,
    cameraStarting: false,
    generation: 1,
    records: [],
    sessionStartedAt: {},
    stream: null,
    frameId: 0,
    cameraReady: false,
  };
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { setItem() {} };
  try {
    await importZip(el, state);
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }

  assert.equal(el.sessionSelect.value, "validation");
  assert.equal(el.validationConditions.disabled, true);
  assert.equal(el.detail.textContent, "Recovered VALIDATION. 47 VALIDATION trials remaining (55 total). Start Camera and Start Selected Session to continue VALIDATION.");
});

test("local TRAIN-only draft resumes at VALIDATION without locking validation notes", () => {
  const trainRecords = completedRecordsForSplit("train", "P69");
  const el = fakeImportElements(new Uint8Array());
  const state = { records: [], sessionStartedAt: {}, consentRecordedAt: "", frameId: 0, cameraReady: false };
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = {
    getItem: () => JSON.stringify({
      participantId: "P69",
      trainConditions: "desk, bright light",
      validationConditions: "",
      sessionStartedAt: { train: "2026-10-13T10:25:21.583Z" },
      consentRecordedAt: "2026-10-13T10:00:00.000Z",
      records: trainRecords,
    }),
  };
  try {
    restoreDraft(el, state);
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }

  assert.equal(el.sessionSelect.value, "validation");
  assert.equal(el.validationConditions.disabled, false);
  assert.equal(el.detail.textContent, "Recovered TRAIN. 48 VALIDATION trials remaining (56 total). After a break, enter actual VALIDATION notes, then Start Camera and Start Selected Session.");
  assert.deepEqual(state.records, trainRecords);
});

test("UNKNOWN before VALIDATION keeps saved condition notes without requesting edits", async () => {
  const unknown = makeTrialPlan().find(row => row.split === "validation_negative");
  const collection = makeCollection({
    participantId: "P04", trainConditions: "desk", validationConditions: "after break",
    recordedAt: "2026-10-13T10:00:00.000Z",
    sessionStartedAt: { train: "2026-10-13T10:00:00.000Z", validation_negative: "2026-10-13T10:15:00.000Z" },
    records: [...completedRecordsForSplit("train", "P04"), ...stampRecords(new SampleScheduler(unknown, 200).finalize("missed_slot"), "P04")],
  });
  const el = fakeImportElements(makeStoredZip({ "collection.json": JSON.stringify(collection) }));
  const state = fakeCollectionState();
  await importZip(el, state);
  assert.equal(el.sessionSelect.value, "validation");
  assert.equal(el.validationConditions.disabled, true);
  assert.equal(el.validationConditions.value, "after break");
  assert.doesNotMatch(el.detail.textContent, /enter actual VALIDATION notes/i);
  assert.match(el.detail.textContent, /continue VALIDATION/);
});

test("starting an already completed section keeps records unchanged and points to remaining work", async () => {
  const trainRecords = completedRecordsForSplit("train", "P69");
  const el = fakeCollectionElements({ split: "train", participantId: "P69", trainConditions: "desk", validationConditions: "" });
  const state = fakeCollectionState({ records: trainRecords });
  state.sessionStartedAt = { train: "2026-10-13T10:25:21.583Z" };

  await startCollection(el, state);

  assert.equal(el.sessionSelect.value, "validation");
  assert.equal(el.detail.textContent, "TRAIN is already complete. 48 VALIDATION trials remaining (56 total). After a break, enter actual VALIDATION notes, then Start Selected Session.");
  assert.deepEqual(state.records, trainRecords);
  assert.deepEqual(state.sessionStartedAt, { train: "2026-10-13T10:25:21.583Z" });
});

test("clearing a draft cancels a pending return ZIP import", async () => {
  const zip = collectionZip("P04", "old train", "old validation");
  const gate = deferred();
  const el = fakeImportElements(zip, () => gate.promise);
  el.participantId.value = "P03";
  el.numericConsent.checked = true;
  el.accessConsent.checked = true;
  const state = {
    collecting: false,
    cameraStarting: false,
    generation: 5,
    records: stampRecords(new SampleScheduler(trial, 0).finalize("missed_slot"), "P03"),
    sessionStartedAt: { train: "2026-10-08T00:00:00.000Z" },
    stream: null,
    frameId: 5,
  };
  const storageCalls = [];
  const previousStorage = globalThis.localStorage;
  const previousConfirm = globalThis.confirm;
  globalThis.localStorage = {
    removeItem: key => storageCalls.push(["remove", key]),
    setItem: (key, value) => storageCalls.push(["set", key, JSON.parse(value)]),
  };
  globalThis.confirm = () => true;
  try {
    const importing = importZip(el, state);
    clearDraft(el, state);
    gate.resolve(zip.buffer.slice(zip.byteOffset, zip.byteOffset + zip.byteLength));
    await importing;
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
    if (previousConfirm === undefined) delete globalThis.confirm;
    else globalThis.confirm = previousConfirm;
  }

  assert.deepEqual(storageCalls.map(([action]) => action), ["remove"]);
  assert.equal(state.generation, 7);
  assert.deepEqual(state.records, []);
  assert.equal(el.participantId.value, "");
  assert.equal(el.numericConsent.checked, false);
  assert.equal(el.accessConsent.checked, false);
  assert.equal(el.detail.textContent, "Local draft cleared from this browser.");
  assert.equal(el.importZip.value, "");
});

test("newer return ZIP import wins over an older pending import", async () => {
  const oldZip = collectionZip("P04", "old train", "old validation");
  const newZip = collectionZip("P05", "new train", "new validation");
  const gate = deferred();
  const el = fakeImportElements(oldZip, () => gate.promise);
  const state = {
    collecting: false,
    cameraStarting: false,
    generation: 0,
    records: [],
    sessionStartedAt: {},
    stream: null,
    frameId: 0,
  };
  const stored = [];
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { setItem: (key, value) => stored.push([key, JSON.parse(value)]) };
  try {
    const olderImport = importZip(el, state);
    el.importZip.files = fakeImportElements(newZip).importZip.files;
    await importZip(el, state);
    el.importZip.value = "next-selection.zip";
    gate.resolve(oldZip.buffer.slice(oldZip.byteOffset, oldZip.byteOffset + oldZip.byteLength));
    await olderImport;
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }

  assert.equal(state.participantId, "P05");
  assert.equal(state.trainConditions, "new train");
  assert.equal(el.participantId.value, "P05");
  assert.equal(stored.length, 1);
  assert.equal(stored[0][1].participantId, "P05");
  assert.equal(el.detail.textContent, "Recovered draft. 47 TRAIN trials remaining (103 total). Start Camera and Start Selected Session to continue TRAIN.");
  assert.equal(el.importZip.value, "next-selection.zip");
});

test("stale rejected return ZIP import cannot overwrite a newer success", async () => {
  const oldZip = collectionZip("P04", "old train", "old validation");
  const newZip = collectionZip("P05", "new train", "new validation");
  const gate = deferred();
  const el = fakeImportElements(oldZip, () => gate.promise);
  const state = {
    collecting: false,
    cameraStarting: false,
    generation: 0,
    records: [],
    sessionStartedAt: {},
    stream: null,
    frameId: 0,
  };
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { setItem() {} };
  try {
    const olderImport = importZip(el, state);
    el.importZip.files = fakeImportElements(newZip).importZip.files;
    await importZip(el, state);
    el.importZip.value = "next-selection.zip";
    gate.reject(new Error("file read failed"));
    await olderImport;
  } finally {
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }

  assert.equal(state.participantId, "P05");
  assert.equal(el.detail.textContent, "Recovered draft. 47 TRAIN trials remaining (103 total). Start Camera and Start Selected Session to continue TRAIN.");
  assert.equal(el.importZip.value, "next-selection.zip");
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

test("completed TRAIN can advance to VALIDATION before future validation notes are entered", async () => {
  const el = fakeCollectionElements({ split: "train", trainConditions: "bright room", validationConditions: "" });
  const state = fakeCollectionState({ records: completedRecordsForSplit("train", "P04") });

  await startCollection(el, state);

  assert.equal(el.detail.textContent, "TRAIN is already complete. 48 VALIDATION trials remaining (56 total). After a break, enter actual VALIDATION notes, then Start Selected Session.");
  assert.deepEqual(state.sessionStartedAt, {});
  assert.equal(el.sessionSelect.value, "validation");
  assert.equal(el.validationConditions.focused, false);
});

test("fresh collection can run TRAIN first, then export all sessions", async () => {
  const restoreClock = installCollectionClock();
  const restoreBrowser = installExportBrowser();
  const el = fakeCollectionElements({ split: "train", trainConditions: "bright room", validationConditions: "" });
  const state = fakeCollectionState();
  state.latest = freshObservation(0, 0);
  const previousStorage = globalThis.localStorage;
  globalThis.localStorage = { setItem() {} };
  try {
    restoreClock.bind(state);
    await startCollection(el, state);
    assert.equal(state.records.length, 48 * SAMPLE_OFFSETS.length);
    assert.deepEqual(Object.keys(state.sessionStartedAt), ["train"]);
    assert.equal(el.validationConditions.value, "");
    assert.equal(el.sessionSelect.value, "validation");
    assert.equal(el.detail.textContent, "TRAIN complete. 48 VALIDATION trials remaining (56 total). After a break, enter actual VALIDATION notes, then Start Selected Session.");

    el.validationConditions.value = "same room, second section";
    await startCollection(el, state);
    assert.equal(el.sessionSelect.value, "validation_negative");
    assert.equal(el.detail.textContent, "VALIDATION complete. 8 UNKNOWN trials remaining (8 total). Start Selected Session to continue UNKNOWN.");
    await startCollection(el, state);
    assert.equal(state.records.length, makeTrialPlan().length * SAMPLE_OFFSETS.length);

    exportZip(el, state);
    const exported = await restoreBrowser.exportedZip();
    const collection = readOwnCollectionZip(new Uint8Array(exported.bytes));
    assert.equal(exported.name, "EMAIL_THIS_P04_development.zip");
    assert.equal(collection.records.length, 520);
    assert.deepEqual(collection.sessions.map((row) => row.split), ["train", "validation", "validation_negative"]);
    assert.deepEqual(collection.sessions.map((row) => row.conditions), [
      "bright room",
      "same room, second section",
      "same room, second section",
    ]);
    assert.equal(new Set(collection.records.map((row) => row.validity_reason)).size, 1);
    assert.equal(collection.records[0].validity_reason, "");
  } finally {
    restoreClock();
    restoreBrowser();
    if (previousStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = previousStorage;
  }
});

test("VALIDATION and UNKNOWN require validation notes and move focus to that field", async () => {
  for (const split of ["validation", "validation_negative"]) {
    const el = fakeCollectionElements({ split, trainConditions: "bright room", validationConditions: "" });
    const state = fakeCollectionState();

    await startCollection(el, state);

    assert.equal(el.detail.textContent, "Enter VALIDATION session condition notes before starting this section.");
    assert.equal(el.validationConditions.focused, true);
    assert.equal(el.validationConditions.scrolled, true);
    assert.equal(state.collecting, false);
    assert.deepEqual(state.sessionStartedAt, {});
  }
});

test("collection start still requires both consent boxes", async () => {
  const el = fakeCollectionElements({ trainConditions: "bright room", validationConditions: "" });
  el.accessConsent.checked = false;
  const state = fakeCollectionState();

  await startCollection(el, state);

  assert.equal(el.detail.textContent, "Tick both consent boxes before collecting.");
  assert.equal(el.accessConsent.focused, true);
  assert.equal(el.accessConsent.scrolled, true);
});

test("collection status appears before the camera preview so started trials are visible", async () => {
  const html = await readFile(new URL("../participant/collector.html", import.meta.url), "utf8");

  assert.ok(html.indexOf('id="collectionStatus"') < html.indexOf('id="preview"'));
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
  let reject;
  const promise = new Promise((done, fail) => {
    resolve = done;
    reject = fail;
  });
  return { promise, resolve, reject };
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
    assert.match(el.detail.textContent, /Start Camera.*Start Selected Session/);

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

function fakeCollectionElements({
  split = "train",
  participantId = "P04",
  trainConditions = "bright room",
  validationConditions = "same room",
} = {}) {
  const focusable = (value = "") => ({
    value,
    checked: true,
    disabled: false,
    focused: false,
    scrolled: false,
    focus() { this.focused = true; },
    scrollIntoView() { this.scrolled = true; },
  });
  return {
    participantId: focusable(participantId),
    trainConditions: focusable(trainConditions),
    validationConditions: focusable(validationConditions),
    numericConsent: focusable(),
    accessConsent: focusable(),
    sessionSelect: { value: split },
    startCollection: { disabled: false },
    exportZip: { disabled: false },
    importZip: { disabled: false },
    clearDraft: { disabled: false },
    detail: { textContent: "" },
    instruction: { textContent: "" },
    progress: { value: 0 },
    progressText: { textContent: "" },
    collectionStatus: { scrollIntoView() { this.scrolled = true; }, scrolled: false },
  };
}

function fakeCollectionState({ records = [] } = {}) {
  return {
    records,
    sessionStartedAt: {},
    cameraReady: true,
    collecting: false,
    generation: 0,
    paused: true,
  };
}

function completedRecordsForSplit(split, participantId) {
  const plan = makeTrialPlan().filter((row) => row.split === split);
  return plan.flatMap((row, index) => stampRecords(new SampleScheduler(row, index * 3).finalize("missed_slot"), participantId));
}

function installCollectionClock(initialMs = 0) {
  let nowMs = initialMs;
  let state = null;
  let frame = 0;
  const performanceDescriptor = Object.getOwnPropertyDescriptor(globalThis, "performance");
  const timeoutDescriptor = Object.getOwnPropertyDescriptor(globalThis, "setTimeout");
  Object.defineProperty(globalThis, "performance", {
    configurable: true,
    value: { timeOrigin: 0, now: () => nowMs },
  });
  Object.defineProperty(globalThis, "setTimeout", {
    configurable: true,
    value: (callback, ms = 0) => {
      nowMs += ms;
      if (state) state.latest = freshObservation(nowMs / 1000, frame += 1);
      callback();
      return 1;
    },
  });
  const restore = () => {
    restoreGlobalProperty("performance", performanceDescriptor);
    restoreGlobalProperty("setTimeout", timeoutDescriptor);
  };
  restore.bind = (nextState) => { state = nextState; };
  return restore;
}

function freshObservation(timestamp, frameId) {
  return {
    timestamp,
    frame_id: frameId,
    hand_count: 1,
    hand: "Right",
    landmarks,
    validity_reason: "",
  };
}

function installExportBrowser() {
  let link = null;
  const documentDescriptor = Object.getOwnPropertyDescriptor(globalThis, "document");
  const urlDescriptor = Object.getOwnPropertyDescriptor(globalThis, "URL");
  Object.defineProperty(globalThis, "document", {
    configurable: true,
    value: {
      createElement: () => {
        link = { href: "", download: "", clicked: false, click() { this.clicked = true; } };
        return link;
      },
    },
  });
  Object.defineProperty(globalThis, "URL", {
    configurable: true,
    value: { createObjectURL: (blob) => blob },
  });
  const restore = () => {
    restoreGlobalProperty("document", documentDescriptor);
    restoreGlobalProperty("URL", urlDescriptor);
  };
  restore.exportedZip = async () => {
    assert.equal(link?.clicked, true);
    return { name: link.download, bytes: await link.href.arrayBuffer() };
  };
  return restore;
}

function collectionZip(participantId, trainConditions, validationConditions) {
  const collection = makeCollection({
    participantId,
    trainConditions,
    validationConditions,
    recordedAt: "2026-10-08T00:00:00.000Z",
    sessionStartedAt: { train: "2026-10-08T00:00:00.000Z" },
    records: stampRecords(new SampleScheduler(trial, 0).finalize("missed_slot"), participantId),
  });
  return makeStoredZip({ "collection.json": JSON.stringify(collection) });
}

function fakeImportElements(zip, arrayBuffer = async () => zip.buffer.slice(zip.byteOffset, zip.byteOffset + zip.byteLength)) {
  return {
    importZip: { files: [{ size: zip.byteLength, arrayBuffer }], value: "return.zip" },
    participantId: { value: "", disabled: false },
    trainConditions: { value: "", disabled: false },
    validationConditions: { value: "", disabled: false },
    numericConsent: { checked: false },
    accessConsent: { checked: false },
    sessionSelect: { value: "train" },
    startCollection: { disabled: false },
    exportZip: { disabled: false },
    clearDraft: { disabled: false },
    progress: { value: 0 },
    progressText: { textContent: "" },
    instruction: { textContent: "" },
    detail: { textContent: "" },
  };
}
