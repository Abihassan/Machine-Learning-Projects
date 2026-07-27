from Bio import Entrez
from typing import List, Dict

# Standard practice: Provide an email to NCBI
Entrez.email = "your.email@example.com" 

class PubMedService:
    @staticmethod
    def fetch_papers(query: str, max_results: int = 5) -> List[Dict]:
        """
        Searches PubMed for the given query and retrieves abstracts.
        """
        try:
            # 1. Search for relevant PubMed IDs
            search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            search_results = Entrez.read(search_handle)
            search_handle.close()
            
            id_list = search_results.get("IdList", [])
            if not id_list:
                return []

            # 2. Fetch details for the retrieved IDs
            fetch_handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
            papers_data = Entrez.read(fetch_handle)
            fetch_handle.close()

            papers = []
            for article in papers_data.get("PubmedArticle", []):
                medline = article.get("MedlineCitation", {})
                pmid = str(medline.get("PMID", ""))
                article_data = medline.get("Article", {})
                title = article_data.get("ArticleTitle", "")
                
                # Extract abstract if available
                abstract_texts = article_data.get("Abstract", {}).get("AbstractText", [])
                abstract = " ".join([str(text) for text in abstract_texts]) if abstract_texts else ""
                
                if abstract: # Only keep papers with abstracts for meaningful RAG
                    papers.append({
                        "pmid": pmid,
                        "title": title,
                        "text": abstract
                    })
                    
            return papers
        except Exception as e:
            print(f"Error fetching from PubMed: {e}")
            return []