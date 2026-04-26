import streamlit as st
import requests
import json
import uuid
from datetime import datetime

st.set_page_config(page_title="RAGentX - Agentic RAG System", layout="wide")

st.title("🤖 RAGentX: Agentic RAG System")
st.markdown("---")

# API Configuration
API_URL = "http://localhost:8000"

# Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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
                    response = requests.post(
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
                    response = requests.post(
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
        uploaded_files = st.file_uploader("Upload files (PDF, TXT, MD)", accept_multiple_files=True)
        
        if st.button("Upload to RAGentX"):
            if uploaded_files:
                with st.spinner("Uploading files..."):
                    try:
                        files = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                        response = requests.post(
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
    
    try:
        docs_response = requests.get(f"{API_URL}/ingest/documents")
        if docs_response.status_code == 200:
            docs = docs_response.json()
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
                        try:
                            download_url = f"{API_URL}/ingest/documents/{doc['doc_id']}/download"
                            # We need to fetch the content for the download button in Streamlit
                            # Alternatively, we can use a link, but download_button is nicer.
                            # Note: Fetching here might be slow if there are many large files.
                            # A better way might be to only fetch on click, but st.download_button needs data upfront.
                            # Let's use a link for simplicity if content is large, or just download it.
                            if st.button("Download", key=f"dl_{doc['doc_id']}"):
                                dl_res = requests.get(download_url)
                                if dl_res.status_code == 200:
                                    st.download_button(
                                        label="Confirm Download",
                                        data=dl_res.content,
                                        file_name=doc.get('filename') or "document",
                                        key=f"confirm_dl_{doc['doc_id']}"
                                    )
                                else:
                                    st.error("Download failed.")
                        except:
                            c3.write("Error")

                        # Delete button
                        if c4.button("Delete", key=f"del_{doc['doc_id']}"):
                            try:
                                del_res = requests.delete(f"{API_URL}/ingest/documents/{doc['doc_id']}")
                                if del_res.status_code == 200:
                                    st.success(f"Deleted {doc.get('filename')}")
                                    st.rerun()
                                else:
                                    st.error(f"Delete failed: {del_res.text}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                        st.divider()
        else:
            st.error("Failed to fetch documents.")
    except Exception as e:
        st.error(f"Connection failed: {e}")
