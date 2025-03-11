import streamlit as st
import requests

# URL of your FastAPI endpoint
API_URL = "http://127.0.0.1:8000/ask"

# Set page config
st.set_page_config(page_title="Entergy PSC Finder", layout="wide")


#Check pop-up
if "popup_shown" not in st.session_state:
    st.session_state.popup_shown = False

# Define the dialog function for the popup
@st.dialog("Welcome to Entergy PSC RAG Chat", width="large")
def info_popup():
    st.write("### Hi, my name is REGGIE! (REGulatory Governance Inquiry Engine)")
    st.write("""
    Use the chatbox below to search through PSC meeting transcripts across multiple states dating back to 2021.
    
    **How to use:**
    1. Select the states you want to search in the sidebar
    2. Type your question in the chat input
    3. View the response based on relevant transcript sections
    
    You can reopen this information anytime by clicking the '?' button.
    """)
    if st.button("Got it!"):
        st.session_state.popup_shown = True
        st.rerun()



# Custom CSS
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #0f0f0f !important;
        color: #f1f1f1 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #181818 !important;
        color: #f1f1f1 !important;
    }
    [data-testid="stHeader"] {
        background-color: #0f0f0f !important;
    }
    [data-testid="block-container"] {
        max-width: 100% !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
    }
    .title-text {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: bold;
    }
    .examples {
        background-color: #1e1e1e !important;
        border-left: 4px solid #4CAF50 !important;
        padding: 1rem !important;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='header'>Entergy PSC RAG Chat</h1>", unsafe_allow_html=True)

st.sidebar.image("entergy_logo.png", width=150)



# Sidebar filters
with st.sidebar:
    if st.button("?", help="Show information", key="help_button_sidebar"):
        info_popup()

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
    - Summarize the discussions on gas prices as a result of the Russian invasion of Ukraine.
    """)


# Show the popup on first visit
if not st.session_state.popup_shown:
    info_popup()



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
            response = requests.post(API_URL, json={"question": prompt, "states": filters_applied})            
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
