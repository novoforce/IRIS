from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService, Session
from typing import Optional

class MemoryManager:
    """
    Encapsulates the ADK Memory and Session services.
    Currently uses InMemory implementations, but can be swapped for others.
    """
    def __init__(self):
        self._session_service = InMemorySessionService()
        self._memory_service = InMemoryMemoryService()

    @property
    def session_service(self) -> InMemorySessionService:
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

    async def save_session_to_memory(self, session: Session):
        """Persists the session to long-term memory."""
        await self._memory_service.add_session_to_memory(session)
