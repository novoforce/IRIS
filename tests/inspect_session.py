import asyncio
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.memory.service import MemoryManager

async def inspect():
    mm = MemoryManager()
    session_id = "test-inspect-id"
    app_name = "iris_retail_app"
    user_id = "default_user"
    
    # Create
    print("Creating session...")
    await mm.create_session(app_name, user_id, session_id)
    
    # Get
    print("Retrieving session...")
    session = await mm.get_session(app_name, user_id, session_id)
    
    print(f"\nSession Type: {type(session)}")
    print(f"Session Fields: {session.model_fields.keys() if hasattr(session, 'model_fields') else 'N/A'}")
    
    try:
        print(f"Session Dump: {session.model_dump()}")
    except Exception as e:
        print(f"Dump failed: {e}")
        try:
            print(f"Dict: {session.dict()}")
        except:
            print("Dict also failed")

if __name__ == "__main__":
    asyncio.run(inspect())
