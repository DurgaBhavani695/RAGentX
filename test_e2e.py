import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8001"

def test_system():
    print("🚀 Starting End-to-End Test...")

    # 1. Ingest
    print("\n📥 Ingesting document...")
    ingest_data = {
        "text": "RAGentX is an advanced multi-agent system built by an expert AI agent in April 2026. It uses LangGraph for orchestration.",
        "filename": "test_info.txt"
    }
    try:
        response = requests.post(f"{BASE_URL}/ingest", json=ingest_data)
        print(f"Ingest Status: {response.status_code}")
        print(f"Ingest Response: {response.json()}")
    except Exception as e:
        print(f"❌ Ingest failed: {e}")
        return

    # 2. Chat
    print("\n💬 Sending chat query...")
    chat_data = {
        "session_id": "test_session_1",
        "query": "What is RAGentX and when was it built?"
    }
    try:
        response = requests.post(f"{BASE_URL}/chat?debug=true", json=chat_data)
        print(f"Chat Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Assistant: {data['response']}")
            print(f"\n🔍 Debug Info: {data.get('debug_info')}")
        else:
            print(f"❌ Chat failed: {response.text}")
    except Exception as e:
        print(f"❌ Chat request failed: {e}")

if __name__ == "__main__":
    test_system()
