import streamlit as st
import requests

# URL of your FastAPI endpoint
API_URL = "http://127.0.0.1:8000/ask"

# Set page config
st.set_page_config(page_title="Entergy PSC Finder", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp {max-width: 1200px; margin: 0 auto;}
    .main {background-color: #f5f7f9;}
    .header {color: #2d5986; padding-bottom: 20px; border-bottom: 2px solid #e6e6e6;}
    .filter-badge {background-color: #f0f2f6; border-radius: 4px; padding: 3px 8px; font-size: 0.8rem;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='header'>Entergy PSC Finder</h1>", unsafe_allow_html=True)

st.sidebar.image("entergy_logo.png", width=150)

# Sidebar filters
with st.sidebar:
    st.header("Search Filters")
    select_all = st.checkbox("Select All", value=True)
    
    # State filters
    filter_la = st.checkbox("Louisiana", value=select_all)
    filter_tx = st.checkbox("Texas", value=select_all)
    filter_ms = st.checkbox("Mississippi", value=select_all)
    filter_ar = st.checkbox("Arkansas", value=select_all)
    filter_no = st.checkbox("New Orleans", value=select_all)
    
    st.caption("Filters determine which state transcripts to search")

# Example questions
with st.expander("Example Questions"):
    st.info("""
    - How were interest rates discussed in last year's PSC meetings?
    - Give examples of hurricane relief preparation plans.
    - Did a change in oil prices affect growth expectations in 2021?
    """)

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input and processing
if prompt := st.chat_input("Ask a question about PSC meetings..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process filters
    filters_applied = []
    if filter_la: filters_applied.append("Louisiana")
    if filter_tx: filters_applied.append("Texas")
    if filter_ms: filters_applied.append("Mississippi")
    if filter_ar: filters_applied.append("Arkansas")
    if filter_no: filters_applied.append("New Orleans")
    
    if not filters_applied:
        filters_applied = ["Louisiana", "Texas", "Mississippi", "Arkansas", "New Orleans"]
    
    # Display thinking indicator
    with st.spinner("Searching transcripts..."):
        try:
            response = requests.post(API_URL, json={"question": prompt, "state": filters_applied[0]})
            response.raise_for_status()
            data = response.json()
            answer = data.get("response", "No answer found.")
        except Exception as e:
            answer = f"Error: {e}"
    
    # Display response
    with st.chat_message("assistant"):
        st.markdown(f"*Searching in: {', '.join(filters_applied)}*")
        st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": f"*Searching in: {', '.join(filters_applied)}*\n\n{answer}"})