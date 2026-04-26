import os
import subprocess
import sys
import shutil

def run_command(command, description):
    print(f"📦 {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        sys.exit(1)

def main():
    print("🤖 RAGentX: Agentic RAG System - Cross-Platform Setup")
    print("-------------------------------------------------------")

    # 1. Check for uv
    if not shutil.which("uv"):
        print("❌ 'uv' is not installed. Please install it from https://github.com/astral-sh/uv")
        sys.exit(1)

    # 2. Sync dependencies
    run_command("uv sync", "Syncing dependencies with uv")

    # 3. Setup .env
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("📝 Creating .env from .env.example...")
            shutil.copy(".env.example", ".env")
        else:
            print("📝 Creating .env from template...")
            with open(".env", "w") as f:
                f.write("GROQ_API_KEY=your_groq_key_here\n")
                f.write("GROQ_MODEL_NAME=llama-3.3-70b-versatile\n")
                f.write("DATABASE_URL=sqlite:///./ragentx.db\n")
                f.write("FAISS_INDEX_PATH=vectorstore/faiss_index\n")
                f.write("EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2\n")
        
        print("\n⚠️  IMPORTANT: Please open '.env' and add your GROQ_API_KEY.")
    else:
        print("✅ .env file already exists.")

    # 4. Create directories
    if not os.path.exists("vectorstore"):
        print("📂 Creating 'vectorstore' directory...")
        os.makedirs("vectorstore")
    
    if not os.path.exists("sample_data"):
        print("📂 Creating 'sample_data' directory...")
        os.makedirs("sample_data")

    print("\n✨ Initialization complete!")
    print("\n🚀 To start the system:")
    print("   Launch Orchestrator: uv run python init_and_run.py")
    print("   (Or run backend and frontend separately as shown in README.md)")

if __name__ == "__main__":
    main()
