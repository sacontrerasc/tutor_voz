import streamlit as st
import os
from PIL import Image
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init

# Inicializar float y sesión
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?"}
        ]
    if "recording" not in st.session_state:
        st.session_state.recording = False

initialize_session_state()

# Estilos CSS
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #080D18 !important;
}
[data-testid="stVerticalBlock"] {
    background-color: transparent !important;
}
h1, h3 {
    font-family: 'Segoe UI', sans-serif;
    text-align: center;
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

# Título superior personalizado
st.markdown("""
<div style='text-align: center; margin-top: 40px; font-family: "Segoe UI", sans-serif;'>
    <h1 style='color: #F7F6F6; font-size: 48px; font-weight: 700;'>Chatea con el Tutor de voz</h1>
    <h3 style='color: #A3AEAD; font-weight: 400; margin-top: -15px;'>Para estudiantes de la CUN</h3>
</div>
""", unsafe_allow_html=True)

# Burbuja de bienvenida
st.markdown("""
<div style='text-align: center;'>
    <div class='chat-bubble'>Hola, soy el tutor IA de la CUN. ¿En qué puedo ayudarte?</div>
</div>
""", unsafe_allow_html=True)

# Avatar
st.markdown("<div class='circle-visual'></div>", unsafe_allow_html=True)

# Cargar imagen del micrófono según estado
mic_filename = "mic_on_fixed.png" if st.session_state.recording else "mic_off_fixed.png"
mic_path = os.path.join("assets", mic_filename)

# Mostrar imagen + botón
st.markdown("<div class='audio-container'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([4, 1, 4])
with col2:
    mic_image = Image.open(mic_path)
    st.image(mic_image, width=80)
    if st.button("🎤", key="mic_button"):
        st.session_state.recording = not st.session_state.recording
st.markdown("</div>", unsafe_allow_html=True)

# Ocultar visual del componente audio_recorder
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
        os.remove(audio_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            st.markdown(f"""<div class="chat-bubble">{transcript}</div>""", unsafe_allow_html=True)

# Respuesta del tutor IA
if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("Pensando 🤔..."):
        final_response = get_answer(st.session_state.messages)
    with st.spinner("Generando audio..."):
        audio_file = text_to_speech(final_response)
        autoplay_audio(audio_file)
        os.remove(audio_file)
    st.markdown(f"""<div class="chat-bubble">{final_response}</div>""", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": final_response})
