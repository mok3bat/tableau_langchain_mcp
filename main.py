from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from pkg.simple_datasource_qa import initialize_simple_datasource_qa

app = FastAPI()

# Tool Input and Output models
class ToolInput(BaseModel):
    question: str

class ToolOutput(BaseModel):
    results: str

# Initialize Tableau tool once using env vars
tool = initialize_simple_datasource_qa(
    domain=os.getenv("TABLEAU_DOMAIN"),
    site=os.getenv("TABLEAU_SITE"),
    jwt_client_id=os.getenv("TABLEAU_JWT_CLIENT_ID"),
    jwt_secret_id=os.getenv("TABLEAU_JWT_SECRET_ID"),
    jwt_secret=os.getenv("TABLEAU_JWT_SECRET"),
    tableau_user=os.getenv("TABLEAU_USER"),
    tableau_api_version=os.getenv("TABLEAU_API_VERSION", "3.17"),
    datasource_luid=os.getenv("TABLEAU_DATASOURCE_LUID"),
    tooling_llm_model=os.getenv("LLM_MODEL_NAME", "gpt-4o"),
)

@app.post("/tool/simple_datasource_qa", response_model=ToolOutput)
def query_tool(payload: ToolInput):
    try:
        answer = tool.run(payload.question)
        return {"results": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
