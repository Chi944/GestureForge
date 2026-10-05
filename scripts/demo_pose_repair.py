"""Generated UI workflow evidence only. No webcam, private input or readiness.

The human-provenance fields deliberately exercise the production validators, as
in the existing profile tests. Every dataset is labelled GENERATED SOFTWARE DEMO
ONLY with a DEMO_ONLY participant. These files are not participant evidence.
"""

import argparse
from dataclasses import replace
import json
from pathlib import Path
import time
from uuid import uuid4

import numpy as np
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from gestureforge.contracts import Observation
from gestureforge.dataset import file_sha256, save_dataset
from gestureforge.enrolment import OFFSETS
from gestureforge.fixtures import synthetic_dataset
from gestureforge.pose_repair_widget import PoseRepairWidget
from gestureforge.profile_widget import ProfileSelectorWidget
from gestureforge.profiles import ProfileSettings, ProfileStore
from gestureforge.vocabulary import GestureVocabulary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.local/pose-repair-demo'))
    args = parser.parse_args()
    folder = args.output.resolve() / ('generated-' + uuid4().hex)
    folder.mkdir(parents=True, exist_ok=False)
    app = QApplication.instance() or QApplication([])
    assert isinstance(app, QApplication)
    font_path = Path('C:/Windows/Fonts/segoeui.ttf')
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))
    app.setStyle('Fusion')
    font = app.font()
    font.setFamily('Segoe UI')
    font.setPointSize(10)
    app.setFont(font)
    generated = synthetic_dataset(trials_per_label_per_split=2)
    vocab = GestureVocabulary(('G1', 'G2', 'G3'))
    names = dict(zip(generated.vocabulary.labels, vocab.labels, strict=True))
    records = tuple(replace(r, participant_id='DEMO_ONLY', hand='Right', provenance='human',
                            intended_label=names.get(r.intended_label, r.intended_label))
                    for r in generated.records)
    source = save_dataset(folder / 'original', records, generated.features,
                          {'chosen_hand': 'Right', 'warning': 'GENERATED SOFTWARE DEMO ONLY'},
                          vocabulary=vocab)
    assert source.manifest_path is not None
    store = ProfileStore(folder / 'profiles')
    original = store.create('GENERATED original', source.manifest_path, 'Right', consent=True,
                            settings=ProfileSettings('knn', 1.5, 1.5))
    source_hash = file_sha256(source.manifest_path)
    now = [0.]
    repair = PoseRepairWidget(folder / 'repair', clock=lambda: now[0])
    selector = ProfileSelectorWidget(store)
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(QLabel('GENERATED SOFTWARE DEMO ONLY — no webcam or participant accuracy'))
    layout.addWidget(repair)
    layout.addWidget(selector)
    window.resize(920, 1550)
    window.show()

    def snap(name):
        app.processEvents()
        window.grab().save(str(folder / (name + '.png')))

    repair.set_source(original.record)
    repair.repair_pose.setCurrentText('NEUTRAL')
    repair.diagnosis.setText('GENERATED diagnostic review; demonstrate one-label replacement only')
    repair.setup.setText('GENERATED SOFTWARE DEMO ONLY')
    repair.trials.setValue(2)
    repair.diagnostic_reviewed.setChecked(True)
    repair.consent.setChecked(True)
    repair.candidate_ready.connect(selector.offer_repair_candidate)
    snap('01-selected-neutral')
    repair.request_collection()
    assert repair.attach_capture(repair.request_id, 'demo-capture', 'DEMO_ONLY')
    session = repair.session
    assert session is not None
    for trial in range(2):
        now[0] = trial * 6.
        repair.tick()
        repair.begin_trial()
        for slot, offset in enumerate(OFFSETS):
            now[0] = trial * 6. + 2. + offset + .01
            points = np.arange(63, dtype=float).reshape(21, 3) / 100
            repair.receive_observation(Observation('demo-capture', 'DEMO_ONLY', trial * 10 + slot,
                                                    now[0], 1, 'Right', points))
        now[0] = trial * 6. + 4.1
        repair.tick()
    assert session.state == 'complete'
    snap('02-count-review')
    repair.count_review.setChecked(True)
    repair.build_candidate()
    assert selector._repair_candidate is not None
    assert selector._future is None and len(store.list_ids()) == 1
    snap('03-explicit-profile-review')
    selector.consent.setChecked(True)
    selector.create_button.click()
    deadline = time.monotonic() + 30
    while selector.busy and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.01)
    assert selector.loaded is not None, selector.status.text()
    assert selector.loaded.record.profile_id != original.record.profile_id
    rollback = store.load(original.record.profile_id)
    assert rollback.record == original.record and file_sha256(source.manifest_path) == source_hash
    selector.status.setText('Generated candidate created; original profile reload verified. No LIVE readiness.')
    snap('04-candidate-and-rollback')
    report = {'scope': 'GENERATED SOFTWARE DEMO ONLY; no webcam, participant accuracy or readiness',
              'selected_label': 'NEUTRAL', 'collected_trials': session.completed,
              'valid_slots': len(session.features), 'original_manifest_unchanged': True,
              'old_profile_reload': True, 'settings_preserved': True,
              'candidate_requires_explicit_create': True,
              'candidate_model_changed': selector.loaded.model.model_version != original.model.model_version,
              'stages': ['01-selected-neutral', '02-count-review', '03-explicit-profile-review',
                         '04-candidate-and-rollback']}
    (folder / 'workflow.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    window.close()
    selector.close()
    print(json.dumps({'output': str(folder)}))


if __name__ == '__main__':
    main()
