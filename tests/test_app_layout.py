import os
from pathlib import Path

import numpy as np
import pytest

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QToolButton

from gestureforge.app import Window
from gestureforge.contracts import RoutingMode


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    # Windows offscreen Qt does not discover the native theme font itself.
    font = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/segoeui.ttf"
    if font.is_file():
        QFontDatabase.addApplicationFont(str(font))
    yield app


@pytest.fixture(autouse=True)
def disable_logging(monkeypatch) -> None:
    monkeypatch.setattr(Window, "log", lambda _self, _event: None)


def _rect_in_window(window: Window, widget) -> bool:
    return window.rect().contains(widget.rect().translated(widget.mapTo(window, QPoint(0, 0))))


def _rect_in_workflow_viewport(window: Window, widget) -> bool:
    rect = widget.rect().translated(widget.mapTo(window.studio_scroll.viewport(), QPoint(0, 0)))
    return window.studio_scroll.viewport().rect().contains(rect)


def test_studio_workflow_scroll_does_not_displace_camera_controls(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        window.deck_tabs.setCurrentWidget(window.practice_page)
        window.practice_host.setMinimumHeight(1200)
        qapp.processEvents()

        assert window.studio_scroll.widget() is window.deck_tabs
        assert window.studio_scroll.verticalScrollBar().maximum() > 0
        assert window.studio_scroll.horizontalScrollBar().maximum() == 0

        for widget in (
            window.preview,
            window.prediction,
            window.state,
            window.progress,
            window.start_button,
            window.pause_button,
        ):
            assert widget.isVisible()
            assert _rect_in_window(window, widget)

        before = [widget.mapTo(window, QPoint(0, 0)).y() for widget in (window.preview, window.start_button)]
        window.studio_scroll.verticalScrollBar().setValue(window.studio_scroll.verticalScrollBar().maximum())
        qapp.processEvents()
        assert before == [widget.mapTo(window, QPoint(0, 0)).y() for widget in (window.preview, window.start_button)]

        window.open_setup_page()
        window.readiness_status.setMinimumHeight(700)
        qapp.processEvents()
        assert window.deck_tabs.currentWidget() is window.studio_setup_panel
        assert window.studio_scroll.verticalScrollBar().maximum() > 0
        for widget in (window.preview, window.start_button, window.pause_button):
            assert widget.isVisible()
            assert _rect_in_window(window, widget)
    finally:
        window.close()


def test_practice_entry_controls_fit_half_width_workflow(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        window.deck_tabs.setCurrentWidget(window.practice_page)
        window.studio_scroll.verticalScrollBar().setValue(0)
        qapp.processEvents()

        for widget in (
            window.practice_status,
            window.practice_consent,
            window.practice_review_cues_button,
            window.practice_start_button,
        ):
            assert widget.isVisible()
            assert _rect_in_workflow_viewport(window, widget), widget.text()

        assert not window.practice_negative_cues.isVisible()
        assert window.studio_scroll.horizontalScrollBar().maximum() == 0

        overflow_buttons = [button for button in window.deck_tabs.findChildren(QToolButton) if button.isVisible()]
        assert overflow_buttons
        assert {button.text() for button in overflow_buttons} == {"‹", "›"}
        for button in overflow_buttons:
            assert button.palette().button().color().name().lower() == "#223247"
            assert _rect_in_window(window, button)
            assert button.accessibleName() in {"Scroll tabs left", "Scroll tabs right"}
        left = next(button for button in overflow_buttons if button.text() == "‹")
        previous = window.deck_tabs.tabBar().tabRect(0).x()
        left.click()
        qapp.processEvents()
        assert window.deck_tabs.tabBar().tabRect(0).x() > previous
    finally:
        window.close()


def test_negative_cue_dialog_keeps_readable_editor_and_editable_cues(qapp) -> None:
    window = Window(model=object(), studio=True)
    try:
        window.practice_cues_dialog.show()
        qapp.processEvents()
        editor = window.practice_negative_cues
        assert editor.palette().base().color().name() == "#0c1620"
        assert editor.palette().text().color().name() == "#e8eef4"
        assert not editor.isReadOnly()
        cues = list(window._practice_negative_cue_values())
        cues[0] = "Keep both hands below the camera."
        editor.setPlainText("\n".join(cues))
        assert window._practice_negative_cue_values() == tuple(cues)
    finally:
        window.practice_cues_dialog.close()
        window.close()


def test_active_practice_actions_fit_half_width_workflow(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        window.deck_tabs.setCurrentWidget(window.practice_page)
        window.practice_consent.setChecked(True)
        assert window.start_practice_rehearsal()
        qapp.processEvents()
        qapp.processEvents()

        assert window.practice_widget is not None
        assert not window.practice_status.isVisible()
        assert not window.practice_consent.isVisible()
        assert not window.practice_review_cues_button.isVisible()
        assert not window.practice_start_button.isVisible()
        assert window.practice_negative_cues.isReadOnly()
        assert _rect_in_workflow_viewport(window, window.practice_widget.prepare_button)
        assert _rect_in_workflow_viewport(window, window.practice_widget.begin_button)

        window.resize(1150, 740)
        window._scroll_practice_actions_into_view()
        qapp.processEvents()
        assert _rect_in_workflow_viewport(window, window.practice_widget.prepare_button)
        assert _rect_in_workflow_viewport(window, window.practice_widget.begin_button)
        assert window.studio_scroll.horizontalScrollBar().maximum() == 0
    finally:
        window.close()


def test_studio_preview_preserves_frame_corners_after_resize(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:80, :80] = (0, 0, 255)
        frame[:80, -80:] = (0, 255, 0)
        frame[-80:, :80] = (255, 0, 0)
        frame[-80:, -80:] = (0, 255, 255)
        window._display_capture_frame(frame)
        qapp.processEvents()

        window.resize(1150, 740)
        qapp.processEvents()
        image = window.preview.pixmap().toImage()

        samples = [
            image.pixelColor(4, 4),
            image.pixelColor(image.width() - 5, 4),
            image.pixelColor(4, image.height() - 5),
            image.pixelColor(image.width() - 5, image.height() - 5),
        ]
        assert all(color.alpha() == 255 for color in samples)
        assert sum(color.red() > 180 for color in samples) >= 2
        assert sum(color.green() > 180 for color in samples) >= 2
        assert sum(color.blue() > 180 for color in samples) >= 1
        assert window.preview.alignment() == Qt.AlignmentFlag.AlignCenter
    finally:
        window.close()


def test_studio_workflow_scroll_height_tracks_active_tab(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        window.open_setup_page()
        window.readiness_status.setMinimumHeight(1800)
        qapp.processEvents()
        setup_scroll = window.studio_scroll.verticalScrollBar().maximum()
        assert setup_scroll > 1000

        window.deck_tabs.setCurrentWidget(window.practice_page)
        qapp.processEvents()
        practice_scroll = window.studio_scroll.verticalScrollBar().maximum()
        assert practice_scroll < setup_scroll - 600
        window.studio_scroll.verticalScrollBar().setValue(practice_scroll)
        qapp.processEvents()
        assert _rect_in_window(window, window.start_button)
        assert _rect_in_window(window, window.pause_button)
    finally:
        window.close()


def test_studio_long_saved_practice_review_bottom_is_reachable(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        long_guidance = "\n".join(
            [
                "Latest saved practice - historical visual regression.",
                *(f"Result detail {index}: hold, recovery and next-step guidance wraps across the panel."
                  for index in range(80)),
                "FINAL GUIDANCE SENTINEL: rerun the failed pose only after reviewing this line.",
            ]
        )
        window.practice_review_label.setText(long_guidance)
        window.deck_tabs.setCurrentWidget(window.summary_widget)
        qapp.processEvents()

        label = window.practice_review_label
        assert label.height() >= label.heightForWidth(label.width())
        assert window.studio_scroll.verticalScrollBar().maximum() > 0

        window.studio_scroll.verticalScrollBar().setValue(window.studio_scroll.verticalScrollBar().maximum())
        qapp.processEvents()
        label_bottom = label.mapTo(window.studio_scroll.viewport(), QPoint(0, label.height() - 1)).y()
        assert 0 <= label_bottom < window.studio_scroll.viewport().height()
    finally:
        window.close()


def test_studio_saved_practice_review_resizes_when_text_changes_at_same_width(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        window.deck_tabs.setCurrentWidget(window.summary_widget)
        qapp.processEvents()
        label = window.practice_review_label
        width = label.width()
        long_text = "\n".join(
            f"Long guidance line {index}: this wraps and must expand at the same width."
            for index in range(70)
        )
        short_text = "Short review."

        label.setText(long_text)
        qapp.processEvents()
        long_height = label.minimumHeight()

        label.setText(short_text)
        qapp.processEvents()
        short_height = label.minimumHeight()

        label.setText(long_text)
        qapp.processEvents()
        restored_height = label.minimumHeight()

        assert label.width() == width
        assert short_height < long_height
        assert restored_height == label.heightForWidth(label.width())
        assert restored_height >= long_height
    finally:
        window.close()


def test_studio_setup_controls_fit_half_width_workflow(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        window.open_setup_page()
        qapp.processEvents()
        viewport = window.studio_scroll.viewport().rect()
        controls = [
            window.load_dataset_button,
            window.camera_picker,
            window.apply_camera_button,
            window.readiness_start_button,
            window.readiness_finish_button,
            window.mode_picker,
            *window.binding_pickers,
            window.apply_bindings_button,
            *window.file_tool_buttons,
        ]
        for widget in controls:
            rect = widget.rect().translated(widget.mapTo(window.studio_scroll.viewport(), QPoint(0, 0)))
            assert rect.left() >= viewport.left(), widget.objectName() or widget.text() if hasattr(widget, "text") else widget.accessibleName()
            assert rect.right() <= viewport.right(), widget.objectName() or widget.text() if hasattr(widget, "text") else widget.accessibleName()
        assert window.studio_scroll.horizontalScrollBar().maximum() == 0
        for button in window.file_tool_buttons:
            assert button.width() >= button.sizeHint().width(), button.text()
    finally:
        window.close()


def test_guest_setup_manual_mode_and_apply_are_visible_without_scrolling(qapp) -> None:
    window = Window(studio=True)
    window.resize(900, 620)
    window.show()
    try:
        assert window.use_studio_guest()
        window.open_setup_page()
        qapp.processEvents()

        assert (window.width(), window.height()) == (900, 620)
        assert window.studio_scroll.verticalScrollBar().value() == 0
        assert window.mode_picker.currentData() == RoutingMode.PREVIEW.value
        assert window.mode_picker.findText("Live") >= 0
        for widget in (window.mode_picker, window.apply_bindings_button):
            assert widget.isVisible() and widget.isEnabled()
            assert _rect_in_workflow_viewport(window, widget)
            assert widget.mapTo(window, QPoint(0, 0)).y() < window.camera_picker.mapTo(window, QPoint(0, 0)).y()
        assert window.worker is None
        assert window.studio_scroll.horizontalScrollBar().maximum() == 0
    finally:
        window.close()


def test_setup_camera_guidance_is_readable_in_the_narrow_workflow(qapp) -> None:
    window = Window(studio=True)
    window.resize(900, 620)
    window.show()
    try:
        window.open_setup_page()
        qapp.processEvents()
        guidance = window.camera_help
        window.studio_scroll.ensureWidgetVisible(guidance)
        qapp.processEvents()

        assert guidance.isVisible() and guidance.wordWrap()
        assert _rect_in_workflow_viewport(window, guidance)
        assert guidance.height() >= guidance.heightForWidth(guidance.width())
        assert "0" in guidance.text() and "first" in guidance.text()
        assert "1" in guidance.text() and "second" in guidance.text()
        assert "without starting" in guidance.text()
        assert "numbering varies" in guidance.text().lower()
        assert window.studio_scroll.horizontalScrollBar().maximum() == 0
    finally:
        window.close()
