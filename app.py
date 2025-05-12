import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from streamlit_float import float_init
from audio_recorder_streamlit import audio_recorder
from tempfile import NamedTemporaryFile

# Inicializa efectos visuales
float_init()

# Estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?"}]

# Estilos personalizados
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
    </style>
""", unsafe_allow_html=True)

# Títulos
st.markdown("<h1>Chatea con el Tutor de voz</h1>", unsafe_allow_html=True)
st.markdown("<h3>Para estudiantes de la CUN</h3>", unsafe_allow_html=True)
st.markdown("<div class='chat-bubble'>Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?</div>", unsafe_allow_html=True)
st.markdown("<div class='circle'></div>", unsafe_allow_html=True)

# Instrucción
st.info("Pulsa el botón rojo para grabar tu pregunta al tutor")

# Botón de grabación de audio
audio_bytes = audio_recorder(pause_threshold=1.0, sample_rate=44100)

# Procesamiento de audio si se graba algo
if audio_bytes:
    # Guardar temporalmente
    with NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        temp_path = f.name

    # Transcribir
    transcript = speech_to_text(temp_path)
    os.remove(temp_path)

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
    else:
        st.markdown(
            "<div class='chat-bubble' style='background-color: #F54242;'>"
            "⚠️ El audio no pudo ser procesado. Por favor, intenta grabar de nuevo."
            "</div>", unsafe_allow_html=True
        )

