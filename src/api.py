from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import Orchestrator

app = FastAPI(title="IRIS API", description="Backend for Intelligent Retail Insights System")

# CORS Middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Orchestrator (Global instance)
# We load it continuously to keep FAISS indices in memory
print("Initializing Orchestrator...")
orchestrator = Orchestrator()
print("Orchestrator Ready.")

class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None

class QueryResponse(BaseModel):
    query: str
    sql: str
    result: list | dict | str | None
    latency: float
    logs: list[str]
    sql_reasoning: str | None = None

@app.get("/")
def health_check():
    return {"status": "ok", "service": "IRIS Backend"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Run the orchestrator
        # Orchestrator.run is now async to support ADK memory operations.
        response = await orchestrator.run(request.query, request.session_id)
        
        return QueryResponse(
            query=response.get("query"),
            sql=response.get("sql", ""),
            result=response.get("result"),
            latency=response.get("latency", 0.0),
            logs=response.get("logs", []),
            sql_reasoning=response.get("sql_reasoning")
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
