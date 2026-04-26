import subprocess
import time
import sys
import os
import signal

def run_command(command, name):
    print(f"🚀 Starting {name}...")
    return subprocess.Popen(command, shell=True)

def main():
    print("🤖 RAGentX: Agentic RAG System - Orchestrator")
    print("---------------------------------------------")

    # 1. Sync dependencies
    print("📦 Ensuring dependencies are synced...")
    subprocess.run("uv sync", shell=True)

    # 2. Define commands
    backend_cmd = "uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
    frontend_cmd = "uv run streamlit run frontend/app.py"

    # 3. Start processes
    backend_proc = run_command(backend_cmd, "Backend (FastAPI)")
    time.sleep(2)  # Give backend a moment to start
    frontend_proc = run_command(frontend_cmd, "Frontend (Streamlit)")

    print("\n✨ System is up and running!")
    print("👉 Backend: http://127.0.0.1:8000")
    print("👉 Frontend: http://localhost:8501 (Streamlit default)")
    print("\nPress Ctrl+C to stop all services.")

    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_proc.poll() is not None:
                print("❌ Backend process stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("❌ Frontend process stopped unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
    finally:
        # Graceful shutdown
        if sys.platform == 'win32':
            subprocess.run(f"taskkill /F /T /PID {backend_proc.pid}", shell=True, capture_output=True)
            subprocess.run(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True, capture_output=True)
        else:
            backend_proc.terminate()
            frontend_proc.terminate()
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    main()
