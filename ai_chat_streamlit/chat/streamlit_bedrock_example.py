from ai_chat_streamlit.chat.model import ChatBedrockModel
import streamlit as st


st.title("Bedrock Chat")

client = ChatBedrockModel(credentials_profile_name="default",
                          model_id="anthropic.claude-3-sonnet-20240229-v1:0")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        print(message["content"])
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
