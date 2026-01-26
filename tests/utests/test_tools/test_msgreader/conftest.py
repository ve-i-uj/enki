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


@pytest.fixture
def logger_mapping_config_file():
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".conf"
    ) as f:
        f.write("logger=4")
        temp_path = f.name

    yield temp_path  # pass the file path to the test

    # Cleanup after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def loginapp_mapping_config_file():
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".conf"
    ) as f:
        f.write("loginapp=11")
        temp_path = f.name

    yield temp_path  # pass the file path to the test

    # Cleanup after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def dbmgr_mapping_config_file():
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".conf"
    ) as f:
        f.write("dbmgr=6")
        temp_path = f.name

    yield temp_path  # pass the file path to the test

    # Cleanup after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def client_mapping_config_file():
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".conf"
    ) as f:
        f.write("client=1")
        f.write("\nloginapp=11")
        temp_path = f.name

    yield temp_path  # pass the file path to the test

    # Cleanup after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mapping_config_file():
    text = """client=1
supervisor=3
logger=4
interfaces=5
dbmgr=6
cellappmgr=7
baseappmgr=8
cellapp=9
baseapp=10
loginapp=11
"""
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".conf"
    ) as f:
        f.write(text)
        temp_path = f.name

    yield temp_path  # pass the file path to the test

    # Cleanup after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)
