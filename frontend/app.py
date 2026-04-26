import streamlit as st
import requests
import json

st.set_page_config(page_title="RAGentX - Agentic RAG System", layout="wide")

st.title("🤖 RAGentX: Agentic RAG System")
st.markdown("---")

# API Configuration
API_URL = "http://localhost:8000"

# Sidebar for Ingestion
with st.sidebar:
    st.header("📄 Document Ingestion")
    ingest_text = st.text_area("Paste text to ingest:", height=200)
    filename = st.text_input("Filename (optional):", placeholder="data.txt")
    
    if st.button("Ingest Document"):
        if ingest_text:
            try:
                response = requests.post(
                    f"{API_URL}/ingest",
                    json={"text": ingest_text, "filename": filename}
                )
                if response.status_code == 200:
                    st.success("Successfully ingested!")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
        else:
            st.warning("Please enter some text.")

# Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Chat Interface
st.header("💬 Chat")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "debug_info" in message and message["debug_info"]:
            with st.expander("🔍 Trace & Debug Info"):
                st.json(message["debug_info"])

# Chat Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat?debug=true",
                    json={"session_id": st.session_state.session_id, "query": prompt}
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data["response"]
                    debug = data.get("debug_info")
                    
                    st.markdown(answer)
                    if debug:
                        with st.expander("🔍 Trace & Debug Info"):
                            st.json(debug)
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer, 
                        "debug_info": debug
                    })
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
