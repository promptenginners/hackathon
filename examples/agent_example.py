import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from agrobot_rules.tools import (
    consultar_contexto_fira,
    consultar_servicios_agrocapital,
    recomendar_credito_agrocapital,
)

load_dotenv(".env")

SYSTEM_PROMPT = """
Eres AgroBot, un agente de ventas B2B para Agrocapital.

Reglas obligatorias:
- La fuente principal de productos financieros es Agrocapital.
- FIRA se usa como contexto publico: tipos de credito, actividades financiables,
  intermediarios financieros e informacion sectorial.
- No prometas aprobacion de credito.
- Siempre indica que la respuesta es un prediagnostico comercial.
- Si faltan datos, pide ubicacion, actividad, monto, destino del credito,
  urgencia y documentos disponibles.
- Cuando tengas datos suficientes, usa la tool recomendar_credito_agrocapital.
"""


def build_agent():
    model = init_chat_model(
        model=os.getenv("CHAT_MODEL", "google_genai:gemini-flash-latest"),
        temperature=0.0,
    )

    return create_agent(
        model=model,
        tools=[
            recomendar_credito_agrocapital,
            consultar_contexto_fira,
            consultar_servicios_agrocapital,
        ],
        system_prompt=SYSTEM_PROMPT,
    )


if __name__ == "__main__":
    agent = build_agent()
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Soy productor de maiz en Guasave. Necesito financiamiento "
                        "para insumos del proximo ciclo por 600000 pesos y me urge esta semana."
                    ),
                }
            ]
        }
    )
    print(response["messages"][-1].content)
