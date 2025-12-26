try:
    from google.adk.agents import SequentialAgent, InvocationContext, LlmAgent
    import inspect
    
    print("--- SequentialAgent ---")
    print(f"Init: {inspect.signature(SequentialAgent.__init__)}")
    # Check if run exists and signature
    if hasattr(SequentialAgent, 'run'):
        print(f"Run: {inspect.signature(SequentialAgent.run)}")
        
    print("\n--- InvocationContext ---")
    print(f"Init: {inspect.signature(InvocationContext.__init__)}")
    
except Exception as e:
    print(f"Error: {e}")
