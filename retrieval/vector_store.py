# retrieval/vector_store.py
from dotenv import load_dotenv
import os
import glob
import PyPDF2

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document

# Load .env
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Load sample documents (PDFs and TXT files)
documents = []
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

# Load PDF files
pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
for pdf_path in pdf_files:
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            
            doc_name = os.path.basename(pdf_path)
            if text.strip():  # Only add if text was extracted
                documents.append(Document(page_content=text, metadata={"doc_name": doc_name}))
                print(f"✓ Loaded {doc_name}")
    except Exception as e:
        print(f"⚠ Error loading {pdf_path}: {e}")

# Load TXT files (for backward compatibility)
txt_files = glob.glob(os.path.join(data_dir, "*.txt"))
for txt_path in txt_files:
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        doc_name = os.path.basename(txt_path)
        documents.append(Document(page_content=text, metadata={"doc_name": doc_name}))
        print(f"✓ Loaded {doc_name}")
    except Exception as e:
        print(f"⚠ Error loading {txt_path}: {e}")

# Split text into chunks with IDs for proper citations
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = []
for doc in documents:
    doc_chunks = splitter.split_documents([doc])
    for chunk_idx, chunk in enumerate(doc_chunks):
        chunk.metadata["chunk_id"] = f"{chunk.metadata['doc_name']}__chunk_{chunk_idx}"
        chunks.append(chunk)

# Create embeddings and FAISS vector store
embeddings = OpenAIEmbeddings()
if chunks:
    vector_store = FAISS.from_documents(chunks, embeddings)
    print(f"✓ Vector store created with {len(chunks)} chunks from {len(documents)} documents")
else:
    print("⚠ Warning: No documents loaded. Vector store will be empty.")
    vector_store = None

# Retrieval function for Research Agent
def retrieve(query, k=3):
    """Retrieve documents with proper citations and chunk tracking."""
    if vector_store is None:
        return [{"text": "No documents available in vector store.", "citation": "N/A", "supported": False}]
    
    results = vector_store.similarity_search_with_score(query, k=k)
    retrieved = []
    for r in results:
        chunk_id = r[0].metadata.get("chunk_id", "unknown")
        doc_name = r[0].metadata.get("doc_name", "unknown")
        retrieved.append({
            "text": r[0].page_content,
            "citation": chunk_id,
            "doc_name": doc_name,
            "similarity_score": float(r[1]),
            "supported": True
        })
    return retrieved
