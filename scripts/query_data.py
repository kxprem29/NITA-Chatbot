import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_astradb.vectorstores import AstraDBVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def create_rag_chain():
    """Connects to an existing vector store and sets up a RAG chain."""
    # 1. Initialize Gemini Embeddings (needed to connect to the store)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    
    # 2. Connect to the existing AstraDB Vector Store
    # Notice we don't call .add_documents() here!
    collection_name = "department_json_embeddings"
    vstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name=collection_name,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_TOKEN,
    )
    retriever = vstore.as_retriever()
    print(f"Successfully connected to vector store '{collection_name}'.")

    # 3. Define the prompt template
    prompt_template = ChatPromptTemplate.from_template(
        """
        Answer the user's question based on the following context:
        {context}

        Question: {question}
        """
    )

    # 4. Initialize the Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
    
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    # 5. Create the RAG chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

if __name__ == "__main__":
    rag_chain = create_rag_chain()
    
    # Loop to ask questions continuously
    while True:
        query = input("\nAsk a question (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        if not query.strip():
            continue
            
        print("\nThinking...")
        response = rag_chain.invoke(query)
        print("\nAnswer:")
        print(response)