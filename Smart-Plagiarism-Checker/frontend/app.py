import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Plagiarism Checker", layout="wide")

st.title("🕵️‍♂️ Semantics-Aware Plagiarism Checker")
st.markdown("Check documents against a local database using context-aware NLP embeddings.")

col1, col2 = st.columns(2)

with col1:
    st.header("1. Build Knowledge Base")
    st.info("Upload source documents here to build your reference database.")
    db_file = st.file_uploader("Upload reference file (PDF, TXT, DOCX)", key="db_upload")
    
    if st.button("Add to Database"):
        if db_file:
            with st.spinner("Indexing document..."):
                files = {"file": (db_file.name, db_file.getvalue(), db_file.type)}
                response = requests.post(f"{API_URL}/upload_to_db/", files=files)
                if response.status_code == 200:
                    st.success(response.json()["message"])
                else:
                    st.error(f"Error: {response.json().get('detail', 'Upload failed')}")
        else:
            st.warning("Please select a file first.")

with col2:
    st.header("2. Check for Plagiarism")
    st.info("Upload a document to check for semantic similarity against the database.")
    check_file = st.file_uploader("Upload file to check (PDF, TXT, DOCX)", key="check_upload")
    
    if st.button("Run Plagiarism Check"):
        if check_file:
            with st.spinner("Analyzing semantics..."):
                files = {"file": (check_file.name, check_file.getvalue(), check_file.type)}
                response = requests.post(f"{API_URL}/check_plagiarism/", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    score = data["overall_score"]
                    
                    # Display Overall Score
                    st.subheader("Results")
                    if score > 20:
                        st.error(f"**Overall Similarity Score: {score}%**")
                    elif score > 0:
                        st.warning(f"**Overall Similarity Score: {score}%**")
                    else:
                        st.success(f"**Overall Similarity Score: {score}% (Clean)**")
                    
                    st.write(f"Matched {data['plagiarized_chunks']} out of {data['total_chunks']} chunks.")
                    
                    # Display Details
                    if data["details"]:
                        st.markdown("### Flagged Sections")
                        for idx, match in enumerate(data["details"]):
                            with st.expander(f"Match {idx+1} - Similarity: {match['similarity_score']}% (Source: {match['source']})"):
                                st.markdown("**Uploaded Document Text:**")
                                st.write(f"> {match['query_text']}")
                                st.markdown("**Matches Database Text:**")
                                st.write(f"> {match['matched_text']}")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Analysis failed')}")
        else:
            st.warning("Please select a file first.")