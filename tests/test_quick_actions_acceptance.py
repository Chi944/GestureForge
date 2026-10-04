"""Studio-level Quick Actions acceptance regressions."""

from types import SimpleNamespace

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from gestureforge.app import Window
from gestureforge.contracts import Action, ActionType, RoutingMode
from gestureforge.shortcuts import Target, TargetKind, TargetRegistry
from gestureforge.vocabulary import GestureVocabulary
from gestureforge.workspace import Workspace


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def isolated_studio_state(tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path / "enrolment")
    monkeypatch.setattr(app_module.Window, "log", lambda self, record: None)


def _model(vocabulary: GestureVocabulary) -> SimpleNamespace:
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels,
        model_version="quick-actions-acceptance",
        config=SimpleNamespace(algorithm="knn", multiplier=2.0, margin=1.5),
    )


def _fill_registry() -> TargetRegistry:
    registry = TargetRegistry()
    for index in range(12):
        registry.configure(
            Target(
                f"target-{index:02d}",
                f"Local target {index:02d}",
                TargetKind.BUILTIN,
                "calculator" if index % 2 == 0 else "camera",
                True,
            )
        )
    registry.bind_quick(("target-00", "target-01", "target-02"))
    return registry


class LauncherSpy:
    def __init__(self) -> None:
        self.calls: list[tuple[Target, str]] = []

    def open(self, target: Target, resolved: str) -> None:
        self.calls.append((target, resolved))


def test_quick_actions_standalone_reload_rebind_recover_and_pause(qapp, tmp_path, monkeypatch):
    import gestureforge.app as app_module

    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    state_path = tmp_path / "studio" / "quick-actions-targets.json"
    registry = _fill_registry()
    registry.save(state_path)

    launcher = LauncherSpy()
    monkeypatch.setattr(app_module, "WindowsLauncher", lambda: launcher)
    monkeypatch.setattr(app_module, "UnsupportedLauncher", lambda: launcher)
    first = Window(model=_model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert first.use_studio_workspace(Workspace("quick-only", "Quick only"))
        assert first.viewer is not None and not first.deck_available
        assert first.runbook is not None and first.runbook.current_stage is None
        assert first.quick_registry.targets == registry.targets
        assert first.quick_registry.quick_slots == ("target-00", "target-01", "target-02")
        assert first.routing is not None and first.routing.state == "PAUSED"
        assert first.use_quick_actions_context()
        assert first.routing.snapshot.mode == RoutingMode.PREVIEW
        assert first.quick_actions_active
        assert launcher.calls == []

        first.quick_actions_widget.launch_buttons[0].click()
        assert first.session_summary.counts()["simulated"] == 1
        assert launcher.calls == []

        first.quick_actions_widget.slots[0].setCurrentIndex(first.quick_actions_widget.slots[0].findData("target-03"))
        assert first.quick_registry.quick_slots == ("target-03", "target-01", "target-02")
        assert len(first.quick_registry.targets) == 12
        assert not first.quick_actions_active
        assert first.use_quick_actions_context()
        assert dict(first.routing.snapshot.bindings)["G1"] == Action(ActionType.OPEN_SHORTCUT, "target-03")
    finally:
        first.close()

    second = Window(model=_model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert second.use_studio_workspace(Workspace("quick-only", "Quick only"))
        assert second.quick_registry.quick_slots == ("target-03", "target-01", "target-02")
        assert len(second.quick_registry.targets) == 12
        assert second.routing is not None and second.routing.state == "PAUSED"
        assert not second.quick_actions_active
        assert launcher.calls == []
        assert second.use_quick_actions_context()

        missing = tmp_path / "missing.txt"
        missing.write_text("temporary target", encoding="utf-8")
        candidate = second.quick_registry.copy()
        candidate.configure(Target("target-03", "Missing file", TargetKind.FILE, str(missing), True))
        second.quick_registry.replace_with(candidate)
        missing.unlink()
        assert not second.use_quick_actions_context()
        assert "repair target" in second.quick_actions_widget.status.text()
        assert not second.quick_actions_active
        assert launcher.calls == []

        candidate = second.quick_registry.copy()
        candidate.configure(Target("target-03", "Local target 03", TargetKind.BUILTIN, "camera", True))
        second.quick_registry.replace_with(candidate)
        assert second.use_quick_actions_context()
        # Manual LIVE requests do not require or manufacture a Practice grant.
        assert second._personal_live_grant is None
        assert second.configure_studio(mode=RoutingMode.LIVE)
        assert second.use_quick_actions_context()
        monkeypatch.setattr(second, "isActiveWindow", lambda: True)
        second.quick_actions_widget.launch_buttons[0].click()
        assert second.routing is not None and second.routing.state == "PAUSED"
        assert second.session_summary.counts()["launch_requested"] == 1
        assert len(launcher.calls) == 1

        second.routing.resume()
        monkeypatch.setattr(second, "isActiveWindow", lambda: False)
        second.changeEvent(QEvent(QEvent.Type.ActivationChange))
        assert second.routing.state == "PAUSED"
        assert "focus loss" in second.state.text()
    finally:
        second.close()
