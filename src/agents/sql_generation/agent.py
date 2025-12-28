import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# CustomLlmAgent
from src.agents.base_agent import CustomLlmAgent

from pydantic import BaseModel

class SQLGenerationOutput(BaseModel):
    sql_query: str
    reason: str

class SQLGenerationAgent(CustomLlmAgent):
    def __init__(self):
        super().__init__(agent_name="sql_generation")

    def execute(self, user_query: str, schema_info: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
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
        
        # Use structured output
        response_data = self.get_llm_response(prompt, temperature=0.0, response_schema=SQLGenerationOutput)
        
        if isinstance(response_data, dict):
            # Clean SQL just in case, though schema should enforce string
            response_data['sql_query'] = response_data['sql_query'].replace('```sql', '').replace('```', '').strip()
            return response_data
            
        # Fallback
        try:
             import json
             data = json.loads(response_data)
             data['sql_query'] = data['sql_query'].replace('```sql', '').replace('```', '').strip()
             return data
        except:
             print(f"Error parsing SQLGeneration output: {response_data}")
             # Return valid structure with error
             return {"sql_query": "", "reason": "Error parsing output"}
