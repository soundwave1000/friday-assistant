import streamlit as st
import google.generativeai as genai

# Configuración visual para móvil
st.set_page_config(page_title="F.R.I.D.A.Y.", page_icon="🤖", layout="centered")

st.markdown("### F.R.I.D.A.Y. • Protocolo Activo")

# Lectura de la clave desde los Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Falta configurar GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

# Configurar la API Key
genai.configure(api_key=api_key)

# Inicializar modelo con personalidad de Friday
system_instruction = (
    "Eres F.R.I.D.A.Y., la IA táctica y asistente personal del usuario al estilo Iron Man. "
    "Tu tono es eficiente, conciso, respetuoso y leal. "
    "Ayudas a priorizar el día, redactar mensajes, responder dudas y estructurar ideas."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# Historial del chat en la sesión
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto del usuario
if user_prompt := st.chat_input("¿Qué necesita, señor?"):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(user_prompt)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error de conexión: {e}")
