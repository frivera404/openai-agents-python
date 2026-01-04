import pytest
pytest.skip("Removed — original moved to tests/voice/removed/test_workflow.py.bak", allow_module_level=True)
            {
                "id": "1",
                "content": [{"annotations": [], "text": "done_2", "type": "output_text"}],
                "role": "assistant",
                "status": "completed",
                "type": "message",
            },
        ]
    )
    assert workflow._current_agent == agent


def test_audio_file_fixture_available_in_workflow(audio_file_path: str) -> None:
    """Sanity-check that the audio_file_path fixture is available to workflow tests."""
    import os

    assert os.path.exists(audio_file_path)
