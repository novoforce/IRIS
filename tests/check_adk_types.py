import google.adk.sessions as sessions
import google.genai.types as types

print("Sessions dir:", dir(sessions))
try:
    from google.adk.sessions import SessionEvent
    print("SessionEvent found")
    print("SessionEvent fields:", SessionEvent.model_fields.keys() if hasattr(SessionEvent, 'model_fields') else 'N/A')
except ImportError:
    print("SessionEvent NOT found")
except Exception as e:
    print(f"Error: {e}")
