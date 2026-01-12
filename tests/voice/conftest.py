import os
import sys

import pytest

# Path to an external test audio file used by voice tests.
# Update this if you want tests to point at a different WAV file.
TEST_AUDIO_FILE = r"C:\Users\frive\Downloads\clip_2.wav"


# Skip voice tests on Python 3.9
def pytest_ignore_collect(collection_path, config):
    if sys.version_info[:2] == (3, 9):
        this_dir = os.path.dirname(__file__)

        if str(collection_path).startswith(this_dir):
            return True


@pytest.fixture(scope="session")
def audio_file_path() -> str:
    """Return the path to the WAV file used by voice tests."""
    return TEST_AUDIO_FILE
