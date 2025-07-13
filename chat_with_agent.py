import streamlit as st
from agent_runner import build_dev

dev = build_dev()

st.title("Saeed's Replit AI Dev")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What do you want to build/fix?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = dev.initiate_chat(recipient=dev, message=prompt).chat_history[-1]["content"]
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})