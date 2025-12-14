import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.embeddings.gemini import GeminiEmbedding

def test_gemini_embedding():
    print("Testing Gemini Embedding Service...")
    
    try:
        # Initialize service
        service = GeminiEmbedding()
        print("Service initialized.")
        
        # Test single embedding
        text = "This is a test sentence for IRIS chatbot."
        print(f"Generating embedding for: '{text}'")
        embedding = service.generate_embedding(text)
        
        if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], float):
            print(f"Success! Generated embedding of length: {len(embedding)}")
        else:
            print("Failed: Output format incorrect.")
            
        # Test batch embedding (manual iteration in class)
        texts = ["Item 1", "Item 2"]
        print(f"Generating embeddings for list: {texts}")
        embeddings = service.generate_embeddings(texts)
        
        if len(embeddings) == 2 and len(embeddings[0]) > 0:
            print("Success! Generated batch embeddings.")
        else:
            print("Failed: Batch output incorrect.")
            
    except Exception as e:
        print(f"Error during test: {e}")
        print("Please ensure GEMINI_API_KEY is set correctly in secrets/.env")

if __name__ == "__main__":
    test_gemini_embedding()
