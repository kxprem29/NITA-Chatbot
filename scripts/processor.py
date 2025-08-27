import json
import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- Configuration ---
# This assumes you run the script from the root of your project directory
WEB_TEXT_DIR = "data/processed/webpages"
PDF_JSON_PATH = "data/processed/pdfs/pdf_metadata.json" # Assuming your PDF JSON is here
UNIFIED_DATA_PATH = "data/processed/unified_data.json"
DB_PATH = "backend/vector_db"
COLLECTION_NAME = "college_docs"

# ==================================================================================
# == TASK 3.1: LOAD AND UNIFY ALL DATA SOURCES
# ==================================================================================
def load_and_unify_data():
    """
    Loads data from text files and a JSON file, unifies them into a single
    list of LangChain Document objects, and saves the result to a file.
    """
    print("--- Task 3.1: Loading and Unifying Data ---")

    # 1. Load from .txt files
    print(f"Loading text files from: {WEB_TEXT_DIR}")
    loader = DirectoryLoader(WEB_TEXT_DIR, glob="**/*.txt", show_progress=True)
    web_docs = loader.load()
    print(f"Loaded {len(web_docs)} documents from webpages.")

    # 2. Load from JSON file (PDF metadata)
    print(f"Loading PDF metadata from: {PDF_JSON_PATH}")
    pdf_docs = []
    try:
        with open(PDF_JSON_PATH, 'r') as f:
            pdf_metadata = json.load(f)
        
        for item in pdf_metadata:
            content = f"Title: {item.get('title', '')}\nDescription: {item.get('description', '')}"
            metadata = {"source": item.get('url', '')}
            doc = Document(page_content=content, metadata=metadata)
            pdf_docs.append(doc)
        print(f"Loaded {len(pdf_docs)} documents from PDF metadata.")
    except FileNotFoundError:
        print(f"Warning: PDF metadata file not found at {PDF_JSON_PATH}. Skipping.")

    # 3. Combine both lists
    all_docs = web_docs + pdf_docs
    print(f"Total documents unified: {len(all_docs)}")
    
    # 4. Save the unified data to a single file (as requested)
    print(f"Saving unified data to: {UNIFIED_DATA_PATH}")
    serializable_docs = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in all_docs]
    with open(UNIFIED_DATA_PATH, 'w') as f:
        json.dump(serializable_docs, f, indent=4)
    print("Unified data saved successfully.")
    
    return all_docs

# ==================================================================================
# == TASK 3.2: IMPLEMENT ADVANCED CHUNKING
# ==================================================================================
def chunk_documents(docs):
    """
    Splits a list of documents into smaller chunks using a text splitter.
    """
    print("\n--- Task 3.2: Chunking Documents ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Split {len(docs)} documents into {len(chunks)} chunks.")
    return chunks

# ==================================================================================
# == TASK 4: BUILD THE VECTOR DATABASE
# ==================================================================================
def build_vector_database(chunks):
    """
    Generates embeddings for chunks and stores them in a persistent ChromaDB.
    """
    print("\n--- Task 4: Building Vector Database ---")
    
    # Task 4.1: Generate Embeddings
    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    # This will download the model from Hugging Face the first time you run it
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'} # Use CPU for broad compatibility
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    print("Embedding model loaded.")

    # Task 4.2: Index and Store in ChromaDB
    print(f"Creating and persisting Vector DB at: {DB_PATH}")
    # This single command creates the DB, generates embeddings, and stores them.
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH,
        collection_name=COLLECTION_NAME
    )
    print("Vector database created and persisted successfully.")
    return vector_db

# ==================================================================================
# == MAIN EXECUTION
# ==================================================================================
if __name__ == "__main__":
    # Execute Task 3
    documents = load_and_unify_data()
    chunked_documents = chunk_documents(documents)
    
    # Execute Task 4
    db = build_vector_database(chunked_documents)
    
    print("\n✅ All tasks completed successfully!")