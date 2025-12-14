import sys
import os
import traceback

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import Orchestrator

def test_flow():
    print("--- Testing Agent Workflow ---")
    try:
        orchestrator = Orchestrator()
        
        # Test 1
        query = "How many records are there in the amazon sales report?"
        print(f"\nQuery: {query}")
        result = orchestrator.run(query)
        print("SQL:", result['sql'])
        print("Result:", result['result'])
        
        # Test 2
        query2 = "Show me columns in Sale Report"
        # This is strictly not an SQL question but tests entity/table selection
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_flow()
