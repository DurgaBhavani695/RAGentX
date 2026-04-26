import os
import sys
import shutil
import pytest
import subprocess
from sqlalchemy import create_engine, inspect

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings

def test_reset_system_script():
    # Setup test environment
    TEST_DB_URL = "sqlite:///./test_reset.db"
    settings.DATABASE_URL = TEST_DB_URL
    
    # Create dummy files and directories
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("vectorstore", exist_ok=True)
    
    with open("data/uploads/test.txt", "w") as f:
        f.write("test")
    with open("vectorstore/test.index", "w") as f:
        f.write("test")
        
    # Run reset script with environment variable
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_DB_URL
    result = subprocess.run([sys.executable, "scripts/reset_system.py"], capture_output=True, text=True, env=env)
    
    assert result.returncode == 0
    
    # Verify directories are empty but exist
    assert os.path.exists("data/uploads")
    assert len(os.listdir("data/uploads")) == 0
    
    assert os.path.exists("vectorstore")
    assert len(os.listdir("vectorstore")) == 0
    
    # Verify DB is re-initialized
    engine = create_engine(TEST_DB_URL)
    inspector = inspect(engine)
    assert "app_config" in inspector.get_table_names()
    engine.dispose()
    
    # Cleanup
    if os.path.exists("./test_reset.db"):
        os.remove("./test_reset.db")
    
    # We leave data/uploads and vectorstore as they are expected to exist in the real app, 
    # but maybe we should clean them up in the test too.
    if os.path.exists("data/uploads"):
        shutil.rmtree("data/uploads")
    if os.path.exists("vectorstore"):
        # Be careful here, the root vectorstore might have real data.
        # But this is a test environment.
        pass
