import os
import streamlit as st
from google import genai
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="F.R.I.D.A.Y. OS", page_icon="💠", layout="centered")

# Estilos CSS HUD Stark Industries / Holograma Friday
hud_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');

    /* Fondo general oscuro */
    .stApp {
        background-color: #050b14;
        color: #00f0ff;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Cabecera estilo interfaz Stark */
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: 3px;
        color: #00f0ff;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.7), 0 0 20px rgba(0, 240, 255, 0.4);
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

    /* Panel de estado holográfico */
    .stark-panel {
        border: 1px solid #00f0ff;
        border-radius: 8px;
        background: rgba(0, 240, 255, 0.03);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15), inset 0 0 15px rgba(0, 240, 255, 0.05);
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    .status-online {
        color: #00ffaa;
        text-shadow: 0 0 8px rgba(0, 255, 170, 0.6);
        font-weight: bold;
    }

    /* Mensajes de chat adaptados al HUD */
    [data-testid="stChatMessage"] {
        background: rgba(4, 18, 36, 0.75) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-left: 4px solid #00f0ff !important;
        border-radius: 4px !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.1) !important;
        color: #e0f9ff !important;
        margin-bottom: 12px;
    }

    /* Caja de texto y grabadora */
    .stChatInputContainer, [data-testid="stAudioInput"] {
        border-color: #00f0ff !important;
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.2) !important;
    }

    /* Ocultar barra superior de Streamlit para efecto inmersivo */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

st.markdown(hud_css, unsafe_allow_html=True)

# Encabezado visual
st.markdown('<div class="hud-title">F. R. I. D. A. Y.</div>', unsafe_allow_html=True)
st.markdown('<div class="hud-sub">STARK INDUSTRIES AI INTERFACE • PROTOCOLO ACTIVO</div>', unsafe_allow_html=True)

# Barra de estado táctica
st.markdown("""
<div class="stark-panel">
    <span>NÚCLEO: GEMINI 3.8 FLASH</span>
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
    "Eres F.R.I.D.A.Y., la inteligencia artificial táctica y asistente personal creada por Industrias Stark. "
    "Tu tono es eficiente, conciso, respetuoso, servicial y leal, con un toque sutil de humor ejecutivo. "
    "Trata al usuario como tu creador o superior. Responde de forma precisa y táctica."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Despliegue de mensajes
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Salida de voz nativa en el navegador
def hablar(texto):
    limpio = texto.replace('"', '\\"').replace('\n', ' ')
    html_code = f"""
    <script>
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{limpio}");
        msg.lang = 'es-ES';
        msg.rate = 1.05;
        msg.pitch = 1.08;
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """
    components.html(html_code, height=0, width=0)

# Controles de entrada
audio_data = st.audio_input("Entrada de voz táctica")
texto_input = st.chat_input("Comando por texto...")

prompt_para_enviar = None

if audio_data is not None:
    audio_bytes = audio_data.read()
    prompt_para_enviar = [
        {"mime_type": "audio/wav", "data": audio_bytes},
        "Responde a esta orden de voz de forma ejecutiva como F.R.I.D.A.Y."
    ]
elif texto_input:
    prompt_para_enviar = texto_input

if prompt_para_enviar is not None:
    display_user = "📡 Entrada de audio recibida" if audio_data is not None else texto_input
    st.session_state.chat_history.append({"role": "user", "content": display_user})
    with st.chat_message("user"):
        st.markdown(display_user)

    with st.chat_message("assistant"):
        with st.spinner("Sistemas analizando..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt_para_enviar,
                    config={"system_instruction": system_prompt}
                )
                respuesta_texto = response.text
                st.markdown(respuesta_texto)
                st.session_state.chat_history.append({"role": "assistant", "content": respuesta_texto})
                hablar(respuesta_texto)
            except Exception as e:
                st.error(f"Alerta de sistema: {e}")
