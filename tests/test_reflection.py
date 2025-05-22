"""Tests for agent self-critique (reflection) functionality."""
import sys, os, types
import pytest

# Ensure app package importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import openai
from app.agent import main as agent_main

class DummyChoice:
    def __init__(self, content):
        self.message = types.SimpleNamespace(content=content)

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

def test_reflection_accept(monkeypatch):
    # Simulate code execution returning '42'
    def fake_run_python(code, globals_dict=None, timeout=None):
        return {'stdout': '42\n', 'stderr': '', 'exit_code': 0, 'timeout': False, 'files': []}
    monkeypatch.setattr('app.agent.run_python', fake_run_python)
    # Prepare responses: first for code-gen, second for reflection
    gen_resp = DummyResponse('print(42)')
    refl_resp = DummyResponse('YES\nResult is correct.')
    seq = [gen_resp, refl_resp]
    def fake_create(*args, **kwargs):
        return seq.pop(0)
    monkeypatch.setattr(openai.ChatCompletion, 'create', fake_create)
    # Agent should return integer 42
    result = agent_main('what is 6*7', 'examples/iris.csv')
    assert result == 42

def test_reflection_reject(monkeypatch):
    # Simulate code execution returning '100'
    def fake_run_python(code, globals_dict=None, timeout=None):
        return {'stdout': '100\n', 'stderr': '', 'exit_code': 0, 'timeout': False, 'files': []}
    monkeypatch.setattr('app.agent.run_python', fake_run_python)
    # First code-gen stub
    gen_resp = DummyResponse('print(100)')
    # Reflection says NO
    refl_resp = DummyResponse('NO\nThe calculation is incorrect.')
    seq = [gen_resp, refl_resp]
    def fake_create(*args, **kwargs):
        return seq.pop(0)
    monkeypatch.setattr(openai.ChatCompletion, 'create', fake_create)
    # Agent should return low_confidence dict
    result = agent_main('compute something', 'examples/iris.csv')
    assert isinstance(result, dict)
    assert 'low_confidence' in result
    assert 'The calculation is incorrect.' in result['low_confidence']