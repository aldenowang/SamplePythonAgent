from cmu_project.conversation import Conversation, tool_result_block


def test_assistant_blocks_stored_unchanged():
    convo = Conversation()
    blocks = [{"type": "thinking", "thinking": "x", "signature": "sig"}]
    convo.add_assistant_blocks(blocks)
    stored = convo.to_api()[-1]
    assert stored["role"] == "assistant"
    assert stored["content"] is blocks  # same object, verbatim


def test_tool_result_ids_match_tool_use_ids():
    convo = Conversation()
    convo.add_user_text("hi")
    results = [
        tool_result_block("tu_1", "ok"),
        tool_result_block("tu_2", "boom", is_error=True),
    ]
    convo.add_tool_results(results)
    msg = convo.to_api()[-1]
    assert msg["role"] == "user"
    assert [b["tool_use_id"] for b in msg["content"]] == ["tu_1", "tu_2"]
    assert msg["content"][1]["is_error"] is True
