"""Tests for agent functionality: Markdown table formatting and file output handling."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import types
import openai
import pytest

from app.agent import main as agent_main

class DummyChoice:
    def __init__(self, content):
        # For ChatCompletion response
        self.message = types.SimpleNamespace(content=content)

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

def test_table_output(monkeypatch):
    # Mock pandas to ensure DataFrame.to_markdown works without actual pandas
    import sys, types
    dummy_pd = types.ModuleType('pandas')
    class DummyDataFrame:
        def __init__(self, data): self._data = data
        def to_markdown(self, index=False):
            keys = list(self._data[0].keys())
            header = "| " + " | ".join(keys) + " |"
            sep = "| " + " | ".join(['---'] * len(keys)) + " |"
            rows = ["| " + " | ".join(str(row[k]) for k in keys) + " |" for row in self._data]
            return "\n".join([header, sep] + rows)
    dummy_pd.DataFrame = DummyDataFrame
    monkeypatch.setitem(sys.modules, 'pandas', dummy_pd)
    # Mock ChatCompletion to return code that prints a list of dicts
    def fake_chatcompletion_create(*args, **kwargs):
        return DummyResponse("print([{'col1': 1, 'col2': 2}, {'col1': 3, 'col2': 4}])")
    monkeypatch.setattr(openai.ChatCompletion, 'create', fake_chatcompletion_create)
    # Mock run_python to return the printed repr
    def fake_run_python(code, globals_dict=None, timeout=None):
        return {
            'stdout': "[{'col1': 1, 'col2': 2}, {'col1': 3, 'col2': 4}]\n",
            'stderr': '',
            'exit_code': 0,
            'timeout': False,
            'files': []
        }
    import app.agent as agent_mod
    monkeypatch.setattr(agent_mod, 'run_python', fake_run_python)
    # Call agent_main with a non-oracle question
    result = agent_main("some table request", "examples/iris.csv")
    # Expected Markdown table
    assert isinstance(result, str)
    # Check header and rows
    assert "| col1 | col2 |" in result
    assert "| 1 | 2 |" in result
    assert "| 3 | 4 |" in result

def test_file_output(monkeypatch):
    # Mock ChatCompletion to return trivial code
    def fake_chatcompletion_create(*args, **kwargs):
        return DummyResponse("print('done')")
    monkeypatch.setattr(openai.ChatCompletion, 'create', fake_chatcompletion_create)
    # Mock run_python to return file outputs
    def fake_run_python(code, globals_dict=None, timeout=None):
        return {
            'stdout': '',
            'stderr': '',
            'exit_code': 0,
            'timeout': False,
            'files': ['agent_outputs/123_chart.png', 'agent_outputs/123_plot.jpg']
        }
    import app.agent as agent_mod
    monkeypatch.setattr(agent_mod, 'run_python', fake_run_python)
    result = agent_main("generate chart", "examples/iris.csv")
    assert isinstance(result, dict)
    assert 'files' in result
    assert result['files'] == ['agent_outputs/123_chart.png', 'agent_outputs/123_plot.jpg']