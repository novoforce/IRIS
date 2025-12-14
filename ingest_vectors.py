import os
import glob
import uuid
import re
from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.qdrant_store import QdrantStore
from qdrant_client import QdrantClient

# Configuration
PROCESSED_DATA_DIR = 'Sales Dataset/Processed_data'
TABLE_COLLECTION = 'table_descriptions'

def get_deterministic_uuid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))

def sanitize_collection_name(name: str) -> str:
    """Sanitizes string to be a valid Qdrant collection name."""
    # Replace non-alphanumeric characters with underscores and lowercase
    return re.sub(r'[^a-zA-Z0-9]', '_', name).lower()

def ingest_all_data():
    print(f"--- Starting Full Ingestion ---")
    
    # Initialize Services
    embedding_service = GeminiEmbedding()
    
    # Shared Client
    db_path = os.path.abspath("qdrant_db")
    shared_client = QdrantClient(path=db_path)
    
    # Table Description Store (Shared for all tables)
    table_store = QdrantStore(collection_name=TABLE_COLLECTION, client=shared_client)
    
    # Iterate through all subdirectories in Processed_data
    if not os.path.exists(PROCESSED_DATA_DIR):
        print(f"Directory not found: {PROCESSED_DATA_DIR}")
        return

    subdirs = [d for d in os.listdir(PROCESSED_DATA_DIR) if os.path.isdir(os.path.join(PROCESSED_DATA_DIR, d))]
    
    print(f"Found {len(subdirs)} tables to process: {subdirs}")
    
    for table_name in subdirs:
        print(f"\n--- Processing Table: {table_name} ---")
        table_dir = os.path.join(PROCESSED_DATA_DIR, table_name)
        
        # 1. Process Table Description
        table_desc_file = os.path.join(table_dir, f"{table_name}_desc.txt")
        
        if os.path.exists(table_desc_file):
            with open(table_desc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Generate Embedding
            print(f"Generating embedding for table description...")
            embedding = embedding_service.generate_embedding(content)
            
            # Upsert to 'table_descriptions' collection
            metadata = {
                "type": "table",
                "table_name": table_name,
                "content": content,
                "source": table_desc_file
            }
            
            table_id = get_deterministic_uuid(f"{table_name}_desc")
            table_store.upsert_vectors(
                vectors=[embedding],
                metadata=[metadata],
                ids=[table_id]
            )
            print(f"Table description ingested into '{TABLE_COLLECTION}'.")
        else:
            print(f"Warning: Table description file not found: {table_desc_file}")

        # 2. Process Column Descriptions
        # Create a specific collection for this table's columns
        # e.g., columns_amazon_sale_report
        safe_table_name = sanitize_collection_name(table_name)
        column_collection_name = f"columns_{safe_table_name}"
        column_store = QdrantStore(collection_name=column_collection_name, client=shared_client)
        
        # Get all _desc.txt files except the table description
        all_files = glob.glob(os.path.join(table_dir, "*_desc.txt"))
        column_files = [f for f in all_files if os.path.basename(f) != f"{table_name}_desc.txt"]
        
        if not column_files:
            print(f"No column description files found for {table_name}.")
            continue
            
        print(f"Found {len(column_files)} columns.")
        
        column_texts = []
        column_metadatas = []
        column_ids = []
        
        for file_path in column_files:
            filename = os.path.basename(file_path)
            column_name = filename.replace('_desc.txt', '')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            column_texts.append(content)
            column_metadatas.append({
                "type": "column",
                "table_name": table_name,
                "column_name": column_name,
                "content": content,
                "source": file_path
            })
            column_ids.append(get_deterministic_uuid(f"{table_name}_{column_name}"))

        # Batch Generate Embeddings
        print(f"Generating embeddings for columns...")
        try:
            embeddings = embedding_service.generate_embeddings(column_texts)
            
            if len(embeddings) != len(column_texts):
                print(f"Error: Mismatch in embeddings count. Expected {len(column_texts)}, got {len(embeddings)}")
                continue

            # Upsert to specific column collection
            print(f"Upserting to collection: {column_collection_name}")
            column_store.upsert_vectors(
                vectors=embeddings,
                metadata=column_metadatas,
                ids=column_ids
            )
            print(f"Successfully ingested columns for {table_name}.")
            
        except Exception as e:
            print(f"Error processing columns for {table_name}: {e}")

if __name__ == "__main__":
    ingest_all_data()
