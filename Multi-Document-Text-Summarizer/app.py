import streamlit as st
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# ==========================================
# 1. Configuration and UI Setup
# ==========================================
st.set_page_config(page_title="Local Multi-Doc Summarizer", layout="wide")
st.title("📄 Local Multi-Document Executive Summarizer")
st.markdown("""
Upload multiple PDFs, and this app will use a **100% local Large Language Model** to read, chunk, 
and condense them into a cohesive set of executive bullet points.
""")

# Sidebar settings for Model and Chunking
with st.sidebar:
    st.header("⚙️ Configuration")
    model_name = st.text_input("Ollama Model Name", value="llama3:8b")
    chunk_size = st.slider("Chunk Size (Tokens/Chars)", 2000, 8000, 4000)
    chunk_overlap = st.slider("Chunk Overlap", 100, 1000, 200)

uploaded_files = st.file_uploader("Upload PDF Documents", type="pdf", accept_multiple_files=True)

# ==========================================
# 2. Prompt Engineering
# ==========================================

# Map Prompt: For summarizing individual chunks
map_prompt_template = """
You are an expert analyst. Write a concise, factual summary of the following text:

"{text}"

CONCISE SUMMARY:
"""
map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])

# Reduce Prompt: For condensing all chunk summaries into executive bullets
reduce_prompt_template = """
You are a C-level executive assistant. The following is a set of summaries derived from multiple documents:

{text}

Take these summaries and distill them into a single, cohesive list of professional, high-level executive bullet points. 
Highlight only the most critical information, key decisions, and major findings. 
Do not include conversational filler. Format the output strictly as a bulleted list.

EXECUTIVE BULLET POINTS:
"""
reduce_prompt = PromptTemplate(template=reduce_prompt_template, input_variables=["text"])

# ==========================================
# 3. Core Processing Logic
# ==========================================
if st.button("Generate Executive Summary") and uploaded_files:
    
    try:
        # Step A: Initialize the local LLM via modern OllamaLLM
        llm = OllamaLLM(model=model_name, temperature=0.1)
        
        all_documents = []
        
        # Step B: Save uploaded files to a temp directory and load them
        with st.spinner("Loading and parsing PDFs..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                for uploaded_file in uploaded_files:
                    temp_filepath = os.path.join(temp_dir, uploaded_file.name)
                    
                    with open(temp_filepath, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Load PDF
                    loader = PyPDFLoader(temp_filepath)
                    docs = loader.load()
                    all_documents.extend(docs)
        
        if not all_documents:
            st.error("No text could be extracted from the uploaded PDFs.")
            st.stop()
            
        # Step C: Text Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        split_docs = text_splitter.split_documents(all_documents)
        
        st.info(f"Loaded {len(all_documents)} pages. Split into {len(split_docs)} chunks for processing.")
        
        # ==========================================
        # Step D: Manual Map-Reduce via LCEL
        # ==========================================
        
        # 1. MAP STEP (Summarize each chunk)
        st.subheader("1. Analyzing Document Chunks")
        map_chain = map_prompt | llm
        chunk_summaries = []
        
        # Setup Progress Bar
        progress_text = "Processing chunk 0..."
        my_bar = st.progress(0.0, text=progress_text)
        
        for i, doc in enumerate(split_docs):
            # Run the LLM on this specific chunk
            summary = map_chain.invoke({"text": doc.page_content})
            chunk_summaries.append(summary)
            
            # Update the progress bar visually
            current_progress = (i + 1) / len(split_docs)
            my_bar.progress(current_progress, text=f"Processing chunk {i+1} of {len(split_docs)}...")
            
        # 2. REDUCE STEP (Combine all summaries into final bullets)
        st.subheader("2. Generating Final Executive Summary")
        with st.spinner("Condensing chunk analyses into final bullet points..."):
            combined_text = "\n\n".join(chunk_summaries)
            reduce_chain = reduce_prompt | llm
            final_summary = reduce_chain.invoke({"text": combined_text})
        
        # Step E: Display Results
        st.success("Summarization Complete!")
        st.markdown("---")
        st.markdown(final_summary)
        
    except Exception as e:
        st.error("An error occurred during processing.")
        st.error(f"Details: {str(e)}")
        
elif not uploaded_files:
    st.warning("Please upload at least one PDF to begin.")