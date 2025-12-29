from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService, Session
from google.adk.sessions.database_session_service import DatabaseSessionService
from typing import Optional, List
import os

class MemoryManager:
    """
    Encapsulates the ADK Memory and Session services.
    Defaults to DatabaseSessionService (SQLite) for persistence.
    """
    def __init__(self, use_memory_service: bool = False):
        # 1. Setup Database Session Service (Default)
        # Ensure directory exists
        db_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../session_database'))
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, 'iris_sessions.db')
        # DatabaseSessionService expects a URL string and handles engine creation.
        # It uses create_async_engine, so we need the sqlite+aiosqlite driver.
        db_url = f"sqlite+aiosqlite:///{db_path}"
        
        self._session_service = DatabaseSessionService(db_url=db_url)
        print(f"MemoryManager: Persisting sessions to {db_path} via async engine")

        # 2. Setup Memory Service (Optional/Auxiliary)
        self._memory_service = InMemoryMemoryService()

    @property
    def session_service(self) -> DatabaseSessionService:
        return self._session_service

    @property
    def memory_service(self) -> InMemoryMemoryService:
        return self._memory_service

    async def create_session(self, app_name: str, user_id: str, session_id: str) -> Session:
        """Helper to create a session."""
        return await self._session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

    async def get_session(self, app_name: str, user_id: str, session_id: str) -> Optional[Session]:
        """Helper to retrieve a session."""
        return await self._session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

    async def list_sessions(self, app_name: str, user_id: str) -> List[Session]:
        """Lists all sessions for a user."""
        try:
            return await self._session_service.list_sessions(
                app_name=app_name,
                user_id=user_id
            )
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    async def save_session_to_memory(self, session: Session):
        """Persists the session to long-term memory (Auxiliary)."""
        await self._memory_service.add_session_to_memory(session)

    async def append_event(self, session: Session, event):
        """Appends an event to the session and persists to database."""
        if hasattr(self._session_service, 'append_event'):
            await self._session_service.append_event(session, event)
        else:
            # Fallback for older versions or unexpected API
            print(f"WARNING: append_event not found on session service {type(self._session_service)}")
            # If append_event is missing, manual update might be needed if update_session exists
            if hasattr(self._session_service, 'update_session'):
                await self._session_service.update_session(session)
