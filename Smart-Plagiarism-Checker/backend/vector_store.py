import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

class VectorStoreManager:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        # Initialize local HuggingFace embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Ensure Chroma uses cosine similarity (default is L2)
        collection_metadata = {"hnsw:space": "cosine"}
        
        self.vector_store = Chroma(
            collection_name="documents_collection",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
            collection_metadata=collection_metadata
        )

    def add_documents(self, chunks):
        """Embeds and stores document chunks in ChromaDB."""
        if not chunks:
            raise ValueError("No text chunks provided for storage.")
        self.vector_store.add_documents(chunks)

    def similarity_search(self, query: str, k: int = 1):
        """Searches DB for similar chunks. Returns chunks and cosine distance."""
        # Note: Chroma with "cosine" space returns distance (1 - similarity)
        # 0.0 means identical, 1.0 means completely orthogonal.
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results