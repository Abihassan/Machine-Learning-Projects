import os
from typing import List, Dict
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document

class RAGService:
    def __init__(self):
        # 1. Initialize Local Embeddings (Sentence Transformers)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'} # Change to 'cuda' if GPU is available
        )
        
        # 2. Initialize Local LLM via Ollama (Assumes Ollama is running locally on default port)
        self.llm = Ollama(model="llama3") # or "mistral", ensure you have pulled it: `ollama run llama3`
        
        # 3. Vector Store Directory
        self.persist_directory = "./data/chroma_db"
        
        # 4. Text Splitter for optimal chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "]
        )
        
        # 5. Strict Prompt Template forcing citations
        self.prompt_template = PromptTemplate(
            template="""You are a strict medical research assistant. Use the following pieces of retrieved context to answer the question. 
            You MUST answer ONLY based on the provided context. If the context does not contain the answer, say "I cannot answer this based on the retrieved medical literature."
            Whenever you state a fact from the context, you MUST append the PubMed ID as an inline citation, e.g., [PMID: 12345678].
            
            Context: {context}
            
            Question: {question}
            
            Answer:""",
            input_variables=["context", "question"]
        )

    def process_and_index_papers(self, papers: List[Dict]) -> Chroma:
        """Chunks PubMed papers and stores them in local ChromaDB."""
        documents = []
        for paper in papers:
            # Attach PMID and Title as metadata for citation retrieval
            doc = Document(
                page_content=paper["text"],
                metadata={"pmid": paper["pmid"], "title": paper["title"]}
            )
            documents.append(doc)
            
        chunks = self.text_splitter.split_documents(documents)
        
        # Create and persist local vector store
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            client_settings=Settings(anonymized_telemetry=False)
        )
        return vectorstore

    def generate_answer(self, question: str, vectorstore: Chroma):
        """Retrieves context and generates a cited answer using Ollama."""
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        
        # Custom QA Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        
        response = qa_chain({"query": question})
        return response