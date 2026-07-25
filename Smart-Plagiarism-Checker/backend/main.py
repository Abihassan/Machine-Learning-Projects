from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.document_processor import DocumentProcessor
from backend.vector_store import VectorStoreManager
from backend.scorer import PlagiarismScorer

app = FastAPI(title="Smart Plagiarism Checker API")

# Initialize modules
processor = DocumentProcessor()
vector_store_manager = VectorStoreManager()
scorer = PlagiarismScorer(vector_store_manager, threshold=0.85)

@app.post("/upload_to_db/")
async def upload_to_db(file: UploadFile = File(...)):
    """Extracts text, creates embeddings, and stores in Vector DB as reference material."""
    try:
        content = await file.read()
        chunks = processor.process_file(content, file.filename)
        vector_store_manager.add_documents(chunks)
        return {"message": f"Successfully indexed '{file.filename}' with {len(chunks)} chunks."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/check_plagiarism/")
async def check_plagiarism(file: UploadFile = File(...)):
    """Checks an uploaded file against the DB for similarity."""
    try:
        content = await file.read()
        chunks = processor.process_file(content, file.filename)
        results = scorer.check_document(chunks)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))