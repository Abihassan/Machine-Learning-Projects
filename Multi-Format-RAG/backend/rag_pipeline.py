import chromadb
import whisper
import ollama
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# 1. Initialize Local Vector Database
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="multi_modal_rag")

# 2. Load Local Models
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
whisper_model = whisper.load_model("base")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def process_file(file_path: str, filename: str):
    ext = filename.split(".")[-1].lower()
    text_content = ""
    
    # Handle Text / PDF
    if ext == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()
            
    elif ext == "pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_content += extracted + "\n"
                
    # Handle Audio
    elif ext in ["mp3", "wav"]:
        result = whisper_model.transcribe(file_path)
        text_content = f"[Audio Transcript]: {result['text']}"
        
    # Handle Images (LLaVA via Ollama)
    elif ext in ["jpg", "jpeg", "png"]:
        response = ollama.chat(
            model="llava",
            messages=[{
                "role": "user",
                "content": "Describe this image in high detail. Mention all visible objects, text, and context.",
                "images": [file_path]
            }]
        )
        text_content = f"[Image Description]: {response['message']['content']}"
    
    else:
        raise ValueError("Unsupported file format.")
        
    # Chunk and Store Embeddings
    chunks = text_splitter.split_text(text_content)
    if not chunks:
        return
        
    embeddings = embedding_model.encode(chunks).tolist()
    ids = [f"{filename}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename} for _ in chunks]
    
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

def query_rag(query: str):
    # Embed user query
    query_embedding = embedding_model.encode([query]).tolist()
    
    # Retrieve top 3 relevant chunks
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )
    
    if not results["documents"][0]:
        return "I couldn't find any relevant information in the uploaded files.", []
    
    context_chunks = results["documents"][0]
    sources_raw = results["metadatas"][0]
    
    context_str = "\n\n".join(context_chunks)
    unique_sources = list(set([m["source"] for m in sources_raw if "source" in m]))
    
    # Generate response with Llama 3
    prompt = f"Use the provided context to answer the user's question.\n\nContext:\n{context_str}\n\nQuestion: {query}\nAnswer:"
    
    llm_response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return llm_response["message"]["content"], unique_sources