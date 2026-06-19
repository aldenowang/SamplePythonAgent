from cmu_project.config import AgentConfig
from cmu_project.llm import build_request_kwargs

CFG = AgentConfig(api_key="x")


def test_tools_enable_auto_tool_choice():
    kwargs = build_request_kwargs(CFG, [], [{"name": "read_file"}], "sys")
    assert kwargs["tool_choice"] == {"type": "auto"}
    assert kwargs["tools"]


def test_no_tools_omits_tool_choice():
    kwargs = build_request_kwargs(CFG, [], [], "sys")
    assert "tool_choice" not in kwargs
    assert "tools" not in kwargs


def test_no_sampling_params():
    kwargs = build_request_kwargs(CFG, [], [], "sys")
    assert "temperature" not in kwargs
    assert "top_p" not in kwargs
    assert "top_k" not in kwargs


def test_thinking_display_summarized_and_budget_below_max():
    kwargs = build_request_kwargs(CFG, [], [], "sys")
    assert kwargs["thinking"]["type"] == "enabled"
    assert kwargs["thinking"]["display"] == "summarized"
    assert kwargs["thinking"]["budget_tokens"] < kwargs["max_tokens"]
