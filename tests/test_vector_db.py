from workflows.agent_system import vector_db


def test_upsert_and_query_inmem():
    user = "test-user"
    vid = vector_db.make_vector_id()
    vec = [0.1] * 8
    meta = {"text": "hello"}
    vector_db.upsert(user, vid, vec, meta)
    results = vector_db.query(user, vec, top_k=1)
    assert len(results) == 1
    assert results[0][0]["text"] == "hello"
