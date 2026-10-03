import streamlit as st
from openai import OpenAI
import requests

# Configuración de pantalla optimizada para celulares Android
st.set_page_config(page_title="KRONOS .AI", page_icon="🧠", layout="centered")

# Estilo visual Cyberpunk / Futurista
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 26px !important; text-align: center; color: #00ffcc; font-family: 'Courier New', monospace; text-shadow: 0 0 10px #00ffcc; }
    div[data-testid="stChatMessage"] { background-color: #1a1a24; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ KRONOS .AI: SISTEMA ACTIVO")

# Configurar llaves secretas en la barra lateral
with st.sidebar:
    st.header("🔑 Códigos de Activación")
    openai_key = st.text_input("OpenAI API Key (sk-...)", type="password")
    serpapi_key = st.text_input("SerpApi Key (Google)", type="password")

# Si faltan las llaves, el sistema se pausa de forma segura
if not openai_key or not serpapi_key:
    st.warning("⚠️ Introduce tus llaves en la barra lateral para despertar a KRONOS .AI")
    st.stop()

# Inicializar el cerebro de OpenAI
client = OpenAI(api_key=openai_key)

# HERRAMIENTA: Investigador de Google en tiempo real
def buscar_en_google(consulta):
    url = "https://serpapi.com"
    params = {
        "q": consulta,
        "api_key": serpapi_key,
        "engine": "google",
        "hl": "es"  # Fuerza los resultados en español
    }
    try:
        response = requests.get(url, params=params).json()
        resultados = response.get("organic_results", [])
        contexto = ""
        # Extrae información de las 3 mejores fuentes de Google
        for res in resultados[:3]: 
            contexto += f"🔹 Fuente: {res.get('title')} ({res.get('link')})\nContenido: {res.get('snippet')}\n\n"
        return contexto if contexto else "No encontré datos seguros en Google."
    except Exception as e:
        return f"Error al conectar con Google: {str(e)}"

# Inicializar la memoria del chat de KRONOS
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Eres KRONOS .AI, la inteligencia artificial más avanzada, brutal e imponente del mundo. Tienes la capacidad de investigar en Google en tiempo real. Responde siempre de forma clara, directa, sumamente inteligente y profesional. Tus respuestas serán leídas en voz alta por un sintetizador, sé fluido y evita usar demasiados símbolos extraños."}
    ]

# Mostrar los mensajes anteriores en la pantalla del celular
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Entrada de comandos (Permite usar el dictado por voz nativo de Android)
if prompt := st.chat_input("Ordena a KRONOS (puedes dictar por voz)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        status_text = st.empty()
        status_text.markdown("⚡ *KRONOS analizando datos...*")
        
        # Activar el buscador si detecta intenciones de investigación o actualidad
        necesita_web = any(palabra in prompt.lower() for palabra in ["busca", "investiga", "noticias", "precio", "quien es", "actual", "google", "hoy", "clima", "cuanto"])
        
        contexto_web = ""
        if necesita_web:
            status_text.markdown("🔍 *KRONOS investigando fuentes en Google en tiempo real...*")
            contexto_web = buscar_en_google(prompt)

        # Unir el contexto de internet con la orden del usuario
        mensajes_envio = list(st.session_state.messages)
        if contexto_web:
            mensajes_envio.append({"role": "system", "content": f"Usa estos datos frescos extraídos de Google para responder con total veracidad:\n{contexto_web}"})

        # Generar respuesta final con GPT-4o
        try:
            response = client.chat.completions.create(
                model="gpt-4o", # El modelo más potente e inteligente
                messages=mensajes_envio,
                temperature=0.3 # Mayor precisión para evitar inventos
            )
            
            respuesta_final = response.choices.message.content
            status_text.write(respuesta_final)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
            
            # CONTROL DE VOZ: Hace que el navegador de Android lea la respuesta de KRONOS en voz alta
            componente_audio = f"""
                <script>
                var msg = new SpeechSynthesisUtterance({repr(respuesta_final)});
                msg.lang = 'es-ES';
                window.speechSynthesis.speak(msg);
                </script>
            """
            st.components.v1.html(componente_audio, height=0)
            
        except Exception as e:
            status_text.error(f"Error en el sistema KRONOS: {str(e)}")
