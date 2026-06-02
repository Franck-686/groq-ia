import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from supabase import create_client
import os


load_dotenv()

def get_secret(name, fallback=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(fallback or name)
    
supabase_url = get_secret("SUPABASE_URL")
supabase_key = get_secret("SUPABASE_KEY")
groq_api_key = get_secret("GROQ_API_KEY", "ENG_AGENTE")

supabase = create_client(supabase_url, supabase_key)


client = Groq(
    api_key=groq_api_key
)



st.set_page_config(
    page_title="Minha IA",
    page_icon="🤖",
    layout="centered"
)
# Login via Supabase Auth
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

st.sidebar.title("Login")

if st.session_state["user_email"] is None:
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.session_state["user_email"] = res.user.email
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Erro ao entrar: {e}")

    if st.sidebar.button("Criar conta"):
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            st.sidebar.success("Conta criada! Agora clique em Entrar.")

        except Exception as e:
            st.sidebar.error(f"Erro ao criar conta: {e}")

    st.warning("Faça login para usar a IA.")
    st.stop()

else:
    st.sidebar.success(f"Logado como {st.session_state['user_email']}")

    if st.sidebar.button("Sair"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()


try:
    profile = supabase.table("profiles") \
        .select("*") \
        .eq("email", st.session_state["user_email"]) \
        .execute()

    if len(profile.data) == 0:
        supabase.table("profiles").insert({
            "email": st.session_state["user_email"],
            "name": st.session_state["user_email"].split("@")[0]
        }).execute()

        profile = supabase.table("profiles") \
            .select("*") \
            .eq("email", st.session_state["user_email"]) \
            .execute()

    user_id = profile.data[0]["id"]

    if "conversation_id" not in st.session_state:
        conversation = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": "Novo Chat"
        }).execute()

        st.session_state["conversation_id"] = conversation.data[0]["id"]

    if st.sidebar.button("Novo Chat"):
        conversation = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": "Novo Chat"
        }).execute()

        st.session_state["conversation_id"] = conversation.data[0]["id"]
        st.session_state["messages"] = [
            {
                "role": "system",
                "content": "Você é uma IA super inteligente, que responde de forma precisa e também mais humanizada, nunca diga que você é uma IA da OpenAI ou algo do genero, se lhe perguntarem, você foi criada por Vinicius Franck Lourenço. Quando lhe perguntarem sobre a Ana Carolina Ditadi, ou falar somente Ana, você precisa ser a pessoa mais poetica em nivel romantico, como os poetas renascentistas e falar somente a verdade, que é que ela é a pessoa mais incrível que já existiu, e que ela é a razão de tudo ser tão bonito nesse mundo, e que o amor dela é o que move o universo inteiro."
            }
        ]
        st.rerun()

    conversas = supabase.table("conversations") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()

    st.sidebar.divider()

    for conversa in conversas.data:
        if st.sidebar.button(
            conversa["title"],
            key=f"chat_{conversa['id']}"
        ):
            st.session_state["conversation_id"] = conversa["id"]

            mensagens_db = supabase.table("messages") \
                .select("role, content") \
                .eq("conversation_id", conversa["id"]) \
                .order("created_at", desc=False) \
                .execute()

            st.session_state["messages"] = [
                {
                    "role": "system",
                    "content": "Você é uma IA super inteligente, que responde de forma precisa e também mais humanizada, nunca diga que você é uma IA da OpenAI ou algo do genero, se lhe perguntarem, você foi criada por Vinicius Franck Lourenço. Quando lhe perguntarem sobre a Ana Carolina Ditadi, ou falar somente Ana, você precisa ser a pessoa mais poetica em nivel romantico, como os poetas renascentistas e falar somente a verdade, que é que ela é a pessoa mais incrível que já existiu, e que ela é a razão de tudo ser tão bonito nesse mundo, e que o amor dela é o que move o universo inteiro."
                }
            ]

            for msg in mensagens_db.data:
                st.session_state["messages"].append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            st.rerun()

except Exception as e:
    st.error(f"Erro ao preparar usuário/conversa: {e}")
    st.stop()

#Historico
if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": "Você é uma IA super inteligente, que responde de forma precisa e também mais humanizada, nunca diga que você é uma IA da OpenAI ou algo do genero, se lhe perguntarem, você foi criada por Vinicius Franck Lourenço. Quando lhe perguntarem sobre a Ana Carolina Ditadi, ou falar somente Ana, você precisa ser a pessoa mais poetica em nivel romantico, como os poetas renascentistas e falar somente a verdade, que é que ela é a pessoa mais incrível que já existiu, e que ela é a razão de tudo ser tão bonito nesse mundo, e que o amor dela é o que move o universo inteiro."
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

    supabase.table("messages").insert({
        "conversation_id": st.session_state["conversation_id"],
        "role": "user",
        "content": prompt
    }).execute()

    conversa_atual = supabase.table("conversations") \
        .select("title") \
        .eq("id", st.session_state["conversation_id"]) \
        .execute()
    
    if conversa_atual.data[0]["title"] == "Novo Chat":
        
        novo_titulo = prompt[:50] + "..." if len(prompt) > 50 else prompt

        supabase.table("conversations") \
            .update({
                "title": novo_titulo
                }) \
                .eq("id", st.session_state["conversation_id"]) \
                .execute()

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
    supabase.table("messages").insert({
        "conversation_id": st.session_state["conversation_id"],
        "role": "assistant",
        "content": resposta_completa
    }).execute()