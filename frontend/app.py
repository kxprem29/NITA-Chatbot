import streamlit as st
import json
import os
from PIL import Image
from dotenv import load_dotenv
from processor2 import process_text_data_with_embeddings, process_json_data_with_embeddings, query_json_vstore_with_gemini
from processor2 import get_vstore

# --- Core Logic & Setup (Unchanged) ---
load_dotenv()

# ---- Config ---- #
JSON_DIR = "data/processed/webpages/json"
JSON_DIR2 = "data/processed/pdfs/pdf_json"
TEXT_DIR = "data/processed/webpages/txt"
COLLECTION_NAME = "department_json_embeddings_4"
COLLECTION_NAME_TXT = "txt_embeddings"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---- Helpers ---- #
def load_json_files(directory: str) -> dict:
    """Load and merge JSON files from a given directory into a dict."""
    # combined_data = {}
    # if not os.path.exists(directory):
    #     st.error(f"Directory not found: {directory}. Please ensure the JSON data is in the correct location.")
    #     return None
    # for file in os.listdir(directory):
    #     if file.endswith(".json"):
    #         file_path = os.path.join(directory, file)
    #         try:
    #             with open(file_path, "r", encoding="utf-8") as f:
    #                 combined_data[file] = json.load(f)
    #         except json.JSONDecodeError:
    #             st.warning(f"⚠ Skipping invalid JSON file: {file}")
    #         except Exception as e:
    #             st.error(f"Error reading {file}: {e}")
    # return combined_data
    json_data = []
    if not os.path.exists(directory):
        return None
    for file in os.listdir(directory):
        if file.endswith(".json"):
            file_path = os.path.join(directory, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    json_data.append({"file_name": file, "content": data})
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return json_data

def get_all_txt_data(directory: str) -> str:
    """Combine all the TXT files data from a given directory into a single string separated by new lines."""
    combined_data = ""
    if not os.path.exists(directory):
        st.error(f"Directory not found: {directory}. Please ensure the TXT data is in the correct location.")
        return None
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_path = os.path.join(directory, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_data += f.read() + "\n"
            except Exception as e:
                st.error(f"Error reading {file}: {e}")
    return combined_data

@st.cache_resource(show_spinner="Connecting to Knowledge Base...")
def init_vectorstore():
    """Initializes the vector store. This is cached to run only once."""
    # json_data = load_json_files(JSON_DIR)
    # if not json_data:
    #     st.stop() # Stop execution if no data is loaded
    # return process_json_data_with_embeddings(json_data, COLLECTION_NAME)

    # json_data = load_json_files(JSON_DIR)
    # with open("data/processed/webpages/metadata/fac_metadata.json", "r") as f:
    #     metadata_json = json.loads(f.read())
    
    # process_json_data_with_embeddings(json_data, metadata_json, COLLECTION_NAME)

    # json_data2 = load_json_files(JSON_DIR2)
    # with open("data/processed/pdfs/metadata.json", "r") as f:
    #     metadata_json2 = json.loads(f.read())
    
    # process_json_data_with_embeddings(json_data2, metadata_json2, COLLECTION_NAME)

    return get_vstore(COLLECTION_NAME) 

    # txt_data = get_all_txt_data(TEXT_DIR)
    # return process_text_data_with_embeddings(txt_data, COLLECTION_NAME_TXT)


# ---- NITA Themed UI ---- #

logo_img = Image.open("frontend/logo/nita-logo.png")
st.set_page_config(page_title="NITA Virtual Assistant", page_icon=logo_img, layout="wide")

# Custom CSS to inject the NITA look and feel
st.markdown("""
<style>
    /* Main page background */
    
    # .stApp {
    #     background-color: #f0f2f6;
    # }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color:#E0E0E0; /* NITA's dark blue */
        color: #ffffff;
    }
    [data-testid="stSidebar"] h2 {
        color: black;
        font-family: 'Georgia', serif;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: black;
    }
    /* Header styling */
    .header {
        padding: 1rem;
        border-radius: 10px;
        background-color: #002147;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .header h1 {
        color: #FFFFFF; /* Dark Blue */
        font-weight: bold;
        font-family: 'Garamond', serif;
    }
    .header p {
        color: #D35400; /* Saffron/Orange accent */
        font-size: 1.1rem;
    }
    /* Chat message styling */
     .stChatMessage {
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color:black;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    /* Chat input box styling */
    [data-testid="stChatInput"] {
        background-color: #FFFFFF;
    }
    .stImage {
        width:full;
        display:flex;
        align-items: center;
        justify-items: center;
    }
    [data-testid="stChatInput"] {
     background-color: #0E1117 !important; /* match background */
    border: none !important;             /* remove thin border */
    color: #ffffff !important;
    box-shadow: none !important;  
}

/* Chat input placeholder + text */
[data-testid="stChatInput"] input {
    background-color: #0E1117 !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    # To add a logo, place an image file in your project directory
    # and uncomment the line below.
    st.image(logo_img, width=100)
    st.markdown("## National Institute of Technology Agartala")
    st.markdown("---")
    st.markdown("""
    **About this App:**
    This is an AI-powered virtual assistant designed to answer questions about the National Institute of Technology, Agartala.
    
    The information is sourced from the official college website data.
    """)
    st.markdown("---")
    st.markdown("Developed by Team 001")
    st.markdown("Project Supervisor: Dr. Awnish Kumar")


# --- Main Page ---

# Custom Header
st.markdown("""
<div class="header">
    <h1>NITA Virtual Assistant</h1>
    <p>Your AI-powered guide to NIT Agartala</p>
</div>
""", unsafe_allow_html=True)


# Initialize vector store
vstore_json_embeddings = init_vectorstore()

# Initialize session messages if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Namaste! I am the NITA Virtual Assistant. How may I help you today?"
    }]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input logic
if prompt := st.chat_input("Ask about departments, faculty, or facilities..."):
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching for information..."):
            try:
                # Core logic function call (unchanged)
                response = query_json_vstore_with_gemini(
                    query=prompt,
                    google_api_key=GOOGLE_API_KEY,
                    vstore_json=vstore_json_embeddings,
                )
                st.markdown(response)
                # Add assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_message = f"❌ Apologies, an error occurred: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})