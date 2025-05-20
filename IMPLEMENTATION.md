
---

**IMPLEMENTATION.md**

```markdown
# Implementation Plan & Milestones

## Milestone 0 — Project Scaffolding (½ day)
- Initialize Git repo & Python venv.
- Install core deps in `requirements.txt`: `openai`, `pandas`, `matplotlib`, sandbox lib.
- Create skeleton directories and empty markdown docs.

## Milestone 1 — CSV Ingestion & Oracle (2 hrs)
- Build CLI/API loader: reads CSV into `pandas.DataFrame`.
- Create `oracle.py` with hardcoded code snippets for known queries (baseline test harness).

## Milestone 2 — Secure Code-Exec Sandbox (½ day)
- Implement `tools.run_python(code: str, globals: dict, timeout: int)`.
- Use subprocess (or Docker) isolation, enforce 2 s timeout and memory caps.
- Strip dangerous built-ins; ban filesystem/network access.

## Milestone 3 — Planner ↔ Executor Loop (1 day)
- System prompt: instruct Codex to generate pandas code only.
- Invoke OpenAI Codex, capture code output.
- Execute in sandbox, capture stdout/stderr.
- On errors, feed trace back to Codex with retry instructions (≤ 3 loops).

## Milestone 4 — Result Post-Processing (½ day)
- Detect output type:
  - **Scalar/DataFrame** → format as Markdown table.
  - **Chart** → save PNG and return file path or embed.
- Optionally ask Codex to summarize findings in one paragraph.

## Milestone 5 — Agent Memory (½ day)
- Implement KV store (`sqlite` or TinyDB) schema: `(hash, code, result, timestamp)`.
- Before Codex call: look up cache by question+schema hash.
- After success: store new entry.

## Milestone 6 — Reflection & Self-Critique (1 day)
- After execution, prompt Codex: “Is this result correct? YES/NO + rationale.”
- On NO, either retry or flag low confidence to user.

## Milestone 7 — Visualization Enhancement (Optional, 1 day)
- Add `plot_chart` tool: receives code body, returns `plt.gcf()`.
- Planner decides based on keywords (e.g., “trend”, “distribution”).

## Milestone 8 — Evaluation Harness & Stretch Goals
- Write Hypothesis + pytest tests to compare agent vs oracle on random CSVs.
- Extend to multi-CSV reasoning with joins.
- Implement streaming partial code generation (ReAct pattern).
- Add natural-language memory for common insights (e.g., “Sales spike in Q4”).
