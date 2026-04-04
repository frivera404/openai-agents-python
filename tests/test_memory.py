from workflows.agent_system import memory


def test_memory_add_and_query():
    user = "mem-user"
    item = {"message": "I like apples", "text": "I like apples"}
    memory.add_long_term(user, item)
    results = memory.query_long_term(user, "apples", limit=5)
    assert isinstance(results, list)
    assert any("apples" in (r.get("message") or r.get("text") or "") for r in results)
