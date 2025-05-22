"""Tests for agent memory (SQLite-based caching)."""
import sys
import os
import importlib
import tempfile

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_memory_roundtrip(tmp_path, monkeypatch):
    # Use a temporary DB file
    db_file = tmp_path / 'memory.db'
    monkeypatch.setenv('AGENT_MEMORY_DB', str(db_file))
    # Reload memory module to reinitialize with new DB path
    import app.memory as memory_mod
    importlib.reload(memory_mod)
    # Initially, cache is empty
    assert memory_mod.get_cache('test_key') is None
    # Store a complex object
    data = {'foo': 'bar', 'nums': [1, 2, 3]}
    memory_mod.set_cache('test_key', data)
    # Retrieve and verify
    result = memory_mod.get_cache('test_key')
    assert result == data
    # Reload again to ensure persistence
    importlib.reload(memory_mod)
    assert memory_mod.get_cache('test_key') == data