from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
import streamlit as st

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Inicializar cliente de OpenAI
client = OpenAI(api_key=api_key)

# Función para obtener respuesta del modelo GPT
def get_answer(messages):
    system_message = [{"role": "system", "content": "Soy tu tutor IA y estoy para ayudarte, ¿qué necesitas hoy?"}]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content

# Función para convertir voz a texto (STT)
def speech_to_text(audio_data):
    try:
        # Validar tamaño mínimo del archivo para evitar errores de audio corto
        if os.path.getsize(audio_data) < 1000:  # 1KB ≈ 0.1 segundos
            return "El audio es muy corto. Intenta grabar al menos 1 segundo."

        with open(audio_data, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                response_format="text",
                file=audio_file
            )
        return transcript

    except Exception as e:
        return f"Ocurrió un error al procesar el audio: {str(e)}"

# Función para convertir texto a voz (TTS)
def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

# Reproducir automáticamente el audio generado
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
