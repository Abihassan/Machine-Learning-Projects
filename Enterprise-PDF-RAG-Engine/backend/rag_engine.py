import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# Configuration
CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama3"

# Initialize singletons to avoid reloading in memory
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
llm = Ollama(model=LLM_MODEL)
vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

def process_and_ingest_pdf(file_path: str, filename: str):
    """Parses a PDF, splits it into chunks, and stores embeddings in Chroma."""
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()

    # Inject filename into metadata for frontend citation
    for doc in documents:
        doc.metadata["source_file"] = filename

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    
    # Ingest into Vector DB
    vector_store.add_documents(chunks)
    return len(chunks)

def get_rag_chain_stream(query: str):
    """Retrieves context and yields streamed tokens from the local LLM."""
    docs = vector_store.similarity_search(query, k=4)
    
    # Extract metadata for citations
    sources = [
        {
            "file": doc.metadata.get("source_file", "Unknown"), 
            "page": doc.metadata.get("page", 0) + 1
        } 
        for doc in docs
    ]
    
    # Deduplicate sources
    unique_sources = [dict(t) for t in {tuple(d.items()) for d in sources}]
    
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt_template = """You are a helpful internal corporate assistant. Use the following context to answer the question securely. 
    If you don't know the answer based on the context, say so. Do not use outside knowledge.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    formatted_prompt = prompt.format(context=context, question=query)
    
    return llm.stream(formatted_prompt), unique_sources

def get_indexed_documents():
    """Retrieves unique document names from the vector store."""
    try:
        data = vector_store.get()
        metadatas = data.get("metadatas", [])
        return list(set(meta.get("source_file") for meta in metadatas if meta and "source_file" in meta))
    except Exception:
        return []