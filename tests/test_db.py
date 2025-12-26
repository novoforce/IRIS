import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.sqlite_client import SQLiteClient

def test_connection():
    db_path = 'Database/iris.db'
    client = SQLiteClient(db_path)
    
    print(f"Connecting to {db_path}...")
    client.connect()
    
    print("Running query: SELECT count(*) FROM amazon_sales")
    results = client.execute_query("SELECT count(*) as count FROM amazon_sales")
    print(f"Result: {results}")
    
    print("Running query: SELECT * FROM amazon_sales LIMIT 1")
    results = client.execute_query("SELECT * FROM amazon_sales LIMIT 1")
    print(f"Result: {results}")

    print("Getting schema for 'amazon_sales'...")
    schema = client.get_table_schema('amazon_sales')
    print(f"Schema: {schema[:50]}...") # Print first 50 chars

    client.disconnect()
    print("Test passed!")

if __name__ == "__main__":
    test_connection()
