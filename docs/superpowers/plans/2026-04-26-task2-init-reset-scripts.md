# Task 2: System Initialization and Reset Scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create system initialization and reset scripts with TDD verification.

**Architecture:** Two standalone Python scripts in `scripts/` directory that interact with the SQLAlchemy models and file system. `scripts/init_db.py` handles table creation and default config seeding. `scripts/reset_system.py` handles database teardown/setup and directory cleanup.

**Tech Stack:** Python, SQLAlchemy, `shutil`, `os`.

---

### Task 2.1: Initialization Script

**Files:**
- Create: `scripts/init_db.py`
- Test: `tests/test_scripts_init.py`

- [ ] **Step 1: Write the failing test**

```python
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
        
    # Run the script via subprocess
    import subprocess
    result = subprocess.run([sys.executable, "scripts/init_db.py"], capture_output=True, text=True)
    
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
    
    # Cleanup
    if os.path.exists("./test_init.db"):
        os.remove("./test_init.db")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scripts_init.py -v`
Expected: FAIL (script not found)

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scripts_init.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/init_db.py tests/test_scripts_init.py
git commit -m "feat: add init_db script"
```

---

### Task 2.2: Reset Script

**Files:**
- Create: `scripts/reset_system.py`
- Test: `tests/test_scripts_reset.py`

- [ ] **Step 1: Write the failing test**

```python
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
        
    # Run reset script
    result = subprocess.run([sys.executable, "scripts/reset_system.py"], capture_output=True, text=True)
    
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
    
    # Cleanup
    if os.path.exists("./test_reset.db"):
        os.remove("./test_reset.db")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scripts_reset.py -v`
Expected: FAIL (script not found)

- [ ] **Step 3: Write minimal implementation**

```python
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
        # We don't want to delete the directory if it's where the script is running from or something,
        # but shutil.rmtree is fine here.
        shutil.rmtree(vector_dir)
    os.makedirs(vector_dir, exist_ok=True)
    print(f"Cleared {vector_dir}")
    
    # 4. Re-initialize
    init_db()
    print("System reset complete.")

if __name__ == "__main__":
    reset_system()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scripts_reset.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/reset_system.py tests/test_scripts_reset.py
git commit -m "feat: add reset_system script"
```
