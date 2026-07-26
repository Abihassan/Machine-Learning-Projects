import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil
import asyncio

from rag_engine import process_and_ingest_pdf, get_rag_chain_stream, get_indexed_documents

app = FastAPI(title="Enterprise Local RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, specify your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks_added = process_and_ingest_pdf(file_path, file.filename)
        return {"message": f"Successfully ingested {file.filename}", "chunks": chunks_added}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/api/documents")
async def list_documents():
    docs = get_indexed_documents()
    return {"documents": docs}

@app.post("/api/chat")
async def chat_stream(request: QueryRequest):
    stream_gen, sources = get_rag_chain_stream(request.query)
    
    async def event_generator():
        # 1. Send the sources first
        yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
        
        # 2. Stream the LLM response tokens
        for chunk in stream_gen:
            yield f"data: {json.dumps({'type': 'token', 'data': chunk})}\n\n"
            await asyncio.sleep(0.01) # Yield control to event loop
            
        # 3. Send completion event
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)