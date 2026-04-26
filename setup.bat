@echo off
setlocal

echo 🤖 Initializing RAGentX: Agentic RAG System Setup...

:: 1. Check for uv
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ uv is not installed. Please install it from https://github.com/astral-sh/uv
    exit /b 1
)

:: 2. Initialize project and sync dependencies
echo 📦 Syncing dependencies with uv...
uv sync

:: 3. Setup .env if it doesn't exist
if not exist .env (
    echo 📝 Creating .env from template...
    echo GROQ_API_KEY=your_groq_key_here > .env
    echo GROQ_API_BASE=https://api.groq.com/openai/v1 >> .env
    echo DATABASE_URL=sqlite:///./ragentx.db >> .env
    echo FAISS_INDEX_PATH=vectorstore/faiss_index >> .env
    echo.
    echo ⚠️  Please open .env and add your GROQ_API_KEY.
) else (
    echo ✅ .env file already exists.
)

:: 4. Create directories
if not exist vectorstore (
    echo 📂 Creating vectorstore directory...
    mkdir vectorstore
)

echo.
echo ✨ Initialization complete!
echo.
echo 🚀 To start the system:
echo    1. Start Backend: uv run python -m uvicorn app.main:app --reload
echo    2. Start Frontend: uv run streamlit run frontend/app.py
echo.

pause
