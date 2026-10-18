import streamlit as st
from google import genai
from google.genai import types

# Configuración visual de la página
st.set_page_config(page_title="FRIDAY OS", page_icon="⚡", layout="centered")

# Estilo HUD futurista (Estética Iron Man)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #00d2ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚡ F.R.I.D.A.Y.")
st.caption("Sistema de Asistencia Táctico Personal - Online")

# Inicializar cliente de Gemini utilizando los Secrets de Streamlit
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error(
        "Error crítico: No se ha configurado la API Key de Gemini en los Secrets"
        " de Streamlit."
    )
    st.stop()

# Instrucción de sistema para darle la personalidad de FRIDAY
system_prompt = """
Eres FRIDAY, un sistema operativo de asistencia personal altamente avanzado, 
inspirado en la inteligencia artificial de Tony Stark. 
Tu tono es eficiente, profesional, ligeramente irónico y siempre leal a tu usuario.
Responde de forma concisa, inteligente y con un toque tecnológico.
"""

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe una orden para FRIDAY..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Configurar chat con Gemini
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt, temperature=0.7
            ),
        )

        response = chat.send_message(prompt)
        bot_response = response.text

    except Exception as e:
        bot_response = f"Error en los sistemas, jefe: {e}"

    with st.chat_message("assistant"):
        st.markdown(bot_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_response}
    )