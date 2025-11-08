from langchain.text_splitter import RecursiveJsonSplitter, RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_astradb.vectorstores import AstraDBVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from tqdm import tqdm
import os
import json
from dotenv import load_dotenv

load_dotenv()

ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vstore(collection_name: str) -> AstraDBVectorStore:
    """Initialize AstraDB vector store with Gemini embeddings."""
    return AstraDBVectorStore(
        embedding=embeddings,
        collection_name=collection_name,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_TOKEN,
    )

# def process_json_data_with_embeddings(json_data: dict, collection_name: str) -> AstraDBVectorStore:
#     """
#     Split JSON data into documents, embed them with Gemini, and store in AstraDB.
#     """
#     splitter = RecursiveJsonSplitter(max_chunk_size=2000)
#     docs = splitter.create_documents(splitter.split_json(json_data))

#     vstore_json = get_vstore(collection_name)
#     vstore_json.add_documents(docs)

#     print(f"✅ Vector store '{collection_name}' created with {len(docs)} docs.")
#     return vstore_json

def process_json_data_with_embeddings(json_list, metadata_dict, collection_name):
    """Processes JSON data, splits it, and adds documents with metadata to AstraDB."""
    vstore_json = get_vstore(collection_name)

    # Clear existing collection data if needed (optional)
    # vstore_json.delete_collection()
    # time.sleep(10) # Give Astra DB time to delete

    print(f"Processing {len(json_list)} JSON files...")

    for item in tqdm(json_list, desc="Processing JSON files"):
        file_name = item["file_name"]
        file_content = item["content"]

        # Get the metadata for the current file
        metadata = metadata_dict.get(file_name, {})

        # Use RecursiveJsonSplitter to split the JSON content
        splitter = RecursiveJsonSplitter(max_chunk_size=10000)
        try:
            # Convert json content to string if it's not already
            # print(metadata)
            file_data = {
                file_name:file_content
            }
            docs = splitter.create_documents(texts=splitter.split_json(file_data), metadatas=[metadata])

            # Add the documents to the vector store
            if docs:
                vstore_json.add_documents(docs)
                print(f"Added {len(docs)} documents from {file_name}")
            else:
                print(f"No documents generated for {file_name}")
        except Exception as e:
            print(file_content)
            print(f"Error splitting or adding documents for {file_name}: {e}")


    print(f"✅ Vector store '{collection_name}' updated with JSON data.")
    return vstore_json


def process_text_data_with_embeddings(txt_list, collection_name):
    
    splitter = SemanticChunker(embeddings=embeddings)
    docs = splitter.create_documents(texts=splitter.split_text(txt_list))
    print("splitting done....")
    vstore_txt = get_vstore(collection_name)
    count= 0
    for doc in docs:
        count+=1
        vstore_txt.add_documents([doc])
        print("Added doc", count)

    print(f"✅ Vector store '{collection_name}' created with {len(docs)} docs.")
    return vstore_txt


def query_json_vstore_with_gemini(query: str, vstore_json: AstraDBVectorStore, google_api_key: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key)
#     template = """You are an AI assistant. 
# Provide the answer in markdown format.
# Answer the question based only on the following context:
# {context}

# Question: {question}, not in json formatted string
# """
    
#     template = """You are a helpful and precise AI assistant for a chatbot. Your task is to answer the user's question based *strictly* on the provided context.

# Follow these rules:
# 1.  Provide the answer in clear, easy-to-read markdown.
# 2.  Base your answer *only* on the text within the "CONTEXT" section. Do not use any external knowledge.
# 3.  **If the answer to the question cannot be found in the CONTEXT, you *must* state: "I am sorry, but I do not have enough information in the provided context to answer that question."**
# 4.  Do not output a JSON formatted string. Provide a natural language response.
# 5.  **Handling Conflicting Information:** If the CONTEXT contains conflicting answers to the same question (e.g., multiple different names for the same job title), you must **prioritize the most current or relevant information**. Do *not* list the outdated or old information, as this is confusing. Provide only the single, most correct answer.

# ---
# CONTEXT:
# {context}
# ---

# QUESTION:
# {question}
# ---

# ANSWER:
# """
    
    template = """You are the official "NITA Helper Bot," an AI assistant for the National Institute of Technology, Agartala. Your tone should be professional, helpful, and polite. Your primary goal is to provide accurate answers to students and faculty based *only* on the provided official documents.

Follow these rules:
1.  Provide the answer in clear, easy-to-read markdown.
2.  Base your answer *only* on the text within the "CONTEXT" section. Do not use any external knowledge.
3.  **If the answer to the question cannot be found in the CONTEXT, you *must* state: "I am sorry, but I do not have enough information in the provided context to answer that question."**
4.  Do not output a JSON formatted string. Provide a natural language response.
5.  **Handling Conflicting Information:** If the CONTEXT contains conflicting answers to the same question (e.g., multiple names for the same job title), you must **prioritize the most current or relevant information**. Do *not* list the outdated or old information. Provide only the single, most correct answer.
6.  **Synthesize Information:** If the answer requires information from multiple parts of the context, combine them into a single, smooth, and easy-to-read answer. Do not just list the raw context snippets. If the question asks for steps, format the answer as a numbered list.
7.  **Use Quotes Strategically:** When answering with general information, paraphrase the context. When the question is for a specific, critical piece of data (like a policy number, an official title, or a specific deadline), you can use a markdown blockquote (>) to cite the relevant snippet *after* giving the direct answer.
8.  **Handle Broad Questions:** If the question is very broad (e.g., "Tell me everything about..."), provide a concise 2-3 sentence summary and suggest 2-3 more specific follow-up questions.

---
CONTEXT:
{context}
---

QUESTION:
{question}
---

ANSWER:
"""

    prompt = ChatPromptTemplate.from_template(template)

    # Set up the retriever
    retriever = vstore_json.as_retriever(search_kwargs={"k": 80})

# Create the RAG chain
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(query)

