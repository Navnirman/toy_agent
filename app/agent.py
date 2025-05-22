"""
Planner–executor loop for CSV Data-Analyst Agent.
Implements a loop that generates pandas code via OpenAI Codex, executes it in a secure sandbox,
retries on errors up to MAX_RETRIES, and returns the processed result.
"""
import os
import re
import ast
import openai
from dotenv import load_dotenv
from app.tools import run_python
from app.memory import get_cache, set_cache

load_dotenv()

MAX_RETRIES = 8
CODE_MODEL = os.getenv("OPENAI_CODE_MODEL", "gpt-4.1-mini")

def extract_code(text: str) -> str:
    """
    Extract Python code from model response text.
    Looks for fenced code blocks; otherwise returns full text stripped.
    """
    pattern = r"```(?:python)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def post_process(raw: str):
    """
    Attempt to convert raw stdout string to Python object (int, float, list, dict).
    Falls back to stripped string.
    """
    raw = raw.strip()
    if not raw:
        return ""
    try:
        return ast.literal_eval(raw)
    except Exception:
        return raw

def main(question: str, csv_path: str):
    """
    Main entry: generate and execute pandas code to answer `question` on CSV at `csv_path`.
    Returns result as Python object or string.
    """
    print(f"[Agent] Question: {question}")
    if not os.path.exists(csv_path):
        raise ValueError(f"CSV file not found: {csv_path}")
    # Quick fallback to deterministic oracle for simple questions
    try:
        from app.oracle import answer_question
        return answer_question(question, csv_path)
    except ValueError:
        pass
    cache_key = f"{question}@@{csv_path}"
    print(f"[Agent] Cache key: {cache_key}")
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    system_prompt = (
        "You are an expert Python developer. Generate Python code using only pandas to answer the "
        "following question on a CSV file. The CSV file path is provided in the variable `csv_path`. "
        "Do not import any libraries other than pandas. Respond with only the code, without additional explanation.\n"
    )
    prev_code = None
    error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[Agent] Attempt {attempt}/{MAX_RETRIES}")
        # Build user message for ChatCompletion
        if prev_code is None:
            user_msg = f"# Question: {question}\n# Code:"
        else:
            user_msg = (
                f"# Question: {question}\n"
                f"# Previous code:\n```python\n{prev_code}\n```\n"
                f"# Error:\n{error}\n"
                "# Please provide corrected code only:\n"
            )
        print("[Agent] Generating code via OpenAI...")
        try:
            # Generate code via ChatCompletion
            response = openai.ChatCompletion.create(
                model=CODE_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=512,
                temperature=0,
                timeout=5,
            )
            text = response.choices[0].message.content
        except Exception as e:
            return f"OpenAI API error: {e}"
        code = extract_code(text)
        print(f"[Agent] Code generated:\n{code or '<empty>'}")
        # If model returned no code, retry
        if not code.strip():
            error = "No code generated"
            print(f"[Agent] {error}, retrying...")
            continue
        prev_code = code
        # Visualization enhancement: detect plotting code and generate chart via local tool
        try:
            plot_keywords = ['plt.', '.plot(', 'hist(', 'bar(', 'scatter(']
            if any(kw in code for kw in plot_keywords):
                from app.tools import plot_chart
                files = plot_chart(code, csv_path)
                return {'files': files}
        except Exception:
            pass
        print("[Agent] Executing code...")
        result = run_python(code, globals_dict={"csv_path": csv_path})
        print(f"[Agent] Execution completed (exit_code={result.get('exit_code')}, timeout={result.get('timeout')})")
        if result.get('stderr'):
            print(f"[Agent] Stderr:\n{result.get('stderr')}")
        # If any files were generated (e.g., plot images), return their paths
        files = result.get('files', []) or []
        if files:
            return {'files': files}
        # On execution errors or timeouts, retry
        if result.get("timeout") or result.get("exit_code") != 0:
            error = result.get("stderr") or result.get("stdout") or "Unknown error"
            continue
        raw_out = result.get("stdout", "")
        # Process stdout into Python object
        print(f"[Agent] Raw stdout:\n{raw_out}")
        processed = post_process(raw_out)
        # Reflection & self-critique
        print("[Agent] Reflecting on result certainty...")
        try:
            prompt_sys = (
                "You are an expert Python developer."
                " Evaluate whether the following result correctly answers the question." 
                "Respond with YES or NO on the first line, followed by a brief rationale.\n"
            )
            # Include the generated code in the reflection prompt for context
            prompt_user = (
                f"Question: {question}\n"
                "Code:\n```python\n" + code + "\n```\n"
                f"Result: {processed}"
            )
            refl = openai.ChatCompletion.create(
                model=CODE_MODEL,
                messages=[
                    {"role": "system", "content": prompt_sys},
                    {"role": "user", "content": prompt_user},
                ],
                max_tokens=128,
                temperature=0,
                timeout=1,
            )
            refl_text = refl.choices[0].message.content.strip()
            first = refl_text.splitlines()[0].strip().lower()
            if first.startswith('no'):
                # Low confidence, return rationale
                rationale = '\n'.join(refl_text.splitlines()[1:]).strip() or refl_text
                return {'low_confidence': rationale}
        except Exception:
            pass
        # Format DataFrame-like outputs as Markdown tables
        # Post-process for output formatting
        print("[Agent] Formatting final output...")
        final = processed
        try:
            import pandas as _pd
            if isinstance(processed, list) and processed and isinstance(processed[0], dict):
                final = _pd.DataFrame(processed).to_markdown(index=False)
            elif isinstance(processed, dict):
                final = _pd.DataFrame(processed).to_markdown(index=False)
        except Exception:
            pass
        set_cache(cache_key, final)
        return final
    return f"Failed to generate working code after {MAX_RETRIES} attempts. Last error:\n{error}"