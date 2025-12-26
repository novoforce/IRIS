try:
    from google.adk.agents import LlmAgent, SequentialAgent
    import inspect
    
    print("--- LlmAgent ---")
    print(f"Init: {inspect.signature(LlmAgent.__init__)}")
    # print(f"Run: {inspect.signature(LlmAgent.run)}") # Might be inherited

    print("\n--- SequentialAgent ---")
    print(f"Init: {inspect.signature(SequentialAgent.__init__)}")
    
except ImportError:
    print("Could not import agents")
except Exception as e:
    print(f"Error: {e}")
