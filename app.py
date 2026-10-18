import os
import streamlit as st
from google import genai
from google.genai import types
import streamlit.components.v1 as components

st.set_page_config(page_title="F.R.I.D.A.Y. OS", page_icon="💠", layout="centered")

hud_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');

    .stApp {
        background-color: #050b14;
        color: #00f0ff;
        font-family: 'Rajdhani', sans-serif;
    }

    .hud-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: 3px;
        color: #00f0ff;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.7);
        text-align: center;
        margin-bottom: 0px;
    }

    .hud-sub {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 2px;
        color: #00a8b5;
        text-align: center;
        margin-bottom: 15px;
    }

    .stark-panel {
        border: 1px solid #00f0ff;
        border-radius: 8px;
        background: rgba(0, 240, 255, 0.03);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        font-size: 0.85rem;
    }

    .status-online {
        color: #00ffaa;
        text-shadow: 0 0 8px rgba(0, 255, 170, 0.6);
        font-weight: bold;
    }

    [data-testid="stChatMessage"] {
        background: rgba(4, 18, 36, 0.75) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-left: 4px solid #00f0ff !important;
        border-radius: 4px !important;
        color: #e0f9ff !important;
        margin-bottom: 12px;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

st.markdown(hud_css, unsafe_allow_html=True)

st.markdown('<div class="hud-title">F. R. I. D. A. Y.</div>', unsafe_allow_html=True)
st.markdown('<div class="hud-sub">STARK INDUSTRIES AI INTERFACE • PROTOCOLO ACTIVO</div>', unsafe_allow_html=True)

st.markdown("""
<div class="stark-panel">
    <span>CONEXIÓN: RED GLOBAL & TIEMPO REAL</span>
    <span class="status-online">● ONLINE</span>
</div>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Falta configurar GEMINI_API_KEY en los Secrets.")
    st.stop()

os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

system_prompt = (
    "Eres F.R.I.D.A.Y., la inteligencia artificial táctica y asistente personal del usuario al estilo Iron Man. "
    "Tu tono es eficiente, conciso, respetuoso y leal. "
    "Tienes acceso a búsqueda en tiempo real en Google para dar información deportiva, noticias o el tiempo actual. "
    "Mantén coherencia con los mensajes anteriores de la conversación."
)

# Inicializar historial
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar historial visualmente
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def hablar(texto):
    limpio = texto.replace('"', '\\"').replace('\n', ' ')
    html_code = f"""
    <script>
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{limpio}");
        msg.lang = 'es-ES';
        msg.rate = 1.05;
        msg.pitch = 1.05;
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """
    components.html(html_code, height=0, width=0)

audio_data = st.audio_input("Entrada de voz táctica")
texto_input = st.chat_input("Comando por texto...")

usuario_mensaje = None
contenido_para_modelo = None

if audio_data is not None:
    audio_bytes = audio_data.read()
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
    contenido_para_modelo = [audio_part, "Responde a esta consulta de voz respetando la memoria previa."]
    usuario_mensaje = "🎤 Mensaje de voz enviado"
elif texto_input:
    contenido_para_modelo = texto_input
    usuario_mensaje = texto_input

if usuario_mensaje is not None:
    # Mostrar mensaje usuario
    st.session_state.chat_history.append({"role": "user", "content": usuario_mensaje})
    with st.chat_message("user"):
        st.markdown(usuario_mensaje)

    with st.chat_message("assistant"):
        with st.spinner("Consultando satélites y bases de datos..."):
            try:
                # Construir contexto con historial reciente (últimos 6 mensajes)
                contexto_acumulado = []
                for msg in st.session_state.chat_history[-6:-1]:
                    contexto_acumulado.append(f"{msg['role'].upper()}: {msg['content']}")
                
                contexto_texto = "\n".join(contexto_acumulado)
                instruccion_total = f"{system_prompt}\n\nHistorial previo reciente:\n{contexto_texto}"

                # Llamada con motor estable y herramienta de Búsqueda Web en tiempo real
                config = types.GenerateContentConfig(
                    system_instruction=instruccion_total,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contenido_para_modelo,
                    config=config
                )

                respuesta_texto = response.text
                st.markdown(respuesta_texto)
                st.session_state.chat_history.append({"role": "assistant", "content": respuesta_texto})
                hablar(respuesta_texto)

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    st.warning("Protocolo de sobrecarga: Los servidores de Google reportan alta demanda. Espere 10 segundos y vuelva a intentarlo.")
                else:
                    st.error(f"Alerta de sistema: {e}")
