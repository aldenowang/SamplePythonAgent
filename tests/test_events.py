from cmu_project.events import Event, EventBus, EventType
from conftest import RecordingListener


def test_listener_receives_events_in_order():
    bus = EventBus()
    rec = RecordingListener()
    bus.subscribe(rec)

    bus.emit(Event(EventType.USER_INPUT, 0, {"text": "a"}))
    bus.emit(Event(EventType.STOP, 0, {"text": "b"}))

    assert rec.types() == [EventType.USER_INPUT, EventType.STOP]


def test_faulty_listener_does_not_break_emit():
    bus = EventBus()

    class Boom:
        def on_event(self, event):
            raise RuntimeError("nope")

    rec = RecordingListener()
    bus.subscribe(Boom())
    bus.subscribe(rec)

    bus.emit(Event(EventType.NOTICE, 0, {"message": "hi"}))
    assert rec.types() == [EventType.NOTICE]


def test_lifecycle_values_match_claude_code_names():
    assert EventType.PRE_TOOL_USE.value == "PreToolUse"
    assert EventType.POST_TOOL_USE.value == "PostToolUse"
    assert EventType.SUBAGENT_START.value == "SubagentStart"
    assert EventType.SUBAGENT_STOP.value == "SubagentStop"
    assert EventType.STOP.value == "Stop"
