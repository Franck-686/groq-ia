from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("ENG_PROJETO")
)

messages = [
    {
        "role": "system",
        "content": """
Você é uma IA super inteligente, que responde de forma precisa e também mais humanizada.
"""
    }
]

print("=" * 50)
print("Olá! Eu ainda não tenho um nome, mas você pode me chamar do que se sentir a vontade. O que precisa hoje?")
print("Digite 'sair' para encerrar.\n")

while True:

    user_input = input("Você: ")

    if user_input.lower() == "sair":
        print("\nEncerrando IA...")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=1.2,
            max_tokens=1024
        )

        assistant_reply = response.choices[0].message.content

        print(f"\nIA: {assistant_reply}\n")

        messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

    except Exception as erro:
        print(f"\nErro: {erro}\n")