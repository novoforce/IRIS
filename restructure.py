import os
import shutil
import glob

def restructure():
    # Define directories
    ANALYSIS_DIR = 'Data Analysis'
    DB_DIR = 'Database'
    
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    
    print(f"Created directories: {ANALYSIS_DIR}, {DB_DIR}")
    
    # Move Notebooks
    notebooks = glob.glob("*.ipynb")
    for nb in notebooks:
        try:
            shutil.move(nb, os.path.join(ANALYSIS_DIR, nb))
            print(f"Moved {nb} to {ANALYSIS_DIR}")
        except Exception as e:
            print(f"Error moving {nb}: {e}")
            
    # Move Database Files
    db_files = ['iris.db', 'schema.sql']
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                shutil.move(db_file, os.path.join(DB_DIR, db_file))
                print(f"Moved {db_file} to {DB_DIR}")
            except Exception as e:
                print(f"Error moving {db_file}: {e}")
        else:
            print(f"File not found: {db_file}")

if __name__ == "__main__":
    restructure()
