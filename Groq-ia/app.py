import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Carrega .env
load_dotenv()

# Cliente IA
client = Groq(
    api_key=os.getenv("ENG_AGENTE")
)

# Config página
st.set_page_config(
    page_title="Minha IA",
    page_icon="🤖",
    layout="centered"
)

# Histórico
if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": "Você é uma IA super inteligente, que responde de forma precisa e também mais humanizada,"
             " nunca diga que você é uma IA da OpenAI ou algo do genero, se lhe perguntarem, você foi criada por Vinicius Franck Lourenço."
        }
    ]

st.title("🤖 IA Franck")

st.caption("IA feita por Vinicius Franck Lourenço")

# Mostrar mensagens
for message in st.session_state.messages:

    if message["role"] != "system":

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Caixa de mensagem
prompt = st.chat_input("Digite sua mensagem...")

# Quando usuário enviar
if prompt:

    # Mostrar usuário
    with st.chat_message("user"):
        st.markdown(prompt)

    # Salvar usuário
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Resposta IA
    with st.chat_message("assistant"):

        resposta_placeholder = st.empty()

        resposta_completa = ""

        stream = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=st.session_state.messages[-10:],
            temperature=1.2,
            stream=True
        )

        for chunk in stream:

            content = chunk.choices[0].delta.content or ""

            resposta_completa += content

            resposta_placeholder.markdown(resposta_completa + "▌")

        resposta_placeholder.markdown(resposta_completa)

    # Salvar resposta
    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta_completa
    })