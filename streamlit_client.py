import streamlit as st
import requests

st.title("Chat with Llama3.1")

# Function to send user input to the FastAPI endpoint and get response
def send_message(user_input):
    response = requests.post("http://localhost:8000/chat", json={"message": user_input}, stream=True)
    return response


if "history" not in st.session_state:
    st.session_state.history = []

def add_message(content, sender):
    if sender == "user":
        st.session_state.history.append({
            "type": "user",
            "content": f"<div style='background-color: #E8F0FE; color: #000000; padding: 10px; border-radius: 10px;'><b>You:</b> {content}</div>"
        })
    else:
        st.session_state.history.append({
            "type": "bot",
            "content": f"<div style='background-color: #F1F8E9; color: #000000; padding: 10px; border-radius: 10px;'><b>Llama3.1:</b> {content}</div>"
        })

for message in st.session_state.history:
    st.markdown(message["content"], unsafe_allow_html=True)
    st.write("")  # Add space between messages


user_input = st.chat_input("You: ")

# Process the user input
if user_input:
    # Display user message
    add_message(user_input, "user")
    st.markdown(f"<div style='background-color: #E8F0FE; color: #000000; padding: 10px; border-radius: 10px;'><b>You:</b> {user_input}</div>", unsafe_allow_html=True)
    st.write("")  # Add space after user message

  
    response = send_message(user_input)

    # Stream and display bot response
    bot_response = ""
    bot_response_placeholder = st.empty()

    buffer = bytearray()
    for chunk in response.iter_content(chunk_size=1024):
        buffer.extend(chunk)
        try:
            decoded_chunk = buffer.decode("utf-8")
            bot_response += decoded_chunk
            buffer = bytearray()
            bot_response_placeholder.markdown(f"<div style='background-color: #F1F8E9; color: #000000; padding: 10px; border-radius: 10px;'><b>Llama3.1:</b> {bot_response}</div>", unsafe_allow_html=True)
        except UnicodeDecodeError:
            continue

    add_message(bot_response, "bot")
    st.write("")  
