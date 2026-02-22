"""Test fixtures for configuration file testing.

This module provides pytest fixtures for creating temporary configuration files
with different content for testing purposes. The fixtures handle automatic
cleanup of temporary files after test execution.
"""

import os
import shutil
import tempfile

import pytest


@pytest.fixture
def empty_mapping_config_file():
    """Fixture that creates a temporary empty configuration file.

    Creates a temporary file with .conf extension that contains no content.
    The file is automatically deleted after the test completes.

    Yields:
        str: Path to the temporary configuration file.

    """
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".conf"
    ) as f:
        f.write("")
        temp_path = f.name

    yield temp_path  # pass the file path to the test

    # Cleanup after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)
