import os
from tempfile import NamedTemporaryFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=100):
        # We use a semantic chunking approach. Overlap prevents cutting sentences in half.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def process_file(self, file_content: bytes, filename: str):
        """Saves file temporarily, extracts text, and chunks it."""
        ext = os.path.splitext(filename)[1].lower()
        
        # Determine appropriate loader
        loaders = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".docx": Docx2txtLoader
        }
        
        if ext not in loaders:
            raise ValueError(f"Unsupported file format: {ext}. Use PDF, TXT, or DOCX.")

        # Save uploaded bytes to a temp file for Langchain loaders
        with NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            loader = loaders[ext](temp_path)
            documents = loader.load()
            
            # Inject filename metadata for database tracing
            for doc in documents:
                doc.metadata['source'] = filename
                
            chunks = self.text_splitter.split_documents(documents)
            return chunks
        finally:
            # Clean up temp file
            os.remove(temp_path)