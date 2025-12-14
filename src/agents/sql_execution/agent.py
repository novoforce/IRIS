import sys
import os
from typing import List, Dict, Any, Union

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.base_agent import BaseAgent
from src.database.sqlite_client import SQLiteClient

class SQLExecutionAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="sql_execution")
        # Initialize DB Client
        db_path = os.path.join(os.path.dirname(__file__), '../../../', self.config.get('db_path', 'Database/iris.db'))
        self.db_client = SQLiteClient(db_path=os.path.abspath(db_path))
        self.db_client.connect()

    def execute(self, sql_query: str) -> Union[List[Dict[str, Any]], str]:
        """
        Executes the SQL query.
        
        Args:
            sql_query (str): The SQL query to execute.
            
        Returns:
            Union[List[Dict], str]: Query results or error message.
        """
        print(f"SQLExecution: Executing query: {sql_query}")
        try:
            results = self.db_client.execute_query(sql_query)
            return results
        except Exception as e:
            return f"Error: {str(e)}"
