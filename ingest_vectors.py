import os
import glob
import re
from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.faiss_store import FaissStore

# Configuration
PROCESSED_DATA_DIR = 'Sales Dataset/Processed_data'
TABLE_COLLECTION_NAME = 'table_descriptions'

def sanitize_collection_name(name: str) -> str:
    """Sanitizes string to be a valid collection name (safe for filenames)."""
    return re.sub(r'[^a-zA-Z0-9]', '_', name).lower()

def ingest_all_data():
    print(f"--- Starting Full Ingestion (FAISS) ---")
    
    # Initialize Services
    embedding_service = GeminiEmbedding()
    
    # Table Description Store
    # We use one index for all table descriptions
    table_store = FaissStore(
        index_name=TABLE_COLLECTION_NAME, 
        embedding_function=embedding_service,
        folder_path="faiss_db" 
    )
    
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
                
            # Add to table_store
            doc = {
                'content': content,
                'metadata': {
                    "type": "table",
                    "table_name": table_name,
                    "source": table_desc_file
                }
            }
            print(f"Ingesting table description for {table_name}...")
            table_store.add_documents([doc])
        else:
            print(f"Warning: Table description file not found: {table_desc_file}")

        # 2. Process Column Descriptions
        # Create/Load specific FAISS index for this table's columns
        safe_table_name = sanitize_collection_name(table_name)
        column_index_name = f"columns_{safe_table_name}"
        
        column_store = FaissStore(
            index_name=column_index_name,
            embedding_function=embedding_service,
            folder_path="faiss_db"
        )
        
        # Get all _desc.txt files except the table description
        all_files = glob.glob(os.path.join(table_dir, "*_desc.txt"))
        column_files = [f for f in all_files if os.path.basename(f) != f"{table_name}_desc.txt"]
        
        if not column_files:
            print(f"No column description files found for {table_name}.")
            continue
            
        print(f"Found {len(column_files)} columns.")
        
        column_docs = []
        for file_path in column_files:
            filename = os.path.basename(file_path)
            column_name = filename.replace('_desc.txt', '')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            column_docs.append({
                'content': content,
                'metadata': {
                    "type": "column",
                    "table_name": table_name,
                    "column_name": column_name,
                    "source": file_path
                }
            })
            
        # Batch add columns
        if column_docs:
            print(f"Ingesting {len(column_docs)} columns into '{column_index_name}'...")
            column_store.add_documents(column_docs)
            print(f"Completed columns for {table_name}")

    print("\n--- Ingestion Complete ---")

if __name__ == "__main__":
    ingest_all_data()
