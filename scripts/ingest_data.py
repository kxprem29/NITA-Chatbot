import json
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveJsonSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_astradb.vectorstores import AstraDBVectorStore

# Load environment variables from your .env file
load_dotenv()
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# This is your original function for processing and embedding data
def process_json_data_with_embeddings(json_data: dict, collection_name: str):
    """
    Processes JSON data, creates embeddings, and stores them in AstraDB.
    """
    print("Splitting JSON data into documents...")
    splitter = RecursiveJsonSplitter(max_chunk_size=2000)
    json_chunks = splitter.split_json(json_data=json_data)
    docs = splitter.create_documents(texts=json_chunks)
    print(f"Data split into {len(docs)} documents.")

    print("Initializing Gemini Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

    print(f"Creating and populating vector store: '{collection_name}'")
    vstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name=collection_name,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_TOKEN,
    )
    
    # This is the key ingestion step
    vstore.add_documents(docs)
    
    print(f"\nVector store '{collection_name}' has been successfully created and populated.")
    return vstore

# Main execution block for running the ingestion
if __name__ == "__main__":
    print("Starting data ingestion process...")
    
    # 1. Load and combine all JSON data from the directory
    combined_data = {}
    JSON_DIR = "data/processed/webpages/json"
    print(f"Reading JSON files from: {JSON_DIR}")
    
    for file in os.listdir(JSON_DIR):
        if file.endswith(".json"):
            file_path = os.path.join(JSON_DIR, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    combined_data[file] = json_data
            except Exception as e:
                print(f"Error processing file {file}: {e}")

    # 2. Call the function to process the data and create the vector store
    if combined_data:
        process_json_data_with_embeddings(combined_data, "department_json_embeddings")
        print("\n✅ Ingestion complete!")
    else:
        print("No JSON data found to process.")