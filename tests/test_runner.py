from pathlib import Path

import cmu_project.llm as llm_module
from cmu_project.config import AgentConfig
from cmu_project.events import EventBus, EventType
from cmu_project.runner import AgentRunner
from cmu_project.tools import build_registry
from conftest import RecordingListener, ScriptedLLM, response, text_block, thinking, tool_use


def make_runner(llm, tmp_path, registry=None, depth=0):
    cfg = AgentConfig(api_key="x")
    bus = EventBus()
    rec = RecordingListener()
    bus.subscribe(rec)
    runner = AgentRunner(
        cfg=cfg, bus=bus, llm=llm, system_prompt="sys",
        registry=registry, workdir=tmp_path, depth=depth,
    )
    return runner, rec


def test_event_order_for_tool_turn(tmp_path):
    (tmp_path / "s.txt").write_text("hi", encoding="utf-8")
    llm = ScriptedLLM([
        response([thinking("read it"), tool_use("t1", "read_file", {"path": "s.txt"})], "tool_use"),
        response([text_block("done")], "end_turn"),
    ])
    runner, rec = make_runner(llm, tmp_path, registry=build_registry(allow_subagent=False))
    runner.run_turn("read s.txt")
    assert rec.types() == [
        EventType.USER_INPUT,
        EventType.THINKING,
        EventType.PRE_TOOL_USE,
        EventType.POST_TOOL_USE,
        EventType.AGENT_TEXT,
        EventType.STOP,
    ]


def test_unknown_tool_is_recoverable(tmp_path):
    llm = ScriptedLLM([
        response([tool_use("t1", "does_not_exist", {})], "tool_use"),
        response([text_block("recovered")], "end_turn"),
    ])
    runner, rec = make_runner(llm, tmp_path, registry=build_registry(allow_subagent=False))
    final = runner.run_turn("go")
    assert final == "recovered"
    post = [e for e in rec.events if e.type == EventType.POST_TOOL_USE][0]
    assert post.payload["is_error"] is True


def test_tool_output_truncation(tmp_path):
    big = "x" * 5000
    (tmp_path / "big.txt").write_text(big, encoding="utf-8")
    llm = ScriptedLLM([
        response([tool_use("t1", "read_file", {"path": "big.txt"})], "tool_use"),
        response([text_block("ok")], "end_turn"),
    ])
    runner, rec = make_runner(llm, tmp_path, registry=build_registry(allow_subagent=False))
    runner.cfg.max_tool_output_chars = 100
    runner.run_turn("read big")
    post = [e for e in rec.events if e.type == EventType.POST_TOOL_USE][0]
    assert "truncated" in post.payload["content"]


def test_subagent_lifecycle(tmp_path, monkeypatch):
    # Child LLM is constructed inside the subagent tool; patch the class.
    def child_factory(cfg, client=None):
        return ScriptedLLM([
            response([thinking("child"), text_block("child summary")], "end_turn")
        ])

    monkeypatch.setattr(llm_module, "LLMClient", child_factory)

    parent_llm = ScriptedLLM([
        response([tool_use("s1", "spawn_subagent", {"task": "do it"})], "tool_use"),
        response([text_block("parent done")], "end_turn"),
    ])
    runner, rec = make_runner(parent_llm, tmp_path, registry=build_registry(allow_subagent=True))
    runner.run_turn("delegate")

    types = rec.types()
    assert EventType.SUBAGENT_START in types
    assert EventType.SUBAGENT_STOP in types
    # Child ran at depth 1 and must NOT emit STOP.
    assert not [e for e in rec.events if e.type == EventType.STOP and e.depth == 1]
    # Exactly one STOP, from the main agent at depth 0.
    assert [e.depth for e in rec.events if e.type == EventType.STOP] == [0]
    # Child thinking happened at depth 1.
    assert any(e.type == EventType.THINKING and e.depth == 1 for e in rec.events)


def test_subagent_registry_excludes_spawn():
    assert "spawn_subagent" in build_registry(allow_subagent=True).names()
    assert "spawn_subagent" not in build_registry(allow_subagent=False).names()
