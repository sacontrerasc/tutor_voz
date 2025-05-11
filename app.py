import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Float feature initialization
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hola, soy el tutor IA de la CUN. ¿En que puedo ayudarte?"}
        ]
    # if "audio_initialized" not in st.session_state:
    #     st.session_state.audio_initialized = False

initialize_session_state()

st.markdown("""
<style>
    body {
        background-color: #080D18;
        color: #F7F6F6;
        font-family: sans-serif;
        margin: 0;
        display: flex;
        flex-direction: column; /* Ensure content flows vertically */
        align-items: center;
        min-height: 100vh;
    }

    .chat-container {
        background-color: #080D18;
        width: 80%;
        max-width: 600px;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        margin-top: 20px; /* Add some top margin */
        flex-grow: 1; /* Allow chat container to grow and take available space */
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Messages start from the top */
    }

    .chat-messages {
        background-color: #000000;
        padding: 15px;
        overflow-y: auto;
        flex-grow: 1; /* Messages take up available space */
        display: flex;
        flex-direction: column;
    }

    .message {
        color: #F7F6F6;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 6px;
        clear: both;
        word-break: break-word; /* Prevent long words from breaking layout */
    }

    .user-message {
        background-color: #3435A1;
        float: right;
        text-align: right;
        align-self: flex-end; /* Align user messages to the right */
    }

    .assistant-message {
        background-color: #0D192E;
        float: left;
        text-align: left;
        align-self: flex-start; /* Align assistant messages to the left */
    }

    .chat-input-container {
        background-color: #000000;
        padding: 10px;
        display: flex;
        align-items: center;
        border-top: 1px solid #192645; /* Separator */
    }

    .input-field {
        flex-grow: 1;
        padding: 8px;
        border: none;
        border-radius: 4px;
        background-color: #192645;
        color: #A3AEAD;
    }

    .send-button {
        background-color: #0D192E;
        color: #5A6CBA;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        margin-left: 10px;
    }

   .generating-response {
        color: #A3AEAD;
        padding: 8px;
        margin-left: 10px;
    }

    .chat-visual {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(to right, #0089FF, #3435A1);
        margin-top: 20px;
    }

    /* Float the footer container */
    .footer-container {
        background-color: #000000;
        padding: 10px;
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        z-index: 1000; /* Ensure it's on top */
        display: flex;
        justify-content: center; /* Center the audio recorder */
    }
</style>
""", unsafe_allow_html=True)

st.title("Tutor de Voz IA 🤖")

st.markdown("""<div class="chat-container"><div class="chat-messages">""", unsafe_allow_html=True)

for message in st.session_state.messages:
    role_class = "user-message" if message["role"] == "user" else "assistant-message"
    st.markdown(f"""<div class="message {role_class}">{message["content"]}</div>""", unsafe_allow_html=True)

st.markdown("""</div>""", unsafe_allow_html=True)

# Input area
with st.container():
    col1, col2 = st.columns([5, 1])
    with col1:
        user_prompt = st.text_input("Pregunta algo...", key="user_input", label_visibility="collapsed")
    with col2:
        send_button = st.button("Enviar")

    if send_button and user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.markdown(f"""<div class="message user-message">{user_prompt}</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="chat-input-container">""", unsafe_allow_html=True)
    audio_bytes = audio_recorder() # Removed text_config
    st.markdown("""</div>""", unsafe_allow_html=True)


if audio_bytes:
    with st.spinner("Transcribiendo..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            st.markdown(f"""<div class="message user-message">{transcript}</div>""", unsafe_allow_html=True)
            os.remove(webm_file_path)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("Pensando🤔..."):
        final_response = get_answer(st.session_state.messages)
    with st.spinner("Generando respuesta del audio..."):
        audio_file = text_to_speech(final_response)
        autoplay_audio(audio_file)
    st.markdown(f"""<div class="message assistant-message">{final_response}</div>""", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    os.remove(audio_file)

st.markdown("""<div class="chat-visual"></div></div>""", unsafe_allow_html=True)

# Footer container for the microphone (using fixed positioning in CSS now)
st.markdown("""<div class="footer-container"></div>""", unsafe_allow_html=True)