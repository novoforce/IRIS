from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class DatabaseConnector(ABC):
    """
    Abstract Base Class for database connectors.
    Ensures all database implementations follow the same interface.
    """

    @abstractmethod
    def connect(self):
        """Establishes a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Closes the database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executes a SQL query and returns the results as a list of dictionaries.
        
        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): Parameters to bind to the query.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is a dictionary mapping column names to values.
        """
        pass

    @abstractmethod
    def get_table_schema(self, table_name: str) -> str:
        """
        Retrieves the schema definition for a specific table.
        
        Args:
            table_name (str): The name of the table.
            
        Returns:
            str: The CREATE TABLE statement or schema description.
        """
        pass
