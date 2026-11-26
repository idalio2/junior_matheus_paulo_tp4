import asyncio
import os
import requests

from getpass import getpass
from agents import Agent, Runner, function_tool

URL_API = "http://127.0.0.1:8000"

token_jwt = None


def autenticar():
    usuario = input("Usuário da API: ")
    senha = getpass("Senha da API: ")

    resposta = requests.post(
        f"{URL_API}/auth/token",
        data={
            "username": usuario,
            "password": senha
        },
        timeout=10
    )

    resposta.raise_for_status()

    return resposta.json()["access_token"]


@function_tool
def classificar_intencao(texto: str) -> str:
    """Classifica a intenção da mensagem do cliente
    utilizando a API FastAPI."""

    resposta = requests.post(
        f"{URL_API}/classify",
        json={"texto": texto},
        headers={
            "Authorization": f"Bearer {token_jwt}"
        },
        timeout=10
    )

    resposta.raise_for_status()

    resultado = resposta.json()

    print("\n[Resultado da API de classificação]")
    print(f"Intenção: {resultado['intencao']}")
    print(f"Probabilidade: {resultado['probabilidade']:.2%}")

    return resposta.text


agente = Agent(
    name="Agente de Atendimento",
    instructions="""
    Você é um agente de atendimento ao cliente.

    Utilize a ferramenta classificar_intencao para
    analisar cada nova mensagem do cliente.

    As possíveis intenções são:

    - Billing inquiry
    - Cancellation request
    - Product inquiry
    - Refund request
    - Technical issue

    Considere a classificação como uma informação
    auxiliar, pois o modelo pode cometer erros.

    Analise também o contexto da conversa.

    Responda de maneira educada, clara e objetiva,
    no mesmo idioma utilizado pelo cliente.

    Não invente informações sobre a empresa e não
    afirme ter realizado operações que não executou.
    """,
    tools=[classificar_intencao]
)


async def main():
    global token_jwt

    if not os.getenv("OPENAI_API_KEY"):
        print("Configure a variável OPENAI_API_KEY.")
        return

    token_jwt = autenticar()

    print("\nAutenticação JWT realizada com sucesso!")
    print("\n=== Agente de Atendimento ===")

    mensagens = [
        "I would like to cancel my subscription.",
        "Will I receive a refund after cancellation?",
        "How can I contact technical support?"
    ]

    historico = []

    for turno, mensagem in enumerate(mensagens, start=1):

        print(f"\n--- Turno {turno} ---")
        print(f"Cliente: {mensagem}")

        historico.append({
            "role": "user",
            "content": mensagem
        })

        resultado = await Runner.run(
            agente,
            input=historico
        )

        print(f"\nAgente: {resultado.final_output}")

        historico = resultado.to_input_list()


if __name__ == "__main__":
    asyncio.run(main())