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
from src.agents.sql_regeneration.agent import SQLRegenerationAgent

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
        
        print("Agents initialized.")

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Runs the full Text-to-SQL pipeline.
        """
        start_time = time.time()
        logs = []
        
        print(f"\n--- Processing Query: {user_query} ---")
        logs.append(f"Query: {user_query}")
        
        # 1. Entity Extraction
        print("Step 1: Extracting Entities...")
        extraction_result = self.entity_agent.execute(user_query)
        entities = extraction_result.get('entities', [])
        attributes = extraction_result.get('attributes', [])
        
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
            
        sql_query = self.sql_gen_agent.execute(user_query, mapped_schema_info)
        print(f"  Generated SQL: {sql_query}")
        logs.append(f"Generated SQL: {sql_query}")
        
        # 5. SQL Execution
        print("Step 5: Executing SQL...")
        execution_result = self.sql_exec_agent.execute(sql_query)
        
        # 6. Error Handling & Regeneration
        if isinstance(execution_result, str) and execution_result.startswith("Error"):
            print(f"  Success: False, Error: {execution_result}")
            print("Step 6: Attempting Regeneration...")
            logs.append(f"Execution Error: {execution_result}")
            
            new_sql_query = self.sql_regen_agent.execute(
                user_query=user_query,
                old_sql=sql_query,
                error_message=execution_result,
                schema_info=mapped_schema_info
            )
            print(f"  Regenerated SQL: {new_sql_query}")
            logs.append(f"Regenerated SQL: {new_sql_query}")
            
            # Retry Execution
            execution_result = self.sql_exec_agent.execute(new_sql_query)
        
        end_time = time.time()
        
        return {
            "query": user_query,
            "sql": sql_query,
            "result": execution_result,
            "latency": end_time - start_time,
            "logs": logs
        }
    
if __name__ == "__main__":
    orchestrator = Orchestrator()
    res = orchestrator.run("How many records are there in amazon sales report?")
    print(res)
