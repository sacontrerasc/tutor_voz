import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from streamlit_float import float_init
from audio_recorder_streamlit import audio_recorder
from tempfile import NamedTemporaryFile
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

# Inicializa efectos visuales
float_init()

# Estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hola, soy tu tutor. ¿En qué puedo ayudarte?"}]
    st.session_state.pending_user_msg = None
    st.session_state.awaiting_response = False

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
        border-radius: 20px;
        margin: 6px 0;
        max-width: 80%;
        font-size: 16px;
    }
    .bubble-assistant {
        align-self: flex-start;
        background: linear-gradient(to right, #0F69F5, #3435A1);
        color: white;
        padding: 12px 20px;
        border-radius: 20px;
        margin: 6px 0;
        max-width: 80%;
        font-size: 16px;
    }
    .mic-button {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px auto;
        padding: 12px 20px;
        background-color: transparent;
        border: none;
        font-size: 18px;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("<h1>Chatea con el Tutor de voz</h1>", unsafe_allow_html=True)
st.markdown("<h3>Para estudiantes de la CUN</h3>", unsafe_allow_html=True)
st.markdown("<div class='circle'></div>", unsafe_allow_html=True)

# Botón de grabación
with st.container():
    st.markdown("<div class='mic-button'>Pregunta algo...</div>", unsafe_allow_html=True)
    audio_bytes = audio_recorder(icon_size="2x")

# Procesamiento del audio
if audio_bytes:
    with NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        temp_path = f.name

    transcript = speech_to_text(temp_path)
    os.remove(temp_path)

    if transcript:
        # Almacena la pregunta y muestra el mensaje "Pensando..."
        st.session_state.messages.append({"role": "user", "content": transcript})
        st.session_state.messages.append({"role": "assistant", "content": "🧠 Pensando..."})
        st.session_state.pending_user_msg = transcript
        st.session_state.awaiting_response = True

        # Fuerza redibujo
        raise RerunException(get_script_run_ctx())

# Si hay respuesta pendiente, la genera y reemplaza "Pensando..."
if st.session_state.awaiting_response and st.session_state.pending_user_msg:
    with st.spinner("Procesando..."):
        response = get_answer(st.session_state.messages[:-1])  # Excluye "Pensando..."
        st.session_state.messages[-1] = {"role": "assistant", "content": response}

        audio_file = text_to_speech(response)
        autoplay_audio(audio_file)
        os.remove(audio_file)

        st.session_state.awaiting_response = False
        st.session_state.pending_user_msg = None

        # Redibuja para mostrar respuesta actualizada
        raise RerunException(get_script_run_ctx())

# Visualización del chat
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    clase = "bubble-user" if msg["role"] == "user" else "bubble-assistant"
    st.markdown(f"<div class='{clase}'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

