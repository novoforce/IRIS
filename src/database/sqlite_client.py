import sqlite3
import os
from typing import List, Dict, Any, Optional
from .base import DatabaseConnector

class SQLiteClient(DatabaseConnector):
    """
    SQLite implementation of the DatabaseConnector.
    """

    def __init__(self, db_path: str):
        """
        Initialize the SQLite client.
        
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establishes a connection to the SQLite database."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found at: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        # Enable row factory to get dictionary-like access if needed, 
        # but we will manually construct dicts for consistency across DBs.
        self.conn.row_factory = sqlite3.Row

    def disconnect(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executes a SQL query and returns the results as a list of dictionaries.
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                # Convert sqlite3.Row objects to standard dictionaries
                return [dict(row) for row in rows]
            else:
                self.conn.commit()
                return []
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            raise e
        finally:
            cursor.close()

    def get_table_schema(self, table_name: str) -> str:
        """
        Retrieves the CREATE TABLE statement for a specific table.
        """
        if not self.conn:
            self.connect()
            
        query = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        results = self.execute_query(query)
        
        if results:
            return results[0]['sql']
        return ""
