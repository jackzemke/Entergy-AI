# RAG/streamlit/app.py
import streamlit as st
import requests  # We'll use requests to call the API

# URL of your FastAPI endpoint
API_URL = "http://127.0.0.1:8000/ask"

st.title("Entergy PSC Finder")

st.markdown(
    """
    <style>
    .top-right-image {
        position: fixed;
        top: 0;
        right: 0;
        z-index: 999;
        margin: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <img src="https://www.entergy.com/userfiles/logos/EntergyLogo-white.png" class="top-right-image" width="50">
    """,
    unsafe_allow_html=True
)

st.markdown("""Test Aid - example questions to try:
1. How were interest rates discussed in last years PSC meetings?
2. Give examples of hurricane relief preparation plans.
3. Did a change in oil prices affect growth expectations in 2021?
""")

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages in the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture new input from the user
if prompt := st.chat_input("Ask a question"):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Call the FastAPI endpoint with the question
    try:
        response = requests.post(API_URL, json={"question": prompt})
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        answer = data.get("response", "No answer returned.")
    except Exception as e:
        answer = f"Error: {e}"
    
    # Process and display the answer
    answer_text = str(answer).replace('\\n', '\n')
    
    with st.chat_message("assistant"):
        st.markdown(answer_text)
    st.session_state.messages.append({"role": "assistant", "content": answer_text})