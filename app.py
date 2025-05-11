import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Inicializa elementos flotantes
float_init()

# Inicializa mensajes en sesión
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hola, soy tu tutor. ¿En qué puedo ayudarte?"}
        ]

initialize_session_state()

# CSS personalizado para fondo oscuro y estilo visual
st.markdown("""
<style>
/* Fondo oscuro real para Streamlit */
[data-testid="stAppViewContainer"] {
    background-color: #080D18 !important;
}

/* Bloques verticales sin fondo blanco */
[data-testid="stVerticalBlock"] {
    background-color: transparent !important;
}

/* Título principal */
h1 {
    font-size: 42px;
    font-weight: bold;
    color: #F7F6F6;
    margin-top: 60px;
    text-align: center;
    font-family: 'Segoe UI', sans-serif;
}

/* Burbuja del tutor */
.chat-bubble {
    background: linear-gradient(to right, #0F69F5, #3435A1);
    color: white;
    font-size: 20px;
    font-weight: 500;
    padding: 18px 28px;
    border-radius: 28px;
    display: inline-block;
    box-shadow: 0 0 15px rgba(0, 137, 255, 0.4);
    margin-top: 30px;
    max-width: 700px;
}

/* Avatar animado */
.circle-visual {
    margin: 40px auto 0;
    width: 130px;
    height: 130px;
    border-radius: 50%;
    background: radial-gradient(circle at center, rgba(0,137,255,0.6), rgba(52,53,161,0.9));
    animation: pulse 2s infinite;
}

/* Animación */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0,137,255, 0.5); }
    70% { box-shadow: 0 0 0 20px rgba(0,137,255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0,137,255, 0); }
}
</style>
""", unsafe_allow_html=True)

# Título del sistema
st.markdown("<h1>Tutor de Voz IA</h1>", unsafe_allow_html=True)

# Mensaje inicial del tutor
st.markdown("""
<div style='text-align: center;'>
    <div class='chat-bubble'>Hola, soy tu tutor. ¿En qué puedo ayudarte?</div>
</div>
""", unsafe_allow_html=True)

# Avatar visual animado
st.markdown("<div class='circle-visual'></div>", unsafe_allow_html=True)

# Entrada de audio (micrófono)
audio_bytes = audio_recorder()

# Procesamiento del audio
if audio_bytes:
    with st.spinner("Transcribiendo..."):
        audio_path = "temp_audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        transcript = speech_to_text(audio_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            st.markdown(f"""<div class="chat-bubble">{transcript}</div>""", unsafe_allow_html=True)
            os.remove(audio_path)

# Generar respuesta del tutor IA
if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("Pensando 🤔..."):
        final_response = get_answer(st.session_state.messages)
    with st.spinner("Generando respuesta de audio..."):
        audio_file = text_to_speech(final_response)
        autoplay_audio(audio_file)
    st.markdown(f"""<div class="chat-bubble">{final_response}</div>""", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    os.remove(audio_file)
