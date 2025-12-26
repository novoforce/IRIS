try:
    from google.adk import agents
    print("google.adk.agents contents:")
    for item in dir(agents):
        if not item.startswith("_"):
            print(f"- {item}")
            
    # Check for specific multi-agent classes
    if hasattr(agents, 'SequentialAgent'):
        print("\nSequentialAgent found.")
    if hasattr(agents, 'RouterAgent'):
        print("RouterAgent found.")
    if hasattr(agents, 'ParallelAgent'):
        print("ParallelAgent found.")

except ImportError:
    print("Could not import google.adk.agents")
