"""Deterministic oracle tests placeholder."""

import pytest
from app.oracle import answer_question

@pytest.fixture
def iris_csv():
    return "examples/iris.csv"

def test_row_count_iris(iris_csv):
    assert answer_question("How many rows are there?", iris_csv) == 3
    assert answer_question("row count", iris_csv) == 3

def test_column_names_iris(iris_csv):
    expected = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
    assert answer_question("What are the column names?", iris_csv) == expected
    assert answer_question("list columns", iris_csv) == expected

def test_unsupported_question(iris_csv):
    with pytest.raises(ValueError):
        answer_question("What is the capital of France?", iris_csv)