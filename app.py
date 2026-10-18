import os
import streamlit as st
from google import genai
import streamlit.components.v1 as components

st.set_page_config(page_title="F.R.I.D.A.Y.", page_icon="🤖", layout="centered")

st.markdown("### F.R.I.D.A.Y. • Protocolo de Voz Activo")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Falta configurar GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

system_prompt = (
    "Eres F.R.I.D.A.Y., la IA táctica y asistente personal del usuario al estilo Iron Man. "
    "Tu tono es eficiente, conciso, respetuoso y leal. "
    "Dado que muchas respuestas se leerán en voz alta, sé breve, directa y natural al hablar. "
    "Evita usar símbolos complejos, asteriscos excesivos o tablas a menos que sea imprescindible."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función para reproducir la voz en el navegador del móvil
def hablar(texto):
    # Escapar comillas para evitar errores de sintaxis en JavaScript
    limpio = texto.replace('"', '\\"').replace('\n', ' ')
    html_code = f"""
    <script>
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{limpio}");
        msg.lang = 'es-ES';
        msg.rate = 1.05;
        msg.pitch = 1.1;
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """
    components.html(html_code, height=0, width=0)

# Entrada por voz con el grabador integrado
audio_data = st.audio_input("Hablar con Friday (Toca el micrófono)")

# Entrada por texto convencional
texto_input = st.chat_input("O escribe aquí...")

prompt_para_enviar = None

if audio_data is not None:
    # Si se grabó una nota de voz
    audio_bytes = audio_data.read()
    prompt_para_enviar = [
        {"mime_type": "audio/wav", "data": audio_bytes},
        "Responde a mi consulta de voz siguiendo tu protocolo de Friday."
    ]
elif texto_input:
    # Si se escribió texto
    prompt_para_enviar = texto_input

if prompt_para_enviar is not None:
    # Registro del mensaje del usuario
    display_user = "🎤 Mensaje de voz enviado" if audio_data is not None else texto_input
    st.session_state.chat_history.append({"role": "user", "content": display_user})
    with st.chat_message("user"):
        st.markdown(display_user)

    with st.chat_message("assistant"):
        with st.spinner("Procesando audio..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt_para_enviar,
                    config={"system_instruction": system_prompt}
                )
                respuesta_texto = response.text
                st.markdown(respuesta_texto)
                st.session_state.chat_history.append({"role": "assistant", "content": respuesta_texto})
                
                # Friday habla por los altavoces del móvil
                hablar(respuesta_texto)
                
            except Exception as e:
                st.error(f"Error en los sistemas: {e}")
