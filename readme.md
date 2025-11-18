# NITA-CHATBOT

#  RAG-Based Chatbot for NIT Agartala

A Retrieval-Augmented Generation (RAG) based chatbot designed for the  
**National Institute of Technology Agartala (NITA)**.  
The system provides accurate, grounded responses to institutional queries using verified data sourced from the official NITA website.

---

## Features

- Retrieval-Augmented Generation pipeline using **Google Gemini (gemini-2.0-flash)**
- **Semantic embeddings** with HuggingFace `all-MiniLM-L6-v2`
- **AstraDB** vector database for efficient document retrieval
- Recursive web crawler + asynchronous data extraction
- Streamlit-based chat interface with NITA-themed design
- Strict grounding to institutional documents (hallucination-safe)

---

## Architecture Overview

User Query → Query Rewriting (Gemini) → Vector Retrieval (AstraDB)
→ Context Assembly → Response Generation → Streamlit UI

---

## Tech Stack
- **Language:** Python  
- **Frameworks:** Streamlit, aiohttp, BeautifulSoup  
- **Embeddings:** HuggingFace all-MiniLM-L6-v2  
- **Vector Store:** AstraDB  
- **LLM:** Google Gemini 2.0 Flash  
- **Environment Management:** python-dotenv  

---

## Installation 

```bash
pip install -r requirements.txt
```
