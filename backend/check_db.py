import chromadb
# from langchain_community.embeddings import HuggingFaceEmbeddings

# --- Configure these to match your project ---
PERSIST_DIRECTORY = "./vector_db"
COLLECTION_NAME = "college_docs"
# ---------------------------------------------

print("Attempting to connect to the database...")

try:
    # Initialize the persistent client
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    
    # Get the collection
    collection = client.get_collection(name=COLLECTION_NAME)
    
    # Get the total number of items in the collection
    count = collection.count()
    
    print(f"\n✅ Success! Connected to collection '{COLLECTION_NAME}'.")
    print(f"   The collection contains {count} document chunks.")
    
    if count == 0:
        print("\n❗️ WARNING: The collection is empty! You need to run your data processing script.")
        
except Exception as e:
    print(f"\n❌ ERROR: Could not connect to the database. Details: {e}")
    print("   Please check if the PERSIST_DIRECTORY and COLLECTION_NAME are correct.")