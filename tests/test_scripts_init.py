import os
import sys
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.models import Base, AppConfig
from app.core.config import settings

def test_init_db_script():
    # Use a test database
    TEST_DB_URL = "sqlite:///./test_init.db"
    settings.DATABASE_URL = TEST_DB_URL
    
    # Ensure DB is clean
    if os.path.exists("./test_init.db"):
        os.remove("./test_init.db")
        
    # Run the script via subprocess with environment variable
    import subprocess
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_DB_URL
    result = subprocess.run([sys.executable, "scripts/init_db.py"], capture_output=True, text=True, env=env)
    
    assert result.returncode == 0
    
    # Verify DB state
    engine = create_engine(TEST_DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    assert "app_config" in tables
    assert "chat_history" in tables
    assert "doc_metadata" in tables
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    configs = {c.key: c.value for c in session.query(AppConfig).all()}
    assert configs["max_file_size_mb"] == 5
    assert configs["max_files_per_upload"] == 5
    assert configs["max_total_files"] == 10
    
    session.close()
    engine.dispose()
    
    # Cleanup
    if os.path.exists("./test_init.db"):
        os.remove("./test_init.db")
