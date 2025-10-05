from langchain.text_splitter import RecursiveJsonSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_astradb.vectorstores import AstraDBVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
import json
import os

from dotenv import load_dotenv
load_dotenv()

ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def process_json_data_with_embeddings(json_data: dict, collection_name: str):
    """
    Processes JSON data using RecursiveJsonSplitter, creates embeddings with Gemini,
    and stores them in an AstraDB vector store.

    Args:
        json_data: The dictionary containing the loaded JSON data.
        collection_name: The name of the AstraDB collection to store embeddings.

    Returns:
        The AstraDBVectorStore object containing the new embeddings.
    """
    # Initialize RecursiveJsonSplitter
    splitter = RecursiveJsonSplitter(max_chunk_size=2000)
    test = splitter.split_json(json_data)
    # Split the JSON data
    docs = splitter.create_documents(test)

    # Initialize Gemini Embeddings
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

    # Ensure ASTRA_DB_API_ENDPOINT and ASTRA_DB_TOKEN are set as environment variables or Colab secrets
    # Create and populate AstraDB Vector Store
    vstore_json = AstraDBVectorStore(
        embedding=embeddings,
        collection_name=collection_name,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_TOKEN,
    )

    vstore_json.add_documents(docs)

    print(f"Vector store '{collection_name}' created and populated with JSON data embeddings.")

    return vstore_json

# Example usage (assuming 'data' contains the loaded JSON)
# vstore_json_embeddings = process_json_data_with_embeddings(data, "department_json_embeddings")


def query_json_vstore_with_gemini(query: str, vstore_json: AstraDBVectorStore, google_api_key: str):
    """
    Queries the JSON-based vector store and uses Gemini to generate a response.

    Args:
        query: The user's query string.
        vstore_json: The AstraDBVectorStore object containing JSON data embeddings.
        google_api_key: Your Google API key for Gemini.

    Returns:
        A tuple containing the generated response string and a list of retrieved Document objects.
    """
    # Retrieve documents from the JSON vector store

    # Define the prompt template
    prompt_template = ChatPromptTemplate.from_template(
        """

        Answer the user's question based on the following context:
        {context}

        Question: {question}
        """
    )

    # Initialize the Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key)

    # Define the RAG chain
    # We need to format the retrieved documents for the prompt
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    # Create a retriever from the JSON-based vector store for the RAG chain
    retriever_json = vstore_json.as_retriever()

    rag_chain_json = (
        {"context": retriever_json | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    # Invoke the RAG chain with the query
    response = rag_chain_json.invoke(query)
    return response

# Example usage (assuming 'vstore_json_embeddings' and 'GOOGLE_API_KEY' are available)
# query = "What are the facilities in the Civil Engineering department?"
# response_json, contexts_json = query_json_vstore_with_gemini(query, vstore_json_embeddings, GOOGLE_API_KEY)
# print("Generated Response (from JSON):")
# print(response_json)



if __name__ == "__main__":

    combined_data = {}
    JSON_DIR = "data/processed/webpages/json"
    directories = os.listdir(JSON_DIR)
    for file in directories:
        if file.endswith(".json"):
            file_path = os.path.join(JSON_DIR, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                    # Assuming each json file contains a dictionary and we want to merge them
                    combined_data[file] = json_data
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file: {file}")
                except Exception as e:
                    print(f"An error occurred while processing file {file}: {e}")


    vstore_json_embeddings = process_json_data_with_embeddings(combined_data, "department_json_embeddings")


    print("\nQuerying the vector store...")
    response = query_json_vstore_with_gemini("chairman of bog", vstore_json_embeddings, GOOGLE_API_KEY)

    print("\nGenerated Response:")
    print(response)