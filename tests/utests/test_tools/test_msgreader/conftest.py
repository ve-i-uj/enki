"""Test fixtures for supervisor configuration testing.

This module provides pytest fixtures specifically for testing supervisor
configuration files and mappings in a temporary, isolated environment.
"""

import os
import tempfile

import pytest


@pytest.fixture
def supervisor_mapping_config_file():
    """Fixture that creates a temporary configuration file with supervisor mapping.

    Creates a temporary .conf file containing a supervisor mapping entry.
    This is useful for testing configuration parsing with actual content.

    Yields:
        str: Path to the temporary configuration file with supervisor=3 entry.

    """
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".conf"
    ) as f:
        f.write("supervisor=3")
        temp_path = f.name

    yield temp_path  # pass the file path to the test

    # Cleanup after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)
