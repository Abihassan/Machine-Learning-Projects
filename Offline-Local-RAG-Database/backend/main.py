import os
import shutil
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI(title="Local RAG API")

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize offline embeddings (downloads once, runs offline)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store_dir = "./chroma_db"
vector_store = Chroma(persist_directory=vector_store_dir, embedding_function=embeddings)

os.makedirs("temp_uploads", exist_ok=True)

class ChatRequest(BaseModel):
    query: str
    model: str = "phi3"

@app.get("/models")
async def get_models():
    """Fetch downloaded models from local Ollama instance."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        models = [model["name"] for model in response.json().get("models", [])]
        return {"models": models}
    except requests.RequestException:
        return {"models": ["phi3", "llama3"]} # Fallback

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Ingest, chunk, and embed documents."""
    file_path = f"temp_uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Select Loader
    if file.filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file.filename.endswith(".txt"):
        loader = TextLoader(file_path)
    elif file.filename.endswith(".md"):
        loader = UnstructuredMarkdownLoader(file_path)
    else:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Unsupported file format")

    documents = loader.load()
    
    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # Store in ChromaDB
    vector_store.add_documents(chunks)
    os.remove(file_path)
    
    return {"message": f"Successfully processed {len(chunks)} chunks from {file.filename}."}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Query the local LLM using the vector store context."""
    llm = Ollama(model=request.model, base_url="http://localhost:11434")
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    response = rag_chain.invoke({"input": request.query})
    
    sources = [{"source": doc.metadata.get("source", "Unknown"), "content": doc.page_content} for doc in response["context"]]
    
    return {"answer": response["answer"], "sources": sources}