import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Core RAG Imports ---
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from the .env file
load_dotenv()

# --- 1. Initialize the Google Gemini LLM ---
# Check if the API key is available
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please add it.")

# Use a fast and efficient model from the Gemini family
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Define the FastAPI application
app = FastAPI(
    title="RAG Chatbot API with Google Gemini",
    description="A backend for a Retrieval-Augmented Generation application using Gemini.",
)

# Pydantic model for the incoming JSON request
class Query(BaseModel):
    user_query: str

# --- 2. Setup the rest of the RAG pipeline (Embeddings and VectorDB) ---
# Use the same embedding model used during data processing
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Set up ChromaDB client to connect to your existing collection
PERSIST_DIRECTORY = "./vector_db"
COLLECTION_NAME = "college_docs"

# Connect to the persisted ChromaDB collection
vector_db = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embedding_model,
    collection_name=COLLECTION_NAME
)

# --- 3. Define the Prompt Template ---
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}

---
Question: {question}
"""
prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


@app.post("/chat")
def get_chatbot_response(query: Query):
    """
    Receives a user query and returns a response from the RAG pipeline.
    """
    # 1. Retrieve the top 4 most relevant documents from the vector database.
    retrieved_docs = vector_db.similarity_search(query.user_query, k=4)
    
    # 2. Extract the text content from the retrieved documents to form the context.
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

    # ADD THESE LINES FOR DEBUGGING
    print("\n" + "="*50)
    print("--- CONTEXT SENT TO LLM ---")
    print(context_text)
    print("="*50 + "\n")

    # 3. Create the RAG chain using LangChain Expression Language (LCEL)
    rag_chain = prompt_template | llm | StrOutputParser()

    # 4. Invoke the chain with the user's query and the retrieved context
    final_response = rag_chain.invoke({
        "context": context_text,
        "question": query.user_query
    })
    
    # Return the LLM's final response
    return {"response": final_response}


# To run the API, navigate to the 'backend' directory in your terminal and run:
# uvicorn main:app --reload