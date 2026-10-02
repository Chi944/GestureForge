from dataclasses import replace

from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode
from gestureforge.readiness import ReadinessCheck, behavior_revision
from gestureforge.routing import RoutingSession
from gestureforge.shortcuts import Target, TargetKind, TargetRegistry
from gestureforge.workspace import Binding, Stage, Workspace


def test_real_router_requires_six_activations_and_neutral_between_holds():
    bindings = {f'G{i}': Action(ActionType.NEXT) for i in (1, 2, 3)}
    router = RoutingSession('p1', 'model1', 'check', bindings, RoutingMode.REHEARSAL)
    check = ReadinessCheck('revision', tuple(bindings))
    router.resume()
    frame = 0

    def hold(label, frames):
        nonlocal frame
        for _ in range(frames):
            frame += 1
            now = frame / 10
            snapshot = router.snapshot
            prediction = Prediction(snapshot.session_id, 'p1', frame, now, label,
                                    label != 'UNKNOWN', 'model1', 'distance_rejection')
            event = router.process(prediction, now)
            if event:
                result = router.route(event, now)
                assert check.record(event, result, 'revision')
                assert not check.record(event, result, 'revision')

    hold('G1', 50)
    assert check.completed == 0  # no initial NEUTRAL
    for count, gesture in enumerate(('G1', 'G2', 'G3', 'G1', 'G2', 'G3'), 1):
        hold('NEUTRAL', 6)
        hold(gesture, 50)
        assert check.completed == count  # long hold cannot earn extra successes
    assert check.passed_for('revision')
    assert not check.passed_for('changed')


def test_wrong_pose_fails_even_when_both_poses_map_to_same_action():
    from gestureforge.contracts import CommandEvent, RoutingResult
    check = ReadinessCheck('revision', ('G1', 'G2', 'G3'))
    event = CommandEvent('e1', 's1', 'p1', 1, 'G2', 1)
    assert not check.record(event, RoutingResult('e1', action=Action(ActionType.NEXT)), 'revision')
    assert check.record(event, RoutingResult('e1', simulated_action=Action(ActionType.NEXT)), 'revision')
    assert check.status == 'failed'
    check.finish()
    assert not check.passed_for('revision')


def test_unknown_only_or_interrupted_check_cannot_pass():
    check = ReadinessCheck('revision', ('G1', 'G2', 'G3'))
    check.finish()
    assert check.status == 'failed'
    assert len(check.trials) == 6 and all(t.observed is None for t in check.trials)
    assert check.completed == 0
    check = ReadinessCheck('revision', ('G1', 'G2', 'G3'))
    check.cancel('Camera stopped')
    assert check.status == 'failed' and check.reason == 'Camera stopped'


def test_revision_covers_behavior_but_not_cosmetic_names():
    binding = Binding('G1', Action(ActionType.NEXT))
    stage = Stage('intro', 'Introduction', 'Start here', None, (binding,))
    workspace = Workspace('work', 'Training', stages=(stage,))
    registry = TargetRegistry()
    target = Target('calc', 'Calculator', TargetKind.BUILTIN, 'calculator')
    registry.configure(target)
    bindings = {'G1': binding.action}

    def revision(work=workspace, targets=registry, **changes):
        args = dict(profile_id='p1', model_version='model1', chosen_hand='Right',
                    workspace=work, registry=targets, bindings=bindings)
        args.update(changes)
        return behavior_revision(**args)

    original = revision()
    registry.configure(replace(target, label='My calculator'))
    assert revision(replace(workspace, title='Renamed', stages=(replace(stage, title='Renamed'),))) == original
    for changes in ({'profile_id': 'p2'}, {'model_version': 'model2'}, {'chosen_hand': 'Left'},
                    {'bindings': {'G1': Action(ActionType.PREVIOUS)}}):
        assert revision(**changes) != original
    assert revision(replace(workspace, stages=(replace(stage, bindings=()),))) != original
    registry.configure(replace(target, value='camera'))
    assert revision() != original
