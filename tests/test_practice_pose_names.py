"""Practice pose names are display metadata, never classifier label remapping."""
from test_practice import Harness


def test_practice_widget_shows_actual_profile_pose_names_without_changing_labels(tmp_path):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from gestureforge.practice_widget import PersonalRehearsalWidget
    app = QApplication.instance() or QApplication([])
    h = Harness()
    names = {'G1': 'Closed fist', 'G2': 'Thumb up', 'G3': 'Index and middle fingers raised',
             'NEUTRAL': 'Open palm'}
    widget = PersonalRehearsalWidget(h.attempt, tmp_path, clock=lambda: h.now, gesture_names=names)
    try:
        assert widget.pose_key.textFormat() == Qt.TextFormat.PlainText
        for pose, name in names.items():
            assert f'{pose} — {name}' in widget.pose_key.text()
        assert 'G1 — Closed fist 1/3' in widget.prompt.text()
        assert 'G2 — Thumb up' in widget.test_selection.itemText(2)
        widget.test_selection.setCurrentIndex(3)
        assert 'G3 — Index and middle fingers raised 1/1' in widget.prompt.text()
        assert h.attempt.expected is not None
        assert h.attempt.expected.expected == 'G3'
        assert widget.test_selection.currentData() == 'G3'
        names['G3'] = 'Changed after practice started'
        widget.refresh()
        assert 'Changed after practice started' not in widget.prompt.text()
    finally:
        widget.close()
        app.processEvents()


def test_practice_widget_does_not_guess_custom_poses_without_names(tmp_path):
    from PySide6.QtWidgets import QApplication
    from gestureforge.practice_widget import PersonalRehearsalWidget
    app = QApplication.instance() or QApplication([])
    h = Harness()
    widget = PersonalRehearsalWidget(h.attempt, tmp_path, clock=lambda: h.now)
    try:
        assert widget.pose_key.text() == 'G1 | G2 | G3 | NEUTRAL'
        assert 'G1 1/3' in widget.prompt.text()
        assert 'fist' not in widget.prompt.text().lower()
    finally:
        widget.close()
        app.processEvents()


def test_practice_widget_keeps_custom_pose_names_literal(tmp_path):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from gestureforge.practice_widget import PersonalRehearsalWidget
    app = QApplication.instance() or QApplication([])
    h = Harness()
    widget = PersonalRehearsalWidget(
        h.attempt, tmp_path, clock=lambda: h.now, gesture_names={'G1': '<b>Pinch</b>'},
    )
    try:
        assert widget.prompt.textFormat() == Qt.TextFormat.PlainText
        assert 'G1 — <b>Pinch</b> 1/3' in widget.prompt.text()
        assert widget.test_selection.itemData(1) == 'G1'
        assert 'fist' not in widget.pose_key.text().lower()
    finally:
        widget.close()
        app.processEvents()


