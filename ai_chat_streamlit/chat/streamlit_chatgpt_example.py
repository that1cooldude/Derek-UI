from ai_chat_streamlit.chat.model import ChatGPTModel
import streamlit as st
import os

st.title("ChatGPT-like clone")

client = ChatGPTModel(api_key=os.environ.get("OPENAI_API_KEY"))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.stream(st.session_state.messages)
        response = st.write_stream(stream)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
