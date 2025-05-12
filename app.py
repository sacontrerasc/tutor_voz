import streamlit as st
import os
from PIL import Image
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from streamlit_float import float_init
import wave
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

# Captura de audio
st.info("Activa el micrófono para hablar")
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )
)

# Función para validar duración del audio
def is_audio_long_enough(path, min_duration=0.1):
    try:
        with wave.open(path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return duration >= min_duration
    except Exception as e:
        return False

# Procesamiento del audio si está disponible
if webrtc_ctx.audio_receiver:
    import av
    import numpy as np

    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    if audio_frames:
        audio = audio_frames[0].to_ndarray()
        with NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio.tobytes())
            temp_path = f.name

        if is_audio_long_enough(temp_path):
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
            os.remove(temp_path)
            st.markdown(
                "<div class='chat-bubble' style='background-color: #F54242;'>"
                "⚠️ El audio grabado es demasiado corto. Por favor, habla al menos 0.1 segundos."
                "</div>", unsafe_allow_html=True
            )
