"""Tests for the secure Python sandbox `run_python` tool."""
import subprocess
import pytest

from app.tools import run_python

def is_docker_available():
    try:
        res = subprocess.run(
            ["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
        )
        return res.returncode == 0
    except Exception:
        return False

docker_missing = not is_docker_available()

@pytest.mark.skipif(docker_missing, reason="Docker is not available")
def test_simple_print():
    result = run_python('print(1+2)')
    assert not result['timeout']
    assert result['exit_code'] == 0
    assert result['stdout'].strip() == '3'

@pytest.mark.skipif(docker_missing, reason="Docker is not available")
def test_import_os_forbidden():
    code = 'import os; print(\'ok\')'
    result = run_python(code)
    assert result['exit_code'] != 0
    # Should raise NameError or ImportError due to missing __import__
    assert 'NameError' in result['stderr'] or 'ImportError' in result['stderr']

@pytest.mark.skipif(docker_missing, reason="Docker is not available")
def test_timeout_infinite_loop():
    # Test that an infinite loop is terminated via timeout
    result = run_python('while True: pass', timeout=1)
    assert result['timeout'] is True
    assert result['exit_code'] is None