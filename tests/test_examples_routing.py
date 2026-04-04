from examples.agent_patterns import routing


def test_triage_handoffs_defined() -> None:
    """Ensure triage agent has the expected handoff agents defined."""
    assert hasattr(routing, "triage_agent")
    triage = routing.triage_agent
    assert hasattr(triage, "handoffs")
    names = [a.name for a in triage.handoffs]
    assert set(names) >= {"french_agent", "spanish_agent", "english_agent"}
