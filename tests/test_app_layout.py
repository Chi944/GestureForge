import os
from pathlib import Path

import numpy as np
import pytest

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from gestureforge.app import Window


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


def test_studio_workflow_scroll_does_not_displace_camera_controls(qapp) -> None:
    window = Window(model=object(), studio=True)
    window.resize(900, 620)
    window.show()
    qapp.processEvents()
    try:
        window.deck_tabs.setCurrentWidget(window.practice_page)
        window.practice_negative_cues.setMinimumHeight(1200)
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
