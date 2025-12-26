try:
    from google.adk.agents import BaseAgent
    import inspect
    
    print("BaseAgent methods:")
    for name, method in inspect.getmembers(BaseAgent, predicate=inspect.isfunction):
        print(f"- {name}: {inspect.signature(method)}")
        
    print("\nBaseAgent doc:")
    print(BaseAgent.__doc__)
    
except ImportError:
    print("Could not import google.adk.agents.BaseAgent")
