import streamlit as st
import requests
import json
import uuid
import time
from datetime import datetime

st.set_page_config(page_title="RAGentX - Agentic RAG System", layout="wide")

st.title("🤖 RAGentX: Agentic RAG System")
st.markdown("---")

# API Configuration
API_URL = "http://localhost:8000"

# Create a session that doesn't use system proxies (to avoid WinError 10061 on some systems)
http = requests.Session()
http.trust_env = False

# Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "active_download" not in st.session_state:
    st.session_state.active_download = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    enable_web_search = st.toggle("Enable Web Search Fallback", value=False)
    
    st.markdown("---")
    st.info("RAGentX uses a multi-agent loop to retrieve, evaluate, and generate answers from your documents.")

# Main Interface with Tabs
tab_chat, tab_docs = st.tabs(["💬 Chat", "📄 Documents"])

with tab_chat:
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
                    payload = {
                        "session_id": st.session_state.session_id, 
                        "query": prompt,
                        "enable_web_search": enable_web_search
                    }
                    response = http.post(
                        f"{API_URL}/chat?debug=true",
                        json=payload
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

with tab_docs:
    st.header("Document Management")
    
    # Ingestion Section
    col_text, col_file = st.columns(2)
    
    with col_text:
        st.subheader("Text Ingestion")
        ingest_text = st.text_area("Paste text to ingest:", height=200)
        filename_text = st.text_input("Filename (optional):", placeholder="data.txt", key="filename_text")
        
        if st.button("Ingest Text"):
            if ingest_text:
                try:
                    response = http.post(
                        f"{API_URL}/ingest",
                        json={"text": ingest_text, "filename": filename_text}
                    )
                    if response.status_code == 200:
                        st.success("Successfully ingested text!")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
            else:
                st.warning("Please enter some text.")

    with col_file:
        st.subheader("File Upload")
        st.markdown("*Supported formats: PDF, TXT, MD*")
        uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, type=["pdf", "txt", "md"])
        
        if st.button("Upload to RAGentX"):
            if uploaded_files:
                with st.spinner("Uploading files..."):
                    try:
                        # Reset file pointers just in case
                        for f in uploaded_files:
                            f.seek(0)
                        files = [("files", (f.name, f, f.type)) for f in uploaded_files]
                        response = http.post(
                            f"{API_URL}/ingest/file",
                            files=files
                        )
                        if response.status_code == 200:
                            st.success(f"Successfully uploaded {len(uploaded_files)} files!")
                            st.rerun()
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")
            else:
                st.warning("Please select files to upload.")

    st.markdown("---")
    st.subheader("Ingested Documents")
    
    # Use a function for document fetching with a simple retry
    def fetch_documents():
        try:
            res = http.get(f"{API_URL}/ingest/documents", timeout=10)
            if res.status_code == 200:
                return res.json()
        except:
            return None
        return None

    docs = fetch_documents()
    if docs is None:
        st.warning("🔄 Connecting to server...")
        time.sleep(1)
        docs = fetch_documents()

    if docs is not None:
        if not docs:
            st.info("No documents ingested yet.")
        else:
            # Create a clean display for documents
            for doc in docs:
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                    c1.write(f"**{doc.get('filename') or 'Unnamed'}**")
                    
                    # Format date
                    date_str = doc.get('upload_date')
                    if date_str:
                        try:
                            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            date_display = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            date_display = date_str
                    else:
                        date_display = "N/A"
                    
                    c2.write(f"📅 {date_display}")
                    
                    # Download button
                    download_url = f"{API_URL}/ingest/documents/{doc['doc_id']}/download"
                    if c3.button("Download", key=f"dl_{doc['doc_id']}"):
                        try:
                            with st.spinner("Fetching file..."):
                                dl_res = http.get(download_url)
                                if dl_res.status_code == 200:
                                    st.session_state.active_download = {
                                        "doc_id": doc["doc_id"],
                                        "content": dl_res.content,
                                        "filename": doc.get("filename") or "document"
                                    }
                                else:
                                    st.error("Download failed.")
                        except Exception as e:
                            st.error(f"Error: {e}")

                    if st.session_state.active_download and st.session_state.active_download["doc_id"] == doc["doc_id"]:
                        st.download_button(
                            label="📥 Save File",
                            data=st.session_state.active_download["content"],
                            file_name=st.session_state.active_download["filename"],
                            key=f"save_{doc['doc_id']}",
                            on_click=lambda: setattr(st.session_state, 'active_download', None)
                        )

                    # Delete button
                    if c4.button("Delete", key=f"del_{doc['doc_id']}"):
                        try:
                            del_res = http.delete(f"{API_URL}/ingest/documents/{doc['doc_id']}")
                            if del_res.status_code == 200:
                                st.success(f"Deleted {doc.get('filename')}")
                                st.rerun()
                            else:
                                st.error(f"Delete failed: {del_res.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    st.divider()
    else:
        st.error("❌ Backend server unreachable. Please check if RAGentX is running.")
