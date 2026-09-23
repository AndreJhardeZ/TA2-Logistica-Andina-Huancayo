import streamlit as st
from groq import Groq

# Configuración inicial de Streamlit
st.set_page_config(page_title="Logística Andina Huancayo", page_icon="🚛", layout="wide")
st.title("🚛 Logística Andina Huancayo - Asistente Virtual & Herramientas")

# Obtener la API Key
groq_api_key = st.sidebar.text_input("Ingrese su Groq API Key:", type="password")

if not groq_api_key:
    st.warning("Por favor, ingrese su clave API de Groq en la barra lateral para continuar.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Pestañas principales
tab1, tab2 = st.tabs(["🤖 Chatbot Logístico", "🎙️ Transcriptor de Voz"])

# --- TAB 1: CHATBOT CON RESTRICCIONES Y MEMORIA ---
with tab1:
    st.header("Asistente Virtual de Envíos y Fletes")

    # System Role y Guardrails
    SYSTEM_PROMPT = """
    Eres el asistente virtual oficial de 'Logística Andina Huancayo'. 
    Tu único propósito es responder dudas sobre servicios logísticos, fletes, seguimiento de envíos, cotizaciones y cobertura regional.
    
    RESTRICCIÓN DE DOMINIO (GUARDRAIL):
    Si el usuario te pregunta sobre cualquier tema ajeno a la logística, transporte, envíos, o 'Logística Andina Huancayo' (por ejemplo: cocina, deportes, programación, cultura general, etc.), responde amablemente:
    'Lo siento, solo puedo responder consultas sobre fletes, envíos y servicios logísticos de Logística Andina Huancayo.'
    """

    # Inicializar memoria de chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Mostrar historial de chat en la interfaz (excluyendo el system prompt)
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Captura de entrada del usuario
    if user_input := st.chat_input("¿En qué puedo ayudarte con tu envío?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Respuesta de Groq
        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    temperature=0.3
                )
                bot_reply = response.choices[0].message.content
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Error al conectar con la API: {e}")

# --- TAB 2: TRANSCRIPTOR DE AUDIO (WHISPER) ---
with tab2:
    st.header("Transcriptor de Notas de Voz")
    st.write("Sube una nota de voz (.mp3, .wav, .ogg) para convertirla a texto.")

    uploaded_file = st.file_uploader("Cargar archivo de audio", type=["mp3", "wav", "ogg"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")
        
        if st.button("Transcribir Audio"):
            with st.spinner("Procesando audio con Whisper..."):
                try:
                    # Enviar archivo directamente a la API de Whisper en Groq
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, uploaded_file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="text",
                        language="es"
                    )
                    st.success("Transcripción completada con éxito:")
                    st.text_area("Resultado de la Transcripción:", transcription, height=150)
                except Exception as e:
                    st.error(f"Error al transcribir el audio: {e}")