import sys
import os
import time
from typing import Dict, Any

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.entity_extraction.agent import EntityExtractionAgent
from src.agents.table_selection.agent import TableSelectionAgent
from src.agents.column_selection.agent import ColumnSelectionAgent
from src.agents.sql_generation.agent import SQLGenerationAgent
from src.agents.sql_execution.agent import SQLExecutionAgent
from src.agents.sql_execution.agent import SQLExecutionAgent
from src.agents.sql_regeneration.agent import SQLRegenerationAgent

# Memory Service
from src.memory.service import MemoryManager
from google.adk.sessions import Session
from google.genai.types import Content, Part
import uuid

# Define a local wrapper since SessionEvent/Event might not be exported in this ADK version
class SessionEvent:
    def __init__(self, content):
        self.content = content

# Inherit from CustomBaseAgent
from src.agents.base_agent import CustomBaseAgent

class Orchestrator(CustomBaseAgent):
    def __init__(self):
        super().__init__(agent_name="orchestrator")
        print("Initializing Orchestrator and Agents...")
        
        # Initialize Agents (Agents now handle their own FAISS connections)
        self.entity_agent = EntityExtractionAgent()
        self.table_agent = TableSelectionAgent()
        self.column_agent = ColumnSelectionAgent()
        self.sql_gen_agent = SQLGenerationAgent()
        self.sql_exec_agent = SQLExecutionAgent()
        self.sql_regen_agent = SQLRegenerationAgent()
        
        # Initialize Memory Manager
        self.memory_manager = MemoryManager()
        self.app_name = "iris_retail_app"
        self.user_id = "default_user" # Simplified for single user demo

        print("Agents and Memory Services initialized.")

    async def run(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Runs the full Text-to-SQL pipeline (Async).
        """
        start_time = time.time()
        logs = []
        
        # --- Memory Integration Start ---
        # 1. Manage Session
        if not session_id:
            session_id = str(uuid.uuid4())
            await self.memory_manager.create_session(self.app_name, self.user_id, session_id)
            current_session = None
        else:
            # Try to retrieve existing session
            current_session = await self.memory_manager.get_session(self.app_name, self.user_id, session_id)
            if not current_session:
                # Re-create if missing (e.g. server restart)
                await self.memory_manager.create_session(self.app_name, self.user_id, session_id)
                current_session = await self.memory_manager.get_session(self.app_name, self.user_id, session_id)

        # 2. Retrieve History
        history_context = ""
        print(f"DEBUG: Session Type: {type(current_session)}")
        
        # Check for history field (history, turns, messages, or events)
        turns = []
        # Documentation says 'events' is the standard history field
        for field in ['events', 'history', 'turns', 'messages']:
            if hasattr(current_session, field):
                attr = getattr(current_session, field)
                if isinstance(attr, list) and len(attr) > 0:
                    turns = attr
                    print(f"DEBUG: Using '{field}' field for history retrieval")
                    break
        
        if not turns:
             print("DEBUG: NO HISTORY DATA FOUND IN SESSION")

        if turns:
            # Simple history construction: Last 5 turns
            recent_turns = turns[-5:]
            history_text = []
            for turn in recent_turns:
                 try:
                     # If wrapped in SessionEvent, unwrap it
                     turn_data = turn
                     if hasattr(turn, 'content') and hasattr(turn.content, 'parts'):
                         turn_data = turn.content

                     role_val = getattr(turn_data, 'role', getattr(turn, 'role', 'user'))
                     role_label = "User" if role_val == "user" else "Assistant"
                     
                     text_content = ""
                     if hasattr(turn_data, 'parts') and turn_data.parts:
                         text_content = turn_data.parts[0].text
                     elif hasattr(turn_data, 'content'):
                         text_content = str(turn_data.content)
                     
                     if text_content:
                        history_text.append(f"{role_label}: {text_content}")
                 except Exception as e:
                     print(f"DEBUG: Error parsing history turn: {e}")
                     continue
            
            if history_text:
                history_context = "\n".join(history_text)
                print(f"  Retrieved History Context ({len(history_text)} messages).")

        # 3. Enrich Query for Entity Agent
        # We pass context + query so it can resolve coreferences (e.g. "it", "that", "Mumbai")
        if history_context:
            enriched_query_prompt = f"Previous Conversation:\n{history_context}\n\nCurrent Query: {user_query}"
        else:
            enriched_query_prompt = user_query
        # --- Memory Integration End ---

        print(f"\n--- Processing Query: {user_query} ---")
        logs.append(f"Query: {user_query}")
        
        # 1. Entity Extraction
        print("Step 1: Extracting Entities...")
        # Pass enriched prompt to agent
        extraction_result = self.entity_agent.execute(enriched_query_prompt)
        entities = extraction_result.get('entities', [])
        attributes = extraction_result.get('attributes', [])
        print(f"  Reasoning: {extraction_result.get('reason', 'N/A')}")
        
        # Fallback: if no entities found, use the whole query as a search term
        if not entities:
            print("  No entities found, using full query as search term.")
            entities = [user_query]
        
        print(f"  Entities: {entities}")
        print(f"  Attributes: {attributes}")
        
        # 2. Table Selection
        print("Step 2: Selecting Tables...")
        selected_tables = self.table_agent.execute(entities)
        
        if not selected_tables:
            return {"error": "No relevant tables found.", "logs": logs}
            
        print(f"  Selected Tables: {selected_tables}")
        
        # 3. Column Selection
        print("Step 3: Selecting Columns...")
        # Use attributes for column search. If no specific attributes, use entities + query words
        search_terms = attributes + entities
        schema_info = self.column_agent.execute(selected_tables, search_terms)
        
        if not schema_info:
             print("  No specific columns match high threshold. Providing table info context.")
             # Fallback
             pass
             
        print(f"  Schema Info: {list(schema_info.keys())}")
        
        # Mapping Table Helper
        # Maps Entity Names to SQLite Table Names (Manual Fix for now)
        TABLE_MAPPING = {
            "Amazon Sale Report": "amazon_sales",
            "International Sale Report": "international_sales",
            "May-2022": "may_2022",
            "P L March 2021": "p_l_march_2021",
            "Sale Report": "inventory", 
            "Cloud Warehouse Compariosn Chart": "product_master"
        }

        # 4. SQL Generation
        print("Step 4: Generating SQL...")
        
        # Create mapped schema info for SQL Gen
        mapped_schema_info = {}
        for original_table, columns in schema_info.items():
            # Use mapped name if available, else sanitize or keep original
            sql_table_name = TABLE_MAPPING.get(original_table, original_table.lower().replace(" ", "_"))
            mapped_schema_info[sql_table_name] = columns
            print(f"  Mapping '{original_table}' -> '{sql_table_name}'")
            
        sql_result = self.sql_gen_agent.execute(user_query, mapped_schema_info)
        sql_query = sql_result['sql_query']
        print(f"  Generated SQL: {sql_query}")
        print(f"  Reasoning: {sql_result.get('reason', 'N/A')}")
        logs.append(f"Generated SQL: {sql_query}")
        
        # 5. SQL Execution
        print("Step 5: Executing SQL...")
        execution_result = self.sql_exec_agent.execute(sql_query)
        
        # 6. Error Handling & Regeneration
        if isinstance(execution_result, str) and execution_result.startswith("Error"):
            print(f"  Success: False, Error: {execution_result}")
            print("Step 6: Attempting Regeneration...")
            logs.append(f"Execution Error: {execution_result}")
            
            new_sql_result = self.sql_regen_agent.execute(
                user_query=user_query,
                old_sql=sql_query,
                error_message=execution_result,
                schema_info=mapped_schema_info
            )
            new_sql_query = new_sql_result['sql_query']
            print(f"  Regenerated SQL: {new_sql_query}")
            print(f"  Reasoning: {new_sql_result.get('reason', 'N/A')}")
            logs.append(f"Regenerated SQL: {new_sql_query}")
            
            # Retry Execution
            execution_result = self.sql_exec_agent.execute(new_sql_query)
        
        end_time = time.time()
        
        # --- Memory Integration: Save Session ---
        # Add User Turn
        user_turn = Content(parts=[Part(text=user_query)], role="user")
        # Add Model Turn (Summary of what happened)
        model_text = f"Executed SQL: {sql_query}. Result: {str(execution_result)}"
        model_turn = Content(parts=[Part(text=model_text)], role="model")
        
        session = await self.memory_manager.get_session(self.app_name, self.user_id, session_id)
        if session:
            print("DEBUG: Appending events to session via service...")
            try:
                # Use the service's append_event logic for persistence
                await self.memory_manager.append_event(session, SessionEvent(content=user_turn))
                await self.memory_manager.append_event(session, SessionEvent(content=model_turn))
                print("  Session events appended and saved to Database.")
            except Exception as e:
                print(f"  WARNING: Failed to append events to session: {e}")
            
        return {
            "query": user_query,
            "sql": sql_query,
            "result": execution_result,
            "latency": end_time - start_time,
            "logs": logs,
            "sql_reasoning": sql_result.get('reason', 'N/A')
        }
    
if __name__ == "__main__":
    import asyncio
    orchestrator = Orchestrator()
    # Test Async Run
    res = asyncio.run(orchestrator.run("How many records are there in amazon sales report?"))
    print(res)
