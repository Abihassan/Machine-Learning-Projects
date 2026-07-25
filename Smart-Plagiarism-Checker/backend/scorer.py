class PlagiarismScorer:
    def __init__(self, vector_store, threshold=0.85):
        self.vector_store = vector_store
        # Cosine distance threshold (Distance = 1 - Similarity)
        # Similarity > 0.85 means Distance < 0.15
        self.distance_threshold = 1.0 - threshold 

    def check_document(self, query_chunks):
        """Checks a list of chunks against the DB to calculate plagiarism score."""
        total_chunks = len(query_chunks)
        plagiarized_chunks = 0
        flagged_details = []

        if total_chunks == 0:
            return {"score": 0.0, "details": []}

        for chunk in query_chunks:
            # Search top 1 closest match for this chunk
            search_results = self.vector_store.similarity_search(chunk.page_content, k=1)
            
            if search_results:
                best_match_doc, best_distance = search_results[0]
                
                # Convert distance back to similarity for UI readability
                similarity = 1.0 - best_distance
                
                if best_distance <= self.distance_threshold:
                    plagiarized_chunks += 1
                    flagged_details.append({
                        "query_text": chunk.page_content,
                        "matched_text": best_match_doc.page_content,
                        "source": best_match_doc.metadata.get("source", "Unknown"),
                        "similarity_score": round(similarity * 100, 2)
                    })

        overall_score = (plagiarized_chunks / total_chunks) * 100
        return {
            "overall_score": round(overall_score, 2),
            "plagiarized_chunks": plagiarized_chunks,
            "total_chunks": total_chunks,
            "details": flagged_details
        }