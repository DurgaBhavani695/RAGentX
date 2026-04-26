import os
import sys
import shutil

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import engine
from app.database.models import Base
from scripts.init_db import init_db

def reset_system():
    print("Resetting system...")
    
    # 1. Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped.")
    
    # 2. Clear data/uploads
    upload_dir = "data/uploads"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
    print(f"Cleared {upload_dir}")
    
    # 3. Clear vectorstore
    vector_dir = "vectorstore"
    if os.path.exists(vector_dir):
        shutil.rmtree(vector_dir)
    os.makedirs(vector_dir, exist_ok=True)
    print(f"Cleared {vector_dir}")
    
    # 4. Re-initialize
    init_db()
    print("System reset complete.")

if __name__ == "__main__":
    reset_system()
