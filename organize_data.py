import os
import shutil
import glob

DATA_DIR = 'Sales Dataset'
RAW_DIR = os.path.join(DATA_DIR, 'Raw_data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'Processed_data')

def organize():
    # Create directories
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    print(f"Created directories:\n- {RAW_DIR}\n- {PROCESSED_DIR}")
    
    # 1. Move CSVs to Raw_data
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(RAW_DIR, filename)
        try:
            shutil.move(file_path, dest_path)
            print(f"Moved to Raw: {filename}")
        except Exception as e:
            print(f"Error moving {filename}: {e}")
            
    # 2. Move Folders to Processed_data
    # List all items in DATA_DIR
    all_items = os.listdir(DATA_DIR)
    for item in all_items:
        item_path = os.path.join(DATA_DIR, item)
        
        # Skip the new directories themselves
        if item in ['Raw_data', 'Processed_data']:
            continue
            
        # If it's a directory, it's likely a documentation folder
        if os.path.isdir(item_path):
            dest_path = os.path.join(PROCESSED_DIR, item)
            try:
                shutil.move(item_path, dest_path)
                print(f"Moved to Processed: {item}")
            except Exception as e:
                print(f"Error moving folder {item}: {e}")

if __name__ == "__main__":
    organize()
