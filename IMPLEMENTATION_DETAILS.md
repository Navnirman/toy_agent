# Implementation Details (Milestone 1)

This document summarizes the code and tests added to implement **Milestone 1: CSV Ingestion & Oracle**.

## Summary
Implemented a deterministic oracle for answering simple questions about a CSV file without using pandas. Provided both a CLI and FastAPI interface to invoke the oracle.

## Package Structure Updates

### app/__init__.py
- Initialized `app` package with `__version__ = "0.1.0"`.

### app/oracle.py
- New module implementing `answer_question(question: str, csv_path: str) -> object`:
  - Supports questions:
    - Row count (`how many rows`, `row count`, `number of rows`) by reading the CSV via Python's `csv.reader`, counting lines minus header.
    - Column names (`column names`, `what are the column names`, `list columns`) by reading the header row.
  - Raises `ValueError` for unsupported questions.

### app/run.py
- Updated CLI entry point:
  - Parses `question` and `csv_path` via `argparse`.
  - Calls `answer_question` and prints result or error message.

### app/api.py
- New FastAPI application exposing an `/ask` endpoint:
  - Defines Pydantic models `AskRequest` and `AskResponse`.
  - POST `/ask` reads JSON `{ question, csv_path }`, invokes `answer_question`, and returns `{ result }`.
  - Returns HTTP 400 on file errors or unsupported questions.

### app/tools.py, app/memory.py, app/agent.py
- Stubs added as placeholders for future milestones (secure sandbox, memory, planner–executor loop).

## Test Suite

### tests/test_oracle.py
- Tests for `answer_question`:
  - Verifies correct row count for `examples/iris.csv`.
  - Verifies correct column names for `examples/iris.csv`.
  - Checks that unsupported questions raise `ValueError`.

### tests/test_api.py
- Tests for FastAPI `/ask` endpoint:
  - Valid row count and column names queries return 200 with correct JSON.
  - Invalid CSV path returns 400.
  - Unsupported question returns 400.

## Examples

### examples/iris.csv
- Sample CSV file with 3 data rows and 5 columns (`sepal_length`, `sepal_width`, `petal_length`, `petal_width`, `species`).

## Dependencies
- Core dependencies for Milestone 1:
  - `fastapi`, `httpx` (for API and testing)
  - `pytest` (for tests)
  - Standard library only for oracle (`csv` module)

## Testing
- All tests pass under the `csv_agent` virtual environment:
  ```bash
  source csv_agent/bin/activate
  python -m pytest -q
  ```

## Milestone 2 — Secure Code-Exec Sandbox (completed)
Implemented and tested the `run_python` sandbox tool in `app/tools.py`:
  - Static banning of dangerous modules (`os`, `sys`, `subprocess`, `socket`, `shutil`, `pathlib`, `requests`, `urllib`) via AST analysis.
  - Restricts built-ins to a whitelist (`print`, `len`, `sum`, `min`, `max`, `range`, `enumerate`).
  - Supports optional `globals_dict` injection into the sandboxed script.
  - Executes code inside a Docker container (`python:3.12-slim`) with:
    • `--network none`, `--memory=256m`, `--cpus .5`, `--rm`
    • Mounts only the temp script directory read-only.
  - Auto-pulls the Docker image if missing.
  - Captures `stdout`, `stderr`, `exit_code`, and a `timeout` flag.
  - Cleans up lingering containers on timeout.

Added pytest tests in `tests/test_tools.py` (all passing):
  - `test_simple_print`: verifies stdout capture.
  - `test_import_os_forbidden`: ensures banned modules cause ImportError.
  - `test_timeout_infinite_loop`: confirms timeout enforcement.

## Next Steps
- Proceed to **Milestone 3: Planner–Executor Loop** as per IMPLEMENTATION.md.

## Milestone 3 — Planner–Executor Loop (completed)
Implemented the core loop in `app/agent.py`:
  - Quick fallback to deterministic `answer_question` for simple row count and column name queries.
  - Caching via `app.memory` (stubbed) to avoid repeated OpenAI calls.
  - Chat-based code generation using OpenAI ChatCompletion (`gpt-4.1-mini` by default), with a 1s API timeout.
  - Code extraction from fenced blocks, static multi-attempt retry (up to 3) on execution errors.
  - Integrated secure execution sandbox (`app/tools.run_python`) to run pandas code in Docker.
  - CLI (`app/run.py`) and FastAPI (`app/api.py`) upgraded to invoke the agent loop instead of the static oracle.
  - Updated tests to import `app` and accept safe fallthrough for unsupported questions.

## Milestone 4 — Result Post-Processing (in progress)
Started updating the sandbox and agent to handle post-processing of outputs:
  - `app/tools.run_python` now mounts the sandbox directory as read-write and collects any output files (e.g., PNG charts) into a host-side `agent_outputs/` directory, exposing their paths via the `files` field.
  - `app/agent.main` now checks for generated files, returning their paths immediately.
  - Next steps:
    - Parse scalar and DataFrame outputs from `stdout` into Markdown tables using pandas parsing.
    - Support chart embedding or linking in CLI/API responses.
    - Optionally prompt the model for a natural-language summary of results.

## Milestone 5 — Agent Memory (completed)
Implemented a persistent cache layer in `app/memory.py`:
  - SQLite-based KV store (`agent_memory.db` by default) with thread-safe access via `threading.Lock`.
  - Schema: `(key TEXT PRIMARY KEY, result TEXT JSON, timestamp TEXT)`.
  - Configurable database path via `AGENT_MEMORY_DB` environment variable.
  - `get_cache(key)`: retrieves and JSON-decodes stored results (or returns raw string or `None`).
  - `set_cache(key, result)`: JSON-encodes results and records UTC timestamp.
  - Integrated into `app/agent.main` to skip OpenAI calls and sandbox execution when a cache hit occurs.

### Tests for Memory
- `tests/test_memory.py`: verifies round-trip storage and retrieval using a temporary database file, ensuring persistence across module reloads.