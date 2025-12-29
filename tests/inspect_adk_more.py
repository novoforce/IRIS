
import asyncio
from google.adk.sessions import Session
try:
    from google.adk.sessions import Event
    print("Found Event in google.adk.sessions")
except ImportError:
    print("Event NOT in google.adk.sessions")

try:
    from google.adk.sessions import SessionEvent
    print("Found SessionEvent in google.adk.sessions")
except ImportError:
    print("SessionEvent NOT in google.adk.sessions")

from google.adk.sessions.database_session_service import DatabaseSessionService

async def main():
    print("\n--- Inspecting Session ---")
    print(dir(Session))
    
    # Try to see if it's a Pydantic model
    if hasattr(Session, 'model_fields'):
        print("Session Fields:", Session.model_fields.keys())
    
    print("\n--- Inspecting DatabaseSessionService ---")
    print(dir(DatabaseSessionService))
    
    db_url = "sqlite+aiosqlite:///tests/temp_db.db"
    service = DatabaseSessionService(db_url=db_url)
    
    print("\n--- Creating a test session ---")
    session = await service.create_session(app_name="test_app", user_id="test_user", session_id="test_sid")
    print("Created Session properties:", dir(session))
    print("Session ID:", getattr(session, 'id', 'N/A'))
    print("Session events:", getattr(session, 'events', 'N/A'))
    
    # Check for append_event
    if hasattr(service, 'append_event'):
        print("Found append_event method!")
        import inspect
        print("Signature:", inspect.signature(service.append_event))
    else:
        print("append_event method NOT found.")

if __name__ == "__main__":
    asyncio.run(main())
