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