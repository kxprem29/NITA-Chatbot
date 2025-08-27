import streamlit as st
import requests
import json

# Define the URL of your FastAPI backend
BACKEND_URL = "http://localhost:8000/chat"

# Set the title for the Streamlit app
st.set_page_config(page_title="RAG Chatbot UI")
st.title("📚 RAG-Powered Chatbot")
st.info("Ask me questions about the documents I've been trained on!")

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What do you want to know?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Send the user's prompt to the backend API
                payload = {"user_query": prompt}
                response = requests.post(
                    BACKEND_URL,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()  # Raise an exception for bad status codes
                
                # Get the response from the backend
                assistant_response = response.json().get("response")
                st.markdown(assistant_response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except requests.exceptions.RequestException as e:
                error_message = f"Failed to connect to backend. Please ensure the backend server is running.\n\nError: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


# To run the Streamlit app:
# Navigate to the 'frontend' directory in your terminal and run:
# streamlit run app.py