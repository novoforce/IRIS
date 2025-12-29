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

@app.get("/sessions")
async def list_sessions():
    """Returns a list of all sessions for the default user."""
    try:
        sessions = await orchestrator.memory_manager.list_sessions(
            orchestrator.app_name, 
            orchestrator.user_id
        )
        
        if sessions is None:
            return []
            
        # Format for frontend with fallbacks for s.id vs s.session_id
        results = []
        for s in sessions:
            # ADK Session doc says 'id' is the unique identifier.
            s_id = getattr(s, 'id', getattr(s, 'session_id', "unknown"))
            
            # Use 'last_update_time' from docs, or fallbacks
            created_at = "N/A"
            for time_field in ['last_update_time', 'created_time', 'created_at', 'lastUpdateTime']:
                if hasattr(s, time_field):
                    val = getattr(s, time_field)
                    if val:
                        created_at = str(val)
                        break
            
            # Add a title for the UI (can be first part of ID or a placeholder)
            title = f"Chat {s_id[:8]}" if len(s_id) > 8 else f"Chat {s_id}"
            
            results.append({
                "id": s_id, 
                "session_id": s_id, # for compatibility
                "created_at": created_at,
                "title": title
            })
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    """Returns the history of a specific session."""
    try:
        session = await orchestrator.memory_manager.get_session(
            orchestrator.app_name, 
            orchestrator.user_id, 
            session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert history to simplified format
        # Handle 'history', 'turns', 'messages', or 'events'
        turns = []
        for field in ['history', 'turns', 'messages', 'events']:
            if hasattr(session, field):
                attr = getattr(session, field)
                if isinstance(attr, list) and len(attr) > 0:
                    turns = attr
                    break
        
        history = []
        for turn in turns:
            try:
                # If wrapped in SessionEvent, unwrap it
                turn_data = turn
                if hasattr(turn, 'content') and hasattr(turn.content, 'parts'):
                    turn_data = turn.content
                
                # Determine role (check both turn and turn_data)
                role_val = getattr(turn_data, 'role', getattr(turn, 'role', 'user'))
                role = "user" if role_val == "user" else "bot"
                
                text = ""
                if hasattr(turn_data, 'parts') and turn_data.parts:
                    text = turn_data.parts[0].text
                elif hasattr(turn_data, 'content'):
                    text = str(turn_data.content)
                
                if text:
                    history.append({"role": role, "content": text})
            except Exception as e:
                print(f"Error parsing turn: {e}")
                continue
            
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions")
async def create_new_session():
    """Creates a new session explicitly."""
    import uuid
    new_id = str(uuid.uuid4())
    # Just return the ID, orchestrator creates it on use if needed, 
    # but we can pre-create to be safe.
    await orchestrator.memory_manager.create_session(
         orchestrator.app_name, 
         orchestrator.user_id, 
         new_id
    )
    return {"session_id": new_id}

