import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import engine, SessionLocal
from app.database.models import Base, AppConfig

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if config already exists
        if not db.query(AppConfig).filter(AppConfig.key == "max_file_size_mb").first():
            default_configs = [
                AppConfig(key="max_file_size_mb", value=5),
                AppConfig(key="max_files_per_upload", value=5),
                AppConfig(key="max_total_files", value=10)
            ]
            db.add_all(default_configs)
            db.commit()
            print("Default configurations seeded.")
        else:
            print("Database already initialized.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
