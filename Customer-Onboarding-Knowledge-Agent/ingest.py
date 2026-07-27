import os
import glob
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

# Configuration
DOCS_DIR = "./docs"
CHROMA_DB_DIR = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def load_documents(docs_dir):
    """Loads PDF and TXT/MD files from the specified directory."""
    documents = []
    
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"Created directory {docs_dir}. Please add your documents and run again.")
        return documents

    # Load PDFs
    for file in glob.glob(os.path.join(docs_dir, "*.pdf")):
        loader = PyPDFLoader(file)
        documents.extend(loader.load())
        print(f"Loaded: {file}")

    # Load Text/Markdown files
    for file in glob.glob(os.path.join(docs_dir, "*.txt")) + glob.glob(os.path.join(docs_dir, "*.md")):
        loader = TextLoader(file, encoding="utf-8")
        documents.extend(loader.load())
        print(f"Loaded: {file}")
        
    return documents

def main():
    print("Starting document ingestion...")
    docs = load_documents(DOCS_DIR)
    
    if not docs:
        print("No documents found. Exiting.")
        return

    # Chunk the documents
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Generated {len(chunks)} chunks.")

    # Initialize Local Embeddings
    print(f"Loading HuggingFace embeddings ({EMBEDDING_MODEL})...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Store in ChromaDB
    print("Creating Chroma vector store...")
    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    
    print(f"Successfully ingested data into vector store at {CHROMA_DB_DIR}")

if __name__ == "__main__":
    main()