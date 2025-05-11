import streamlit as st
from PIL import Image
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init

# Inicializar configuración visual
float_init()

# Estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?"}
    ]
if "recording" not in st.session_state:
    st.session_state.recording = False
if "run_recorder" not in st.session_state:
    st.session_state.run_recorder = False

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #080D18;
    }
    h1, h3 {
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
        color: white;
    }
    .chat-bubble {
        background: linear-gradient(to right, #0F69F5, #3435A1);
        color: white;
        font-size: 18px;
        padding: 16px 24px;
        border-radius: 24px;
        display: inline-block;
        margin-top: 24px;
        max-width: 600px;
        box-shadow: 0 0 12px rgba(0, 137, 255, 0.4);
    }
    .circle {
        margin: 30px auto 10px;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle at center, rgba(0,137,255,0.6), rgba(52,53,161,0.9));
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0,137,255, 0.5); }
        70% { box-shadow: 0 0 0 20px rgba(0,137,255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0,137,255, 0); }
    }
    .mic-button {
        display: flex;
        justify-content: center;
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

# --- TÍTULOS ---
st.markdown("<h1>Chatea con el Tutor de voz</h1>", unsafe_allow_html=True)
st.markdown("<h3>Para estudiantes de la CUN</h3>", unsafe_allow_html=True)

# --- MENSAJE DE INICIO ---
st.markdown("<div style='text-align: center;'><div class='chat-bubble'>Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?</div></div>", unsafe_allow_html=True)

# --- AVATAR ANIMADO ---
st.markdown("<div class='circle'></div>", unsafe_allow_html=True)

# --- BOTÓN DE MICRÓFONO CENTRAL ---
mic_icon = "mic_on_fixed.png" if st.session_state.recording else "mic_off_fixed.png"
mic_path = os.path.join("assets", mic_icon)

col1, col2, col3 = st.columns([4, 1, 4])
with col2:
    st.image(mic_path, width=80)
    if st.button("🎤", key="toggle_mic"):
        st.session_state.recording = not st.session_state.recording
        st.session_state.run_recorder = True

# --- CAPTURAR AUDIO SOLO TRAS CLIC ---
audio_bytes = None
if st.session_state.run_recorder:
    st.session_state.run_recorder = False  # limpiar trigger
    with st.container():
        st.markdown("<div class='hide-recorder'>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(text="", icon_size="0.0001rem")
        st.markdown("</div>", unsafe_allow_html=True)

# --- TRANSCRIPCIÓN Y RESPUESTA ---
if audio_bytes:
    with st.spinner("Transcribiendo..."):
        audio_path = "temp_audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        transcript = speech_to_text(audio_path)
        os.remove(audio_path)

    if transcript:
        st.session_state.messages.append({"role": "user", "content": transcript})
        st.markdown(f"<div class='chat-bubble'>{transcript}</div>", unsafe_allow_html=True)

        with st.spinner("Pensando 🤔..."):
            response = get_answer(st.session_state.messages)

        with st.spinner("Generando audio..."):
            audio_file = text_to_speech(response)
            autoplay_audio(audio_file)
            os.remove(audio_file)

        st.markdown(f"<div class='chat-bubble'>{response}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})

