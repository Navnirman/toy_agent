# Security & Sandbox Guidelines

## Isolation & Execution
- **Subprocess** or Docker container with `--network none`.
- **Filesystem**: Code runs in a temp dir; no write access outside.
- **Resource Limits**: 2 s CPU timeout, RLIMIT_AS for memory cap (e.g., 256 MB).

## Built-in & Module Restrictions
- **Whitelist Built-ins**: `print`, `len`, `sum`, `min`, `max`, `range`, `enumerate`.
- **Banned Modules**: `os`, `sys`, `subprocess`, `socket`, `shutil`, `pathlib`, `requests`, `urllib`.
- **Code Size**: Limit to ≤ 200 lines.

## Network & Data Safety
- **No external network**: block internet by default.
- **Timeout Retries**: Max 3 execution retries per question.
- **Audit Logs**: Record code hash, execution time, and resource usage.

## Security Testing
- Include pytest fixtures that attempt prohibited actions (e.g., `import os`) and confirm failures.
- Automate periodic sandbox config reviews and CI checks for policy compliance.

