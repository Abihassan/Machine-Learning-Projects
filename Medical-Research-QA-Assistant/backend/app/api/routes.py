from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, SourceReference
from app.services.pubmed_service import PubMedService
from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

@router.post("/ask", response_model=QueryResponse)
async def ask_medical_question(request: QueryRequest):
    try:
        # 1. Fetch live data from PubMed based on the question keywords
        # Note: In a production app, you might want a separate keyword extraction step
        print(f"\n--- New Query: {request.question} ---")
        
        print("1. Fetching papers from PubMed...")
        papers = PubMedService.fetch_papers(request.question, max_results=request.max_papers)
        
        if not papers:
            raise HTTPException(status_code=404, detail="No relevant medical papers found on PubMed.")

        # 2. Index the fetched papers locally
        print(f"2. Found {len(papers)} papers. Indexing into ChromaDB...")
        vectorstore = rag_service.process_and_index_papers(papers)

        # 3. Perform RAG to get the answer
        print("3. Indexing complete! Sending to local LLM (Ollama) for generation...")
        print("   (Note: If this step takes a long time, it is due to local CPU processing)")
        rag_result = rag_service.generate_answer(request.question, vectorstore)
        
        # 4. Format sources for the frontend
        print("4. Answer successfully generated!")
        source_docs = rag_result.get("source_documents", [])
        sources = []
        seen_pmids = set()
        
        for doc in source_docs:
            pmid = doc.metadata.get("pmid")
            if pmid not in seen_pmids:
                sources.append(
                    SourceReference(
                        pmid=pmid,
                        title=doc.metadata.get("title", "Unknown Title"),
                        snippet=doc.page_content[:200] + "..." # Snippet for frontend reference card
                    )
                )
                seen_pmids.add(pmid)

        # 5. Cleanup ChromaDB collection to keep memory fresh per query (optional, depends on use case)
        vectorstore.delete_collection()

        return QueryResponse(
            answer=rag_result["result"],
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))