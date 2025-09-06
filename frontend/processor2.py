from langchain.text_splitter import RecursiveJsonSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_astradb.vectorstores import AstraDBVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_vstore(collection_name: str) -> AstraDBVectorStore:
    """Initialize AstraDB vector store with Gemini embeddings."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY,
    )
    return AstraDBVectorStore(
        embedding=embeddings,
        collection_name=collection_name,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_TOKEN,
    )

def process_json_data_with_embeddings(json_data: dict, collection_name: str) -> AstraDBVectorStore:
    """
    Split JSON data into documents, embed them with Gemini, and store in AstraDB.
    """
    splitter = RecursiveJsonSplitter(max_chunk_size=2000)
    docs = splitter.create_documents(splitter.split_json(json_data))

    vstore_json = get_vstore(collection_name)
    vstore_json.add_documents(docs)

    print(f"✅ Vector store '{collection_name}' created with {len(docs)} docs.")
    return vstore_json

def query_json_vstore_with_gemini(query: str, vstore_json: AstraDBVectorStore, google_api_key: str) -> str:
    """
    Query the AstraDB vector store and generate an answer using Gemini.
    """
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an assistant with access to structured JSON data.
        Answer clearly using the following context:

        {context}

        Question: {question}
        """
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    retriever = vstore_json.as_retriever()

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(query)
