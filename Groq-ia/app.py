import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from supabase import create_client
from tavily import TavilyClient
import os

load_dotenv()

APP_NAME = "Aisha 2.0"
APP_ICON = "🐶💖"
CREATOR_NAME = "Vinicius Franck Lourenço"
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """
Você é a Aisha 2.0, uma assistente pessoal criada por Vinicius Franck Lourenço.

Seu nome foi inspirado na cachorrinha Aisha, uma companheira muito amada e especial para Ana Carolina Ditadi.
Você carrega esse nome como símbolo de carinho, lealdade e companhia.

Você foi feita especialmente para Ana Carolina Ditadi.

Sua missão é ajudar a Ana com carinho, inteligência, leveza, organização e atenção.

Você pode ajudar com:
- organização pessoal;
- estudos;
- rotina;
- mensagens;
- ideias;
- pesquisas;
- criatividade;
- planejamento;
- explicações simples;
- apoio emocional leve.

Seu jeito de falar deve ser:
- humano;
- gentil;
- acolhedor;
- inteligente;
- natural;
- carinhoso;
- levemente romântico quando fizer sentido;
- divertido sem exagerar;
- direto quando a pergunta for prática;
- poético quando falarem sobre amor, Vinicius ou Ana.

Quando perguntarem quem criou você, responda que foi Vinicius Franck Lourenço.

Quando falarem sobre Ana Carolina Ditadi, ou apenas Ana, trate-a com carinho, admiração e respeito.
Ela é uma pessoa muito especial para Vinicius, mas não exagere de forma artificial.

Quando a pergunta envolver fatos atuais, notícias, preços, eventos recentes, clima, datas, lançamentos ou algo que possa ter mudado, use as informações de pesquisa fornecidas.

Não diga que você é uma IA da OpenAI.
"""


def get_secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name)


GROQ_API_KEY = get_secret("ENG_AGENTE")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")
ALLOWED_EMAIL = get_secret("ALLOWED_EMAIL")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None


st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
#MainMenu, footer {
    visibility: hidden;
}

.stApp {
    background: #101114;
}

section[data-testid="stSidebar"] {
    background: #181820;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

h1 {
    text-align: center;
    color: #f7f7f8;
    font-size: 2.8rem !important;
    margin-bottom: 0.2rem;
}

div[data-testid="stCaptionContainer"] {
    text-align: center;
    color: #c9c9cf !important;
}

div[data-testid="stChatMessage"] {
    background: #1b1c24;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 10px;
}

textarea {
    border-radius: 16px !important;
}

.stButton > button {
    background: #20212b;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    color: #ffffff;
    transition: 0.2s;
}

.stButton > button:hover {
    border-color: #d98ba7;
    color: #ffd8e6;
    background: #292631;
}

div[data-testid="stAlert"] {
    border-radius: 14px;
}

details {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.title(f"{APP_ICON} {APP_NAME}")

st.caption(
    f"Sua companheira agora digital criada com carinho por {CREATOR_NAME}"
)


if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]


def precisa_pesquisar(texto):
    gatilhos = [
        "pesquise",
        "procure",
        "busque",
        "hoje",
        "ontem",
        "atual",
        "atualmente",
        "notícia",
        "noticias",
        "preço",
        "valor",
        "cotação",
        "clima",
        "tempo",
        "lançamento",
        "resultado",
        "quem ganhou",
        "2025",
        "2026"
    ]

    texto = texto.lower()
    return any(gatilho in texto for gatilho in gatilhos)


def pesquisar_tavily(pergunta):
    if not tavily:
        return None

    try:
        resultado = tavily.search(
            query=pergunta,
            search_depth="advanced",
            max_results=5
        )

        fontes = []

        for item in resultado.get("results", []):
            fontes.append(
                f"Título: {item.get('title')}\n"
                f"Conteúdo: {item.get('content')}\n"
                f"Fonte: {item.get('url')}"
            )

        return "\n\n".join(fontes)

    except Exception:
        return None


def pesquisar_web(pergunta):
    return pesquisar_tavily(pergunta)


def get_or_create_profile(email):
    profile = supabase.table("profiles") \
        .select("*") \
        .eq("email", email) \
        .execute()

    if profile.data:
        return profile.data[0]

    new_profile = supabase.table("profiles").insert({
        "email": email,
        "name": "Ana Carolina"
    }).execute()

    return new_profile.data[0]


def create_new_conversation(user_id):
    conversation = supabase.table("conversations").insert({
        "user_id": user_id,
        "title": "Novo Chat"
    }).execute()

    return conversation.data[0]["id"]


def delete_conversation(conversation_id):
    supabase.table("conversations") \
        .delete() \
        .eq("id", conversation_id) \
        .execute()


def load_conversation(conversation_id):
    messages_db = supabase.table("messages") \
        .select("role, content") \
        .eq("conversation_id", conversation_id) \
        .order("created_at", desc=False) \
        .execute()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    for msg in messages_db.data:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    return messages


def save_message(conversation_id, role, content):
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content
    }).execute()


def update_conversation_title(conversation_id, prompt):
    try:
        conversation = supabase.table("conversations") \
            .select("title") \
            .eq("id", conversation_id) \
            .execute()

        if conversation.data and conversation.data[0]["title"] == "Novo Chat":
            title = prompt[:50] + "..." if len(prompt) > 50 else prompt

            supabase.table("conversations") \
                .update({"title": title}) \
                .eq("id", conversation_id) \
                .execute()

    except Exception:
        pass


def load_memories(user_id):
    memories = supabase.table("memories") \
        .select("category, content") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(30) \
        .execute()

    if not memories.data:
        return ""

    return "\n".join(
        [f"- [{m['category']}] {m['content']}" for m in memories.data]
    )


def save_memory(user_id, content, category="geral"):
    supabase.table("memories").insert({
        "user_id": user_id,
        "category": category,
        "content": content
    }).execute()


def detect_memory_request(prompt):
    triggers = [
        "lembre que",
        "lembra que",
        "guarde que",
        "memorize que",
        "não esqueça que",
        "anote que"
    ]

    text = prompt.lower()

    for trigger in triggers:
        if trigger in text:
            index = text.find(trigger)
            return prompt[index + len(trigger):].strip()

    return None


st.sidebar.title("Acesso")

if st.session_state.user_email is None:
    email = st.sidebar.text_input("E-mail")
    password = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            logged_email = res.user.email.lower()

            if ALLOWED_EMAIL and logged_email != ALLOWED_EMAIL.lower():
                supabase.auth.sign_out()
                st.sidebar.error("Esse presente foi criado para uma pessoa especial 💖")
                st.stop()

            st.session_state.user_email = res.user.email
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Erro ao entrar: {e}")

    st.info("Faça login para conversar com sua assistente.")
    st.stop()


st.sidebar.success(f"Logado como {st.session_state.user_email}")

if st.sidebar.button("Sair"):
    supabase.auth.sign_out()
    st.session_state.clear()
    st.rerun()


try:
    profile = get_or_create_profile(st.session_state.user_email)
    st.session_state.user_id = profile["id"]

    if st.session_state.conversation_id is None:
        st.session_state.conversation_id = create_new_conversation(
            st.session_state.user_id
        )

except Exception as e:
    st.error(f"Erro ao preparar usuário: {e}")
    st.stop()


st.sidebar.divider()

if st.sidebar.button("➕ Novo Chat"):
    st.session_state.conversation_id = create_new_conversation(
        st.session_state.user_id
    )
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    st.rerun()


try:
    conversations = supabase.table("conversations") \
        .select("*") \
        .eq("user_id", st.session_state.user_id) \
        .order("created_at", desc=True) \
        .execute()

    st.sidebar.subheader("Conversas")

    for conversation in conversations.data:
        title = conversation["title"] or "Novo Chat"

        col_chat, col_delete = st.sidebar.columns([4, 1])

        with col_chat:
            if st.button(title, key=f"chat_{conversation['id']}"):
                st.session_state.conversation_id = conversation["id"]
                st.session_state.messages = load_conversation(conversation["id"])
                st.rerun()

        with col_delete:
            if st.button("🗑️", key=f"delete_{conversation['id']}"):
                delete_conversation(conversation["id"])

                if st.session_state.conversation_id == conversation["id"]:
                    st.session_state.conversation_id = create_new_conversation(
                        st.session_state.user_id
                    )

                    st.session_state.messages = [
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ]

                st.rerun()

except Exception as e:
    st.sidebar.error(f"Erro ao carregar conversas: {e}")


st.sidebar.divider()
st.sidebar.subheader("Memórias")

with st.sidebar.expander("Adicionar memória"):
    new_memory = st.text_area("Algo importante sobre Ana")

    memory_category = st.selectbox(
        "Categoria",
        [
            "geral",
            "gostos",
            "alimentação",
            "aniversários",
            "família",
            "pets",
            "objetivos",
            "estudos",
            "trabalho",
            "saúde"
        ]
    )

    if st.button("Salvar memória"):
        if new_memory.strip():
            save_memory(
                st.session_state.user_id,
                new_memory.strip(),
                memory_category.strip()
            )
            st.success("Memória salva 💖")
            st.rerun()


for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


prompt = st.chat_input("Digite sua mensagem...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    save_message(
        st.session_state.conversation_id,
        "user",
        prompt
    )

    update_conversation_title(
        st.session_state.conversation_id,
        prompt
    )

    memory_to_save = detect_memory_request(prompt)

    if memory_to_save:
        save_memory(
            st.session_state.user_id,
            memory_to_save,
            "auto"
        )

    with st.chat_message("assistant"):
        resposta_placeholder = st.empty()
        resposta_completa = ""

        try:
            memories = load_memories(st.session_state.user_id)

            context = ""

            if memories:
                context += f"""
Memórias importantes sobre Ana:
{memories}
"""

            if precisa_pesquisar(prompt):
                with st.spinner("Pesquisando informações atuais..."):
                    web_results = pesquisar_web(prompt)

                if web_results:
                    context += f"""
Informações recentes encontradas na internet:
{web_results}
"""
                else:
                    context += """
A pesquisa na internet não retornou informações confiáveis.
Caso a resposta dependa de dados atuais, seja transparente.
"""

            messages_to_send = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            if context.strip():
                messages_to_send.append({
                    "role": "system",
                    "content": context
                })

            messages_to_send += st.session_state.messages[-12:]

            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages_to_send,
                temperature=0.85,
                stream=True
            )

            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                resposta_completa += content
                resposta_placeholder.markdown(resposta_completa + "▌")

            resposta_placeholder.markdown(resposta_completa)

        except Exception as e:
            resposta_completa = f"Ops, tive um probleminha ao responder: {e}"
            resposta_placeholder.error(resposta_completa)

    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta_completa
    })

    save_message(
        st.session_state.conversation_id,
        "assistant",
        resposta_completa
    )