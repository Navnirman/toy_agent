# CSV Data-Analyst Agent Toy Project

Natural-language Q&A over any CSV by planning, writing, and running pandas code.

## Usage

CLI:

    python -m app.run "<question>" path/to/file.csv

API (with FastAPI/uvicorn):

    uvicorn app.api:app --reload --port 8000