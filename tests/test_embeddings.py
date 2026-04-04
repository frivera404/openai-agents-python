from workflows.agent_system import embeddings


def test_get_embedding_fallback_shapes():
    v = embeddings.get_embedding("hello world")
    assert isinstance(v, list)
    assert len(v) >= 1
    assert all(isinstance(x, (float, int)) for x in v)
