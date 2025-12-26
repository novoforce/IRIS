import sys
import os
import time
import traceback

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.orchestrator import Orchestrator

def verify_system():
    print("="*50)
    print("VERIFYING GOOGLE ADK REFRACTOR")
    print("="*50)
    
    orchestrator = None
    try:
        print("\n[1] Initializing Orchestrator (ADK Agent)...")
        orchestrator = Orchestrator()
        print("    Success: Orchestrator initialized.")
        print(f"    Type: {type(orchestrator)}")
        print(f"    ADK Name: {orchestrator.name}")
        
    except Exception as e:
        print(f"    FAILED: {e}")
        traceback.print_exc()
        return

    test_queries = [
        "How many records are there in the amazon sales report?",
        "What is the total amount for orders shipped to Mumbai?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[2.{i}] Running Query: '{query}'")
        try:
            result = orchestrator.run(query)
            
            if result.get('sql'):
                print(f"    Success: SQL Generated.")
                print(f"    SQL: {result['sql']}")
            else:
                print(f"    Warning: No SQL generated.")
                
            if result.get('result') and not str(result['result']).startswith("Error"):
                print(f"    Success: Execution Result: {result['result']}")
            else:
                print(f"    Failed: Execution Error: {result.get('result')}")
                
        except Exception as e:
            print(f"    CRITICAL FAILURE: {e}")
            traceback.print_exc()

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    verify_system()
