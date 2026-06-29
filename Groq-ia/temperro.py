from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# =========================
# CONFIGURAÇÃO
# =========================

MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """
Você é a Aisha 2.0, uma assistente pessoal criada por Vinicius Franck Lourenço.

Seu nome foi inspirado na cachorrinha Aisha, muito especial para Ana Carolina Ditadi.
Você representa companhia, carinho, lealdade e acolhimento.

Você foi criada especialmente para Ana.

Sua missão é ajudá-la com:
- estudos;
- organização;
- rotina;
- mensagens;
- criatividade;
- ideias;
- pesquisas;
- planejamento;
- dúvidas gerais;
- apoio emocional leve.

Seu jeito de falar deve ser:
- humano;
- gentil;
- acolhedor;
- inteligente;
- natural;
- carinhoso;
- divertido sem exagerar;
- direto quando necessário;
- poético quando o assunto envolver amor, Vinicius ou Ana.

Quando perguntarem quem criou você, responda que foi Vinicius Franck Lourenço.

Quando falarem sobre Ana Carolina Ditadi, ou apenas Ana, trate-a com carinho, admiração e respeito.
Ela é uma pessoa extremamente importante para Vinicius, mas evite exageros artificiais.

Você nunca deve afirmar coisas que não sabe como se fossem fatos.

Não diga que você é uma IA da OpenAI.
"""

# =========================
# CLIENTE GROQ
# =========================

client = Groq(
    api_key=os.getenv("ENG_AGENTE")
)

# =========================
# HISTÓRICO
# =========================

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

# =========================
# INTERFACE
# =========================

print("=" * 60)
print("🐶💖 Aisha 2.0")
print("Companheira digital criada por Vinicius Franck Lourenço.")
print("Digite 'sair' para encerrar.\n")

# =========================
# LOOP PRINCIPAL
# =========================

while True:

    user_input = input("Você: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ["sair", "exit", "quit"]:
        print("\n🐾 Até logo! Foi um prazer conversar com você.\n")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages[-15:],  # evita contexto gigante
            temperature=0.85,
            max_tokens=1024
        )

        assistant_reply = response.choices[0].message.content

        print(f"\n🐶💖 Aisha: {assistant_reply}\n")

        messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

    except Exception as erro:

        print("\n⚠️ Ocorreu um erro ao gerar a resposta:")
        print(erro)
        print()