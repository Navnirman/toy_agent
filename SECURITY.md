# SECURITY.md

# Security & Sandbox Guidelines

## Docker Sandbox Requirement
- **Mandatory Docker**: All user-generated code must run inside Docker containers to ensure strong isolation.
- **Container flags**: Always use `--network none`, `--memory=256m`, and `--cpus=" .5"` for sandbox runs.
- **Ephemeral execution**: Containers are run with `--rm` and mount only the specific code file (read-only).

## Isolation & Execution
- **Subprocess wrapper**: Launch Docker from a parent process to apply timeouts and capture output.
- **Filesystem**: Containers mount only the temp directory containing the user script; no other host paths.
- **Resource Limits**: Enforced by Docker flags (`memory`, `cpus`) and `timeout` for CPU time.

## Built-in & Module Restrictions
- **Whitelist Built-ins**: `print`, `len`, `sum`, `min`, `max`, `range`, `enumerate`.
- **Banned Modules**: `os`, `sys`, `subprocess`, `socket`, `shutil`, `pathlib`, `requests`, `urllib`.
- **Code Size**: Limit to ≤ 200 lines.

## Network & Data Safety
- **No external network**: Docker `--network none` blocks all Internet access.
- **Timeout Retries**: Max 3 execution retries per question.
- **Audit Logs**: Record code hash, execution time, and resource usage.

## Security Testing
- Include pytest fixtures that attempt prohibited actions (e.g., `import os`) and confirm failures.
- Automate periodic sandbox config reviews and CI checks for policy compliance.
