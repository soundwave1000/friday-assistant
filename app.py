import os
import streamlit as st
from google import genai

# Configuración visual para móvil
st.set_page_config(page_title="F.R.I.D.A.Y.", page_icon="🤖", layout="centered")

st.markdown("### F.R.I.D.A.Y. • Protocolo Activo")

# Lectura de la clave desde Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Falta configurar GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# Configuración obligatoria para claves de autorización europea
os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

# Historial del chat en la sesión
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Instrucción de personalidad de Friday
system_prompt = (
    "Eres F.R.I.D.A.Y., la IA táctica y asistente personal del usuario al estilo Iron Man. "
    "Tu tono es eficiente, conciso, respetuoso y leal. "
    "Ayudas a priorizar el día, responder dudas y estructurar ideas."
)

# Entrada de texto del usuario
if user_prompt := st.chat_input("¿Qué necesita, señor?"):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_prompt,
                config={"system_instruction": system_prompt}
            )
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error en los sistemas: {e}")
