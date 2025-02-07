import streamlit as st

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

# Add the image to the top right corner
st.markdown(
    """
    <img src="https://www.entergy.com/userfiles/logos/EntergyLogo-white.png" class="top-right-image" width="50">
    """,
    unsafe_allow_html=True
)

##st.image("https://www.entergy.com/userfiles/logos/EntergyLogo-white.png", caption="Image Caption", width=300)



st.markdown("""Test Aid - example questions to try:\n 
1.  How were interest rates discussed in last years PSC meetings?\n 
2.  Give examples of hurricane relief preperation plans\n 
3.  Did a change in oil prices effect growth expectations in 2021?\n
""")
                
                
##------- Chat bot code ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
 # echo user input - AkA send to rag
    response = f"You asked: {prompt}"
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
