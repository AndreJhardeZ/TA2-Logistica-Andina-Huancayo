import streamlit as st
from groq import Groq

# Configuración de la página
st.set_page_config(page_title="Logística Andina Huancayo", page_icon="🚚", layout="wide")

# Título Principal
st.title("🚚 Logística Andina Huancayo - Asistente Virtual & Herramientas")

# Menú lateral para la API Key
st.sidebar.header("Configuración")
api_key = st.sidebar.text_input("Ingrese su Groq API Key:", type="password")

if not api_key:
    st.info("Por favor, ingrese su API Key de Groq en la barra lateral para continuar.")
    st.stop()

# Inicializar cliente de Groq
client = Groq(api_key=api_key)

# Crear pestañas principales
tab1, tab2 = st.tabs(["🤖 Chatbot Logístico", "🎙️ Transcriptor de Voz"])

# ==========================================
# PESTAÑA 1: CHATBOT LOGÍSTICO
# ==========================================
with tab1:
    st.header("Asistente Virtual de Envíos y Fletes")
    
    # System Prompt con Guardrail (Restricción estricta de tema)
    SYSTEM_PROMPT = """
    Eres el Asistente Virtual oficial de 'Logística Andina Huancayo'. 
    Tu único propósito es atender consultas relacionadas con servicios de transporte, fletes, seguimiento de envíos, tarifas, rutas (Lima-Huancayo y anexos) y atención de reclamos logísticos.
    
    REGLA DE GUARDRAIL OBLIGATORIA:
    Si el usuario pregunta sobre cualquier tema ajeno a la logística, transporte o envíos de la empresa (por ejemplo: cocina, recetas, fútbol, noticias generales, tareas escolares, etc.), debes responder educada y cortésmente indicando que solo estás capacitado para atender consultas sobre fletes y envíos de Logística Andina Huancayo.
    """

    # Inicializar el historial del chat en session_state (Memoria)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Contenedor con altura fija y scroll para que los mensajes siempre queden arriba
    chat_container = st.container(height=500)

    # Mostrar todos los mensajes anteriores DENTRO del contenedor
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # La caja de entrada se coloca AFUERA del contenedor, asegurando que quede siempre abajo
    if prompt := st.chat_input("¿En qué puedo ayudarte con tu envío?"):
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Mostrar mensaje del usuario dentro del contenedor
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Preparar el contexto completo para la API
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        # Generar respuesta y mostrarla dentro del contenedor
        with chat_container:
            with st.chat_message("assistant"):
                try:
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=api_messages,
                        temperature=0.3
                    )
                    bot_reply = response.choices[0].message.content
                    st.markdown(bot_reply)
                    
                    # Guardar respuesta en la memoria
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    st.error(f"Error al conectar con la API: {e}")

# ==========================================
# PESTAÑA 2: TRANSCRIPTOR DE VOZ (WHISPER)
# ==========================================
with tab2:
    st.header("Transcriptor de Notas de Voz")
    st.write("Sube una nota de voz o audio de coordinación logística para transcribirla automáticamente.")
    
    uploaded_file = st.file_uploader("Selecciona un archivo de audio (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file)
        if st.button("Transcribir Audio"):
            with st.spinner("Procesando transcripción con Whisper..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, uploaded_file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="text"
                    )
                    st.success("Transcripción completada:")
                    st.text_area("Resultado:", value=transcription, height=150)
                except Exception as e:
                    st.error(f"Error durante la transcripción: {e}")
