import subprocess
import time
import sys
import os
import shutil

def run_command(command, name):
    print(f"🚀 Starting {name}...")
    # Use the appropriate command based on whether we are on Windows or not
    return subprocess.Popen(command, shell=True)

def check_setup():
    """Checks if the project is initialized."""
    if not os.path.exists(".env"):
        print("⚠️  '.env' file not found. Running setup first...")
        subprocess.run([sys.executable, "setup.py"], check=True)
    
    if not os.path.exists("vectorstore"):
        os.makedirs("vectorstore")

def main():
    print("🤖 RAGentX: Agentic RAG System - Orchestrator")
    print("---------------------------------------------")

    try:
        # 1. Ensure setup is done
        check_setup()

        # 2. Sync dependencies
        print("📦 Ensuring dependencies are synced...")
        subprocess.run("uv sync", shell=True, check=True)

        # 3. Define commands
        backend_cmd = "uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
        frontend_cmd = "uv run streamlit run frontend/app.py"

        # 4. Start processes
        backend_proc = run_command(backend_cmd, "Backend (FastAPI)")
        time.sleep(3)  # Give backend a moment to start
        
        frontend_proc = run_command(frontend_cmd, "Frontend (Streamlit)")

        print("\n✨ System is up and running!")
        print("👉 Backend API:  http://127.0.0.1:8000")
        print("👉 Frontend UI:  http://localhost:8501")
        print("\nPress Ctrl+C to stop all services.")

        while True:
            time.sleep(1)
            # Monitor processes
            if backend_proc.poll() is not None:
                print("❌ Backend process stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("❌ Frontend process stopped unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        # Graceful shutdown
        try:
            if sys.platform == 'win32':
                # Use taskkill for full process tree cleanup on Windows
                subprocess.run(f"taskkill /F /T /PID {backend_proc.pid}", shell=True, capture_output=True)
                subprocess.run(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True, capture_output=True)
            else:
                backend_proc.terminate()
                frontend_proc.terminate()
        except NameError:
            # Processes might not have been defined yet
            pass
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    main()
