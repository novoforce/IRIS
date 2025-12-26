import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# CustomLlmAgent
from src.agents.base_agent import CustomLlmAgent

class SQLGenerationAgent(CustomLlmAgent):
    def __init__(self):
        super().__init__(agent_name="sql_generation")

    def execute(self, user_query: str, schema_info: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generates SQL query based on schema and query.
        """
        schema_context = ""
        for table, columns in schema_info.items():
            col_list = ", ".join([col['name'] for col in columns])
            schema_context += f"Table: {table}\nColumns: {col_list}\n\n"
            for col in columns:
                schema_context += f"  - {col['name']}: {col.get('description', '')[:50]}...\n"
                
        prompt = self.config['prompt_template'].format(
            user_query=user_query,
            schema_context=schema_context
        )
        
        response = self.get_llm_response(prompt, temperature=0.0)
        
        sql = response.replace('```sql', '').replace('```', '').strip()
        return sql
