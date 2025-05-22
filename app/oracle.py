"""
Deterministic oracle with hardcoded code snippets for known queries.
"""
"""
Deterministic oracle with hardcoded code snippets for known queries.
"""
import csv

def answer_question(question: str, csv_path: str):
    """
    Answer simple questions about a DataFrame using hardcoded logic.

    Supported questions (case-insensitive):
      - Row count (e.g., "how many rows", "row count")
      - Column names (e.g., "what are the column names")
    """
    q = question.strip().lower()
    if ("how many rows" in q) or ("row count" in q) or ("number of rows" in q):
        with open(csv_path, newline='') as f:
            reader = csv.reader(f)
            # subtract header
            count = sum(1 for _ in reader) - 1
        return count
    if ("column names" in q) or ("what are the column names" in q) or ("list columns" in q):
        with open(csv_path, newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
        return header
    raise ValueError(f"Unsupported question: {question}")