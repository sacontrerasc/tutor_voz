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
    st.session_state.messages = [{"role": "assistant", "content": "Hola, soy tu tutor. ¿En qué puedo ayudarte?"}]

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
    .circle {
        margin: 30px auto 10px;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle at center, rgba(0,137,255,0.6), rgba(52,53,161,0.9));
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        max-width: 800px;
        margin: 20px auto;
    }
    .bubble-user {
        align-self: flex-end;
        background-color: #1f2937;
        color: white;
        padding: 12px 20px;
        border-radius: 20px 20px 0px 20px;
        margin: 6px 0;
        max-width: 65%;
        font-size: 16px;
    }
    .bubble-assistant {
        align-self: flex-start;
        background: linear-gradient(to right, #0F69F5, #3435A1);
        color: white;
        padding: 12px 20px;
        border-radius: 20px 20px 20px 0px;
        margin: 6px 0;
        max-width: 80%;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("<h1>Chatea con el Tutor de voz</h1>", unsafe_allow_html=True)
st.markdown("<h3>Para estudiantes de la CUN</h3>", unsafe_allow_html=True)
st.markdown("<div class='circle'></div>", unsafe_allow_html=True)

# Botón de grabación
audio_bytes = audio_recorder(
    text="Pregunta algo", 
    pause_threshold=1.0, 
    sample_rate=44100
)

# Procesamiento del audio
if audio_bytes:
    with NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        temp_path = f.name

    transcript = speech_to_text(temp_path)
    os.remove(temp_path)

    if transcript:
        # Agrega la pregunta del usuario
        st.session_state.messages.append({"role": "user", "content": transcript})

        # Agrega temporalmente "Pensando..." como respuesta provisional
        st.session_state.messages.append({"role": "assistant", "content": "🤔 Pensando..."})

        # Redibuja inmediatamente para mostrar la pregunta y spinner
        st.experimental_rerun()

# Si hay un mensaje de "Pensando...", lo reemplaza con la respuesta real
if len(st.session_state.messages) >= 2 and st.session_state.messages[-1]["content"] == "🤔 Pensando...":
    # Obtener contexto hasta antes del "Pensando..."
    context_messages = st.session_state.messages[:-1]

    # Generar respuesta
    respuesta = get_answer(context_messages)

    # Reemplazar el último mensaje ("Pensando...") con la respuesta real
    st.session_state.messages[-1]["content"] = respuesta

    # Reproducir audio
    audio_file = text_to_speech(respuesta)
    autoplay_audio(audio_file)
    os.remove(audio_file)

    # Redibujar
    st.experimental_rerun()

# Mostrar los mensajes tipo chat
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    clase = "bubble-user" if msg["role"] == "user" else "bubble-assistant"
    st.markdown(f"<div class='{clase}'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
