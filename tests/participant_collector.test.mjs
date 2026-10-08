import test from "node:test";
import assert from "node:assert/strict";
import {
  LABELS,
  clearDraft,
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
