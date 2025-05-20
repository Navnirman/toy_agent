"""Tests for FastAPI /ask endpoint."""
import shutil
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_ask_row_count(tmp_path):
    src = "examples/iris.csv"
    dest = tmp_path / "iris.csv"
    shutil.copy(src, dest)
    response = client.post("/ask", json={"question": "row count", "csv_path": str(dest)})
    assert response.status_code == 200
    assert response.json() == {"result": 3}

def test_ask_column_names(tmp_path):
    src = "examples/iris.csv"
    dest = tmp_path / "iris.csv"
    shutil.copy(src, dest)
    response = client.post("/ask", json={"question": "list columns", "csv_path": str(dest)})
    expected = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
    assert response.status_code == 200
    assert response.json() == {"result": expected}

def test_ask_bad_csv(tmp_path):
    bad = tmp_path / "no.csv"
    response = client.post("/ask", json={"question": "row count", "csv_path": str(bad)})
    assert response.status_code == 400

def test_unsupported_question(tmp_path):
    src = "examples/iris.csv"
    dest = tmp_path / "iris.csv"
    shutil.copy(src, dest)
    response = client.post("/ask", json={"question": "foo", "csv_path": str(dest)})
    assert response.status_code == 400