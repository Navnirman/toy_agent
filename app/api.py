"""FastAPI API for CSV Data-Analyst Agent."""
"""FastAPI API for CSV Data-Analyst Agent."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.oracle import answer_question

class AskRequest(BaseModel):
    question: str
    csv_path: str

class AskResponse(BaseModel):
    result: object

app = FastAPI()

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        result = answer_question(request.question, request.csv_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")
    return {"result": result}