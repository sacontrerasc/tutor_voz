import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from streamlit.components.v1 import html

# Inicializa flotantes
float_init()

# Inicializa sesión
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?"}
        ]
    if "recording" not in st.session_state:
        st.session_state.recording = False
    if "toggle_flag" not in st.session_state:
        st.session_state.toggle_flag = False

initialize_session_state()

# CSS personalizado
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #080D18 !important;
}
[data-testid="stVerticalBlock"] {
    background-color: transparent !important;
}
h1 {
    font-size: 42px;
    font-weight: bold;
    color: #F7F6F6;
    margin-top: 60px;
    text-align: center;
    font-family: 'Segoe UI', sans-serif;
}
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
.circle-visual {
    margin: 40px auto 0;
    width: 130px;
    height: 130px;
    border-radius: 50%;
    background: radial-gradient(circle at center, rgba(0,137,255,0.6), rgba(52,53,161,0.9));
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0,137,255, 0.5); }
    70% { box-shadow: 0 0 0 20px rgba(0,137,255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0,137,255, 0); }
}
.audio-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
}
.hide-recorder audio, .hide-recorder div {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    width: 0px !important;
}
</style>
""", unsafe_allow_html=True)

# Título y bienvenida
st.markdown("<h1>Tutor de Voz IA</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center;'>
    <div class='chat-bubble'>Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?</div>
</div>
""", unsafe_allow_html=True)
st.markdown("<div class='circle-visual'></div>", unsafe_allow_html=True)

# Selecciona imagen según estado
mic_img = "mic_on_fixed.png" if st.session_state.recording else "mic_off_fixed.png"

# Mostrar botón HTML con imagen central
html(f"""
    <style>
    .mic-button {{
        background: none;
        border: none;
        cursor: pointer;
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }}
    .mic-button img {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        transition: transform 0.2s;
    }}
    .mic-button img:hover {{
        transform: scale(1.1);
    }}
    </style>
    <form method="post">
        <button class="mic-button" name="toggle_recording">
            <img src="https://raw.githubusercontent.com/sacontrerasc/tutor_voz/main/assets/{mic_img}" alt="Mic">
        </button>
    </form>
""", height=130)

# Manejar evento del botón
if st.session_state.get("toggle_flag", False) is False and "toggle_recording" in st.experimental_get_query_params():
    st.session_state.recording = not st.session_state.recording
    st.session_state.toggle_flag = True
else:
    st.session_state.toggle_flag = False

# Grabación (oculta)
audio_bytes = None
if st.session_state.recording:
    with st.container():
        st.markdown("<div class='hide-recorder'>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(text="", icon_size="0.0001rem")
        st.markdown("</div>", unsafe_allow_html=True)

# Transcripción
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

# Respuesta IA
if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("Pensando 🤔..."):
        final_response = get_answer(st.session_state.messages)
    with st.spinner("Generando audio..."):
        audio_file = text_to_speech(final_response)
        autoplay_audio(audio_file)
    st.markdown(f"""<div class="chat-bubble">{final_response}</div>""", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    os.remove(audio_file)
