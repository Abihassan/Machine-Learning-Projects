from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

# Configuration
CHROMA_DB_DIR = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3"

def get_rag_chain():
    """Initializes the RAG pipeline and returns the retrieval chain."""
    
    # 1. Load Local Embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # 2. Connect to Local Vector Database
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=embeddings
    )
    
    # 3. Create Retriever (fetch top 4 chunks)
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    
    # 4. Initialize Local LLM (Ollama)
    # Using ChatOllama for better conversational capabilities
    llm = ChatOllama(model=LLM_MODEL, temperature=0.2)
    
    # 5. Define Custom Prompt Template
    system_prompt = (
        "You are a helpful Customer Onboarding Assistant. "
        "Use the provided context to answer the user's question about corporate processes. "
        "If the answer is not in the context, say you don't know.\n\n"
        "Context: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    # 6. Build the Chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain

def ask_agent(chain, query: str) -> str:
    """Passes a query to the chain and returns the answer."""
    response = chain.invoke({"input": query})
    return response["answer"]