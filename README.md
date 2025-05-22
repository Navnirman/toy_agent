# CSV Data-Analyst Agent Toy Project

Natural-language Q&A over any CSV by planning, writing, and running pandas code securely in a sandbox or local environment.

## Setup

Prerequisites:
- Python 3.12+
- Docker (optional, for secure sandbox execution)
- An OpenAI API key (set via `OPENAI_API_KEY` in `.env` or your shell)

1. Activate the provided virtual environment (recommended):
   ```bash
   source csv_agent/bin/activate
   ```

   Or create and activate your own venv and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the example environment file and configure your API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY
   ```

## Usage

### CLI

Ask a question about a CSV file:
```bash
python -m app.run "<question>" path/to/file.csv
```

Examples:
```bash
python -m app.run "row count" examples/iris.csv
python -m app.run "Plot the histogram of num11" examples/complex.csv
```

You will see step-by-step logs (`[Agent] ...`) followed by one of:
- A scalar or string result
- A Markdown table for tabular output
- Markdown image links (`![chart](...)`) for generated charts (saved in `agent_outputs/`)
- A `low_confidence` message if the agent is uncertain

### API (FastAPI)

Start the server:
```bash
uvicorn app.api:app --reload --port 8000
```

Send a POST request to `/ask`:
```bash
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question":"What is the average num5 per cat1?","csv_path":"examples/complex.csv"}'
```

Response JSON will include one of:
- `result`: a string or Markdown table
- `files`: list of chart file paths
- `low_confidence`: rationale for uncertain results

## Testing

Run the full test suite:
```bash
pytest -q
```