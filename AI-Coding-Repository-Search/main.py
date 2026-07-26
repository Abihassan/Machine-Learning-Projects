import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI(
    title="AI Coding Repository Search",
    description="Backend API for local codebase ingestion and RAG querying."
)

# ---------------------------------------------------------
# Configuration & Filtering
# ---------------------------------------------------------
IGNORED_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", ".idea", ".vscode", "dist", "build"}
ALLOWED_EXTENSIONS = {".py", ".ts", ".js", ".md", ".tsx", ".jsx", ".html", ".css", ".json", ".txt"}

# Initialize the text splitter
# We use chunk_size=1000 and overlap=200 to ensure context isn't lost between chunks.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def should_process_file(file_path: Path) -> bool:
    """Check if the file has an allowed extension and is not in an ignored directory."""
    if file_path.suffix not in ALLOWED_EXTENSIONS:
        return False
    for part in file_path.parts:
        if part in IGNORED_DIRS:
            return False
    return True

def parse_and_chunk_directory(repo_path: Path) -> List[dict]:
    """Recursively read files, filter them, and split them into chunks."""
    chunks_data = []
    
    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found.")

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = Path(root) / file
            
            if should_process_file(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Split the file content into smaller chunks
                    texts = text_splitter.split_text(content)
                    
                    # Store chunks with their metadata for vectorization later
                    for i, text in enumerate(texts):
                        chunks_data.append({
                            "file_path": str(file_path),
                            "chunk_index": i,
                            "content": text
                        })
                except Exception as e:
                    print(f"Skipping {file_path} due to read error: {e}")
                    
    return chunks_data

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.post("/ingest")
async def ingest_repository(
    repo_path: Optional[str] = Form(default="/Users/abihassan/repos/my-project"),
    repo_zip: Optional[UploadFile] = File(None)
):
    """
    Ingest a repository by providing a local path or uploading a .zip file.
    It parses the files, chunks the text, and prepares it for embedding.
    """
    target_dir = None
    cleanup_needed = False

    try:
        # Handle Zip File Upload
        if repo_zip:
            target_dir = Path(f"./temp_extracted_{repo_zip.filename}")
            target_dir.mkdir(exist_ok=True)
            
            zip_path = target_dir / repo_zip.filename
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(repo_zip.file, buffer)
                
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
                
            os.remove(zip_path) # Clean up the raw zip file
            cleanup_needed = True

        # Handle Local Directory Path
        elif repo_path:
            target_dir = Path(repo_path)
            
        else:
            raise HTTPException(status_code=400, detail="Must provide either repo_path or repo_zip.")

        # Parse files and generate chunks
        chunks = parse_and_chunk_directory(target_dir)
        
        # NOTE: In Step 2, we will embed these chunks and store them in ChromaDB/FAISS.
        # For now, we return a summary to confirm ingestion is working.
        
        return {
            "status": "success",
            "message": f"Successfully parsed and chunked repository.",
            "total_files_processed": len(set(c["file_path"] for c in chunks)),
            "total_chunks_generated": len(chunks)
        }

    finally:
        # Clean up temporary extracted zip directories
        if cleanup_needed and target_dir and target_dir.exists():
             shutil.rmtree(target_dir)