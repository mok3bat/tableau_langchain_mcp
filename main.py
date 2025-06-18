from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from pkg.simple_datasource_qa import run_query  # or initialize_simple_datasource_qa

app = FastAPI()

class ToolInput(BaseModel):
    question: str
    # plus any required connection fields (use environment vars or add fields)

class ToolOutput(BaseModel):
    results: str

@app.post("/tool/simple_datasource_qa", response_model=ToolOutput)
def query(payload: ToolInput):
    try:
        answer = run_query(question=payload.question, ...)  # add needed args
        return {"results": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8000)
