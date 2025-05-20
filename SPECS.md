# CSV Data-Analyst Agent Toy Project

## Goal
Natural-language Q&A over any CSV by planning, writing, and running pandas code in a secure sandbox.

## Key Features
- **Tool Use**: Generates and executes pandas code in a sandbox environment.
- **Code Validation**: Automatic retry loop on errors up to 3 attempts.
- **Result Types**:
  - Scalar or small DataFrame answers as Markdown tables.
  - Optional PNG charts for trend or distribution queries.
- **Agent Skills**:
  - **Planning**: Decomposes NL questions into code steps.
  - **Execution**: Runs and validates code safely.
  - **Memory**: Caches code results for repeated queries.
  - **Reflection**: Self-critiques results and retries if needed.

## Usage
- **CLI**: `python -m app.run "<question>" path/to/file.csv`
- **API**: FastAPI endpoint at `/ask`, accepts JSON with `question` and `csv_path`.

## Repo Structure
```text
csv-agent/
├─ app/
│  ├─ agent.py       # planner–executor loop
│  ├─ tools.py       # secure code-exec sandbox
│  ├─ memory.py      # simple cache store
│  └─ run.py         # CLI entry point
├─ examples/
│  └─ iris.csv       # sample data
├─ tests/
│  └─ test_oracle.py # deterministic oracle tests
├─ SPECS.md
├─ IMPLEMENTATION.md
├─ SECURITY.md
├─ requirements.txt
├─ .env.example
└─ README.md
