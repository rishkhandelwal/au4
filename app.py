import streamlit as st
import requests
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Set up the API endpoint
API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://shalini-audio-ov26lo32lq-uc.a.run.app/interact')

def send_request(user_id, text=None, audio=None):
    files = None
    data = {'user_id': user_id}
    if text:
        data['text'] = text
    elif audio:
        files = {'file': ('audio.wav', io.BytesIO(audio), 'audio/wav')}
    try:
        response = requests.post(API_ENDPOINT, data=data, files=files)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        content_type = response.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            return response.json()
        elif 'audio/' in content_type:
            return {'audio': response.content, 'content_type': content_type}
        else:
            return {"response": f"Received unexpected content type: {content_type}"}
    except requests.exceptions.RequestException as e:
        return {"response": f"Error communicating with server: {str(e)}"}

def main():
    st.title("AI shalini Chatbot")
    user_id = st.text_input("Enter your User ID:", value="default_user")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.write("### Chat with shalini")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "audio":
                st.audio(message["content"], format="audio/wav")

    input_method = st.radio("Choose input method:", ("Text", "Audio"))

    if input_method == "Text":
        user_input = st.text_area("Enter your message:")
        if st.button("Send Text"):
            if user_input:
                with st.chat_message("user"):
                    st.markdown(user_input)
                st.session_state.messages.append({"role": "user", "type": "text", "content": user_input})
                with st.spinner("AI is thinking..."):
                    response = send_request(user_id, text=user_input)
                process_response(response)
            else:
                st.warning("Please enter a message before sending.")

    else:  # Audio
        st.write("Record your audio message:")
        audio_file = st.file_uploader("Upload audio file", type=["wav", "mp3"])
        
        if audio_file is not None:
            st.audio(audio_file, format="audio/wav")
            if st.button("Send Audio"):
                audio_bytes = audio_file.read()
                with st.chat_message("user"):
                    st.markdown("Audio message sent")
                    st.audio(audio_bytes, format="audio/wav")
                st.session_state.messages.append({"role": "user", "type": "audio", "content": audio_bytes})
                with st.spinner("Processing audio..."):
                    response = send_request(user_id, audio=audio_bytes)
                process_response(response)
        else:
            st.info("Please upload an audio file to send.")

def process_response(response):
    if 'response' in response:
        with st.chat_message("assistant"):
            st.markdown(response['response'])
        st.session_state.messages.append({"role": "assistant", "type": "text", "content": response['response']})
    elif 'audio' in response:
        with st.chat_message("assistant"):
            st.audio(response['audio'], format=response['content_type'])
        st.session_state.messages.append({"role": "assistant", "type": "audio", "content": response['audio']})

if __name__ == "__main__":
    main()
