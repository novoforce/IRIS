import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.base_agent import BaseAgent

class SQLRegenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="sql_regeneration")

    def execute(self, user_query: str, old_sql: str, error_message: str, schema_info: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Regenerates SQL query based on error.
        
        Args:
            user_query (str): The original user question.
            old_sql (str): The failed SQL query.
            error_message (str): The execution error.
            schema_info (Dict): Schema context.
            
        Returns:
            str: The corrected SQL query.
        """
        # Format schema context
        schema_context = ""
        for table, columns in schema_info.items():
            col_list = ", ".join([col['name'] for col in columns])
            schema_context += f"Table: {table}\nColumns: {col_list}\n\n"
                
        prompt = self.config['prompt_template'].format(
            user_query=user_query,
            old_sql=old_sql,
            error_message=error_message,
            schema_context=schema_context
        )
        
        response = self.get_llm_response(prompt, temperature=0.0)
        
        # Clean response
        sql = response.replace('```sql', '').replace('```', '').strip()
        return sql
