"""Embeddable selected-pose repair using the existing enrolment handshake."""

from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from .enrolment_widget import EnrolmentWidget
from .pose_repair import PoseRepair
from .profiles import ProfileRecord
from .dataset import dataset_hashes, load_dataset


class PoseRepairWidget(EnrolmentWidget):
    candidate_ready = Signal(object)  # RepairCandidate; offer to selector, never auto train/load

    def __init__(self, output_root: Path, parent=None, **kwargs):
        super().__init__(output_root, parent, **kwargs)
        self.source: ProfileRecord | None = None
        self.repair: PoseRepair | None = None
        self.repair_manifest: Path | None = None
        self._collected_hashes: dict[str, str] | None = None
        self.source_notice = QLabel('Choose an existing saved profile before repairing one pose.')
        self.source_notice.setTextFormat(Qt.TextFormat.PlainText)
        self.source_notice.setWordWrap(True)
        self.repair_pose = QComboBox()
        self.repair_pose.setAccessibleName('Pose to repair')
        self.diagnosis = QLineEdit()
        self.diagnosis.setMaxLength(500)
        self.diagnosis.setPlaceholderText('Describe the reviewed diagnostic and intended pose')
        self.diagnostic_reviewed = QCheckBox('I reviewed the diagnostic and want to repair this pose.')
        self.count_review = QCheckBox('I reviewed the replacement and retained TRAIN counts.')
        self.count_review.setEnabled(False)
        self.candidate_button = QPushButton('Save separate TRAIN candidate')
        self.candidate_button.setEnabled(False)
        layout = self.layout()
        assert isinstance(layout, QVBoxLayout)
        layout.insertWidget(0, self.source_notice)
        layout.insertWidget(1, self.repair_pose)
        layout.insertWidget(2, self.diagnosis)
        layout.insertWidget(3, self.diagnostic_reviewed)
        layout.addWidget(self.count_review)
        layout.addWidget(self.candidate_button)
        self.dataset_saved.connect(self._collection_complete)
        self.candidate_button.clicked.connect(self.build_candidate)
        self.repair_pose.currentIndexChanged.connect(self._reset_review)
        self.diagnosis.textChanged.connect(self._reset_review)
        self.notice.setText('Collect one reviewed pose. The original data/profile stays available for rollback.')
        self.request_button.setText('Request selected-pose collection')
        # Identity/vocabulary come from the saved profile, not editable form inputs.
        self.participant.setReadOnly(True)
        self.hand.setEnabled(False)
        self.split.setEnabled(False)
        for field in self.pose_fields.values():
            field.setReadOnly(True)
        form = self.form.layout()
        assert isinstance(form, QFormLayout)
        for identity_widget in (self.participant, self.hand, self.split, *self.pose_fields.values()):
            form.setRowVisible(identity_widget, False)

    def _reset_review(self, *args):
        self.diagnostic_reviewed.setChecked(False)

    def set_source(self, source: ProfileRecord | None):
        if self.pending_plan is not None or (self.session is not None
                and self.session.state not in ('complete', 'cancelled')):
            raise ValueError('Finish or preserve the current repair before changing source')
        self.source = source
        self.repair = None
        self.repair_manifest = None
        self._collected_hashes = None
        self.count_review.setChecked(False)
        self.count_review.setEnabled(False)
        self.candidate_button.setEnabled(False)
        self.consent.setChecked(False)
        self.diagnosis.clear()
        self.repair_pose.clear()
        if source is None:
            self.source_notice.setText('Load a saved personal profile in Profiles before repairing one pose.')
            return
        self.repair_pose.addItems(list(source.vocabulary.labels))
        self.source_notice.setText(f'Original: {source.display_name} · {source.selected_hand} hand. '
                                   'A separate candidate replaces all TRAIN samples for the selected pose; '
                                   'it keeps the other poses\' samples. Retraining can change predictions '
                                   'for every pose. The original profile stays available.')

    def request_collection(self):
        try:
            if self.pending_plan is not None or (self.session is not None
                    and self.session.state not in ('complete', 'cancelled')):
                return
            if self.source is None:
                raise ValueError('Choose an existing saved profile')
            if not self.consent.isChecked() or not self.diagnostic_reviewed.isChecked():
                raise ValueError('Confirm numeric collection consent and review the diagnostic first')
            repair = PoseRepair(self.source, self.repair_pose.currentText(), self.diagnosis.text().strip())
            plan = repair.plan(self.trials.value(), self.setup.text().strip())
            self.repair = repair
            self.repair_manifest = None
            self._collected_hashes = None
            self.count_review.setChecked(False)
            self.count_review.setEnabled(False)
            self.candidate_button.setEnabled(False)
            self.request_plan(plan)
        except (OSError, ValueError) as exc:
            self.feedback.setText(str(exc))

    def refresh(self):
        super().refresh()
        # EnrolmentWidget.__init__ calls refresh before these fields exist.
        if not hasattr(self, 'repair_pose'):
            return
        if self.session is None:
            self.cue.setText('Choose one diagnosed pose and review the notes, then request collection.')
        elif self.session.state == 'complete':
            self.cue.setText('Selected-pose collection saved. Review counts before creating a separate TRAIN candidate.')
        busy = self.pending_plan is not None or (self.session is not None
                and self.session.state not in ('complete', 'cancelled'))
        for widget in (self.repair_pose, self.diagnosis, self.diagnostic_reviewed):
            widget.setEnabled(not busy)

    def _collection_complete(self, path: Path):
        try:
            self._collected_hashes = dataset_hashes(load_dataset(path))
        except (OSError, ValueError) as exc:
            self.feedback.setText(f'Cannot review collected data: {exc}')
            return
        self.repair_manifest = path
        session = self.session
        if session is None or self.repair is None:
            return
        valid = len(session.features)
        total = len(session.records)
        counts = {label: sum(r.intended_label == label
                             for r in self.repair.bundle.valid_records('train'))
                  for label in self.repair.source.vocabulary.labels}
        retained = ', '.join(f'{label}: {count}' for label, count in counts.items()
                             if label != self.repair.label)
        self.source_notice.setText(f'Collected {self.repair.label}: {valid}/{total} valid slots. '
                                   f'Replace {self.repair.label} TRAIN: {counts[self.repair.label]} -> {valid} '
                                   f'valid samples (not added). Retain TRAIN: {retained}. '
                                   'Retraining can change predictions for every pose; evaluate all poses '
                                   'and negative gestures before using the candidate. Original profile retained.')
        self.count_review.setEnabled(True)
        self.candidate_button.setEnabled(True)

    def build_candidate(self):
        try:
            if self.repair is None or self.repair_manifest is None or self.session is None:
                raise ValueError('Complete the selected-pose collection first')
            if self.session.state != 'complete':
                raise ValueError('Cancelled or unsaved repair cannot create a candidate')
            if dataset_hashes(load_dataset(self.repair_manifest)) != self._collected_hashes:
                raise ValueError('Collected data changed after counts were displayed; review again')
            candidate = self.repair.build_candidate(self.repair_manifest, self.output_root,
                                                    reviewed=self.count_review.isChecked(),
                                                    expected_repair_hashes=self._collected_hashes)
        except (OSError, ValueError) as exc:
            self.feedback.setText(f'Candidate not saved: {exc}. Original profile retained; retry when resolved.')
            return
        self.candidate_button.setEnabled(False)
        self.feedback.setText('Separate TRAIN candidate saved. Review it in Profiles, then explicitly '
                              'create/load a new profile. Reload the original profile to roll back.')
        self.candidate_ready.emit(candidate)
