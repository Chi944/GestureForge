import json
import os
from dataclasses import replace
from pathlib import Path
from time import monotonic
from typing import cast
from unittest.mock import Mock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from gestureforge.contracts import Action, ActionType
from gestureforge.dataset import save_dataset
from gestureforge.fixtures import synthetic_dataset
from gestureforge.profiles import LoadedProfile, ProfileStore
from gestureforge.shortcuts import Target, TargetKind
from gestureforge.workspace import Binding, Stage, Workspace


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def isolated_app_state(tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path / "enrolment")
    monkeypatch.setattr(app_module.Window, "log", lambda self, record: None)


def generated_store(tmp_path) -> tuple[ProfileStore, Path, LoadedProfile, LoadedProfile]:
    bundle = synthetic_dataset(trials_per_label_per_split=2, seed=304)
    records = tuple(
        replace(record, participant_id="GENERATED_TEST", hand="Right", provenance="human")
        for record in bundle.records
    )
    source = save_dataset(
        tmp_path / "generated",
        records,
        bundle.features,
        {"chosen_hand": "Right", "warning": "GENERATED SOFTWARE TEST ONLY"},
    )
    assert source.manifest_path is not None
    store = ProfileStore(tmp_path / "profiles")
    first = store.create("Alpha profile", source.manifest_path, "Right", consent=True)
    second = store.create("Bravo profile", source.manifest_path, "Right", consent=True)
    return store, source.manifest_path, first, second


def deck_file(path: Path) -> Path:
    path.write_text(json.dumps({
        "schema_version": 1,
        "deck_id": "deck-test",
        "title": "Deck Test",
        "cards": [
            {"id": "intro", "title": "Intro", "body": "One"},
            {"id": "done", "title": "Done", "body": "Two"},
        ],
    }), encoding="utf-8")
    return path


def select_profile(widget, profile_id):
    for index in range(widget.profiles.count()):
        item = widget.profiles.item(index)
        if item.data(Qt.ItemDataRole.UserRole) == profile_id:
            widget.profiles.setCurrentItem(item)
            return
    raise AssertionError(f"missing profile {profile_id}")


def finish(window, selector):
    deadline = monotonic() + 15
    while (selector.busy or window.model_loader is not None) and monotonic() < deadline:
        QApplication.processEvents()
    assert not selector.busy, selector.status.text()
    assert window.model_loader is None, window.notice.text()


def test_profile_selector_load_guest_reload_rename_delete_and_start_request(tmp_path, monkeypatch, qapp):
    from gestureforge.app import Window

    store, _source, first, second = generated_store(tmp_path)
    window = Window(studio=True, profile_store=store)
    selector = window.profile_selector
    try:
        select_profile(selector, first.record.profile_id)
        selector.load_button.click()
        finish(window, selector)
        assert window.selected_profile_id == first.record.profile_id
        assert selector.loaded is not None and selector.loaded.record.profile_id == first.record.profile_id

        start = Mock()
        monkeypatch.setattr(window, "start_camera", start)
        other_selection = second.selection
        selector.loaded = second
        selector._current_label()
        selector.start_button.click()
        assert not start.called
        assert "no longer matches" in window.notice.text()

        selector.loaded = first
        selector._current_label()
        selector.start_button.click()
        start.assert_called_once_with()

        model = window.model
        assert window.routing is not None
        session = window.routing.snapshot.session_id
        selector.name.setText("Renamed Alpha")
        selector.rename_button.click()
        assert window.model is model
        assert window.routing.snapshot.session_id == session
        assert window.selected_profile_name == "Renamed Alpha"
        assert "Renamed Alpha" in window.camera_status.text()
        assert other_selection.profile_id == second.record.profile_id

        selector.guest_button.click()
        assert window.model is None
        assert selector.loaded is None
        assert "Guest" in selector.current.text()
        assert first.record.profile_id not in window._deleted_profile_ids

        select_profile(selector, second.record.profile_id)
        selector.load_button.click()
        finish(window, selector)
        assert window.selected_profile_id == second.record.profile_id

        monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes)
        selector.delete_button.click()
        assert window.selected_profile_id is None
        assert second.record.profile_id in window._deleted_profile_ids
        assert store.list_ids() == (first.record.profile_id,)
        assert selector.loaded is None
    finally:
        window.close()


def test_profile_selector_syncs_direct_shell_profile_guest_and_adhoc(tmp_path, qapp):
    from gestureforge.app import Window

    store, _source, first, _second = generated_store(tmp_path)
    window = Window(studio=True, profile_store=store)
    selector = window.profile_selector
    try:
        active = cast(LoadedProfile, first)
        assert active is not None
        window.use_studio_profile(active)
        assert selector.loaded is active
        assert "Alpha profile" in selector.current.text()

        assert window.use_studio_guest()
        assert selector.loaded is None
        assert "Guest" in selector.current.text()

        window.use_studio_model(active.model, "Right", "P02", active.record.vocabulary)
        assert selector.loaded is None
        assert "Ad-hoc dataset" in selector.current.text()
    finally:
        window.close()


def test_profile_selector_busy_blocks_competing_shell_controls(tmp_path, qapp):
    from gestureforge.app import Window

    store, source, first, _second = generated_store(tmp_path)
    window = Window(studio=True, profile_store=store)
    selector = window.profile_selector
    try:
        window.use_studio_profile(first)
        assert selector.loaded is not None
        selector._future = Mock()
        selector._controls()
        window.set_profile_selector_busy(True)

        assert not window.load_studio_dataset(source)
        assert not window.load_studio_profile(store, first.record.profile_id)
        assert window.start_camera() is None
        deck_path = deck_file(tmp_path / "deck.json")
        blocked_workspace = Workspace("blocked", "Blocked")
        before = (window.selected_profile_id, window.workspace.id, window.viewer.deck.deck_id)

        assert not window.load_studio_deck(deck_path)
        assert not window.use_studio_workspace(blocked_workspace)
        assert not window.use_quick_actions_context()
        assert not window.use_studio_guest()
        with pytest.raises(ValueError, match="profile selector"):
            window.use_studio_profile(first)
        with pytest.raises(ValueError, match="profile selector"):
            window.use_studio_model(first.model, "Right", "adhoc", first.record.vocabulary)
        with pytest.raises(ValueError, match="profile selector"):
            window.configure_studio(context_id="blocked-context")
        with pytest.raises(ValueError, match="profile selector"):
            window.set_studio_camera(1)

        window.quick_actions_widget.state_path = tmp_path / "targets.json"
        candidate = window.quick_registry.copy()
        candidate.configure(Target("calc", "Calculator", TargetKind.BUILTIN, "calculator"))
        with pytest.raises(ValueError, match="shell rejected"):
            window.quick_actions_widget._publish(candidate)
        assert not window.quick_actions_widget.state_path.exists()
        assert (window.selected_profile_id, window.workspace.id, window.viewer.deck.deck_id) == before
    finally:
        selector._future = None
        window.set_profile_selector_busy(False)
        window.close()


def test_profile_selector_hidden_host_load_still_installs(tmp_path, qapp):
    from gestureforge.app import Window

    store, _source, first, _second = generated_store(tmp_path)
    window = Window(studio=True, profile_store=store)
    selector = window.profile_selector
    try:
        select_profile(selector, first.record.profile_id)
        selector.load_button.click()
        selector.hide()
        finish(window, selector)
        assert window.selected_profile_id == first.record.profile_id
        assert selector.loaded is not None and selector.loaded.record.profile_id == first.record.profile_id
    finally:
        window.close()


def test_profile_selector_host_load_restores_runbook_and_quick_actions_context(tmp_path, qapp):
    from gestureforge.app import Window

    store, _source, first, _second = generated_store(tmp_path)
    window = Window(studio=True, profile_store=store)
    selector = window.profile_selector
    try:
        from gestureforge.viewer import load_deck

        deck = load_deck(deck_file(tmp_path / "runbook-deck.json"))
        workspace = Workspace(
            "training",
            "Training",
            deck,
            stages=(
                Stage(
                    "intro",
                    "Intro",
                    "Use Quick Actions during profile load.",
                    "intro",
                    (Binding("G1", Action(ActionType.NEXT)),),
                ),
            ),
        )
        assert window.use_studio_workspace(workspace)
        window.quick_actions_widget.state_path = tmp_path / "quick-actions.json"
        candidate = window.quick_registry.copy()
        candidate.configure(Target("calc", "Calculator", TargetKind.BUILTIN, "calculator"))
        candidate.bind_quick(("calc", None, None))
        window.quick_actions_widget._publish(candidate)
        assert window.use_quick_actions_context()
        assert window.runbook is not None and window.runbook.current_stage is not None
        assert window.quick_actions_active

        select_profile(selector, first.record.profile_id)
        selector.load_button.click()
        finish(window, selector)

        assert window.selected_profile_id == first.record.profile_id
        assert selector.loaded is not None and selector.loaded.record.profile_id == first.record.profile_id
        assert window.runbook is not None and window.runbook.current_stage.id == "intro"
        assert window.quick_actions_active
        assert window.routing_manual_only is False
        assert window.manual_context_id == window.quick_actions_context_id
        assert window.routing is not None
        assert window.routing.snapshot.context_id == window.quick_actions_context_id
        assert "Previous selection retained" not in window.notice.text()
    finally:
        window.close()


def test_profile_selector_cli_loaded_profile_hydrates_request_button(tmp_path, qapp):
    from gestureforge.app import Window

    store, _source, first, _second = generated_store(tmp_path)
    window = Window(
        first.model,
        studio=True,
        profile=first.record.profile_id,
        vocabulary=first.record.vocabulary,
        profile_display_name=first.record.display_name,
        profile_store=store,
        loaded_profile=first,
    )
    try:
        assert window.profile_selector.loaded is first
        assert window.profile_selector.start_button.isEnabled()
        assert "Alpha profile" in window.profile_selector.current.text()
    finally:
        window.close()
