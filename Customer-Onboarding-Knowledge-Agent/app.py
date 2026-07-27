import streamlit as st
from agent import get_rag_chain, ask_agent
import os

st.set_page_config(page_title="Customer Onboarding Agent", page_icon="🏢", layout="centered")

st.title("🏢 Customer Onboarding Agent")
st.markdown("Ask me anything about our corporate processes, HR policies, or onboarding steps!")

# Check if vector db exists to prevent errors
if not os.path.exists("./chroma_db"):
    st.error("Vector database not found. Please run `python ingest.py` first.")
    st.stop()

# Initialize the RAG chain in session state to avoid reloading on every UI interaction
if "rag_chain" not in st.session_state:
    with st.spinner("Initializing local AI Agent..."):
        st.session_state.rag_chain = get_rag_chain()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How do I request software access?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Searching corporate documents..."):
            # Get response from the agent
            response = ask_agent(st.session_state.rag_chain, prompt)
            st.markdown(response)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})