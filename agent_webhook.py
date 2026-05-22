"""
agent_webhook.py
================
FastAPI webhook que se dispara cuando Supabase inserta una cotización.
Flujo:
  1. Recibe el ID de la cotización vía POST /webhook/cotizacion
  2. El agente LangChain consulta Supabase para construir el contexto completo
  3. Invoca la engine de agrobot_rules para obtener el prediagnóstico
  4. Persiste el resultado en la tabla `prediagnosticos` de Supabase
  5. Envía un correo al asesor interno con el resumen del diagnóstico

Requiere las siguientes variables de entorno (ver .env.example):
  SUPABASE_URL, SUPABASE_SERVICE_KEY
  GOOGLE_API_KEY
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
  ASESOR_EMAIL
"""

from __future__ import annotations

import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from textwrap import dedent
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import Client, create_client

# LangChain + Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# Reglas de negocio propias
from agrobot_rules.engine import recommend_credit
from agrobot_rules.models import ProspectInput

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agrobot.webhook")

# ---------------------------------------------------------------------------
# Clientes globales
# ---------------------------------------------------------------------------

_supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)

_llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.2,
)

# ---------------------------------------------------------------------------
# Herramientas LangChain
# ---------------------------------------------------------------------------

@tool
def obtener_cotizacion(cotizacion_id: str) -> str:
    """
    Recupera todos los datos relevantes de una cotización desde Supabase:
    cotización, oportunidad asociada, empresa y contacto principal.
    Devuelve un JSON con toda la información.
    """
    cot = (
        _supabase.table("cotizaciones")
        .select(
            "id, numero_cotizacion, estado, total, moneda, valida_hasta, "
            "notas, creado_en, "
            "oportunidades(id, titulo, monto, etapa, fuente, puntuacion_lead, "
            "  empresa_id, contacto_id, "
            "  empresas(nombre, industria, ciudad, ingresos_anuales), "
            "  contactos(nombre, apellido, correo, whatsapp, cargo))"
        )
        .eq("id", cotizacion_id)
        .single()
        .execute()
    )
    if not cot.data:
        return json.dumps({"error": f"Cotización {cotizacion_id} no encontrada"})
    return json.dumps(cot.data, ensure_ascii=False, default=str)


@tool
def evaluar_candidatura(
    destino_credito: str,
    actividad: str,
    monto_solicitado: float | None = None,
    poblacion_menor_50000: bool = False,
    tiene_inventario_garantia: bool = False,
    urgencia_dias: int | None = None,
    cliente_recurrente: bool = False,
    documentos_recibidos: list[str] | None = None,
    dias_desde_ultimo_contacto: int | None = None,
) -> str:
    """
    Evalúa si el cliente es candidato a un crédito Agrocapital.
    Usa las reglas de negocio internas para calcular score, prioridad,
    riesgo de abandono y recomienda el producto más adecuado.
    Devuelve un JSON con el prediagnóstico completo.
    """
    prospect = ProspectInput(
        destino_credito=destino_credito,
        actividad=actividad,
        monto_solicitado=monto_solicitado,
        poblacion_menor_50000=poblacion_menor_50000,
        tiene_inventario_garantia=tiene_inventario_garantia,
        urgencia_dias=urgencia_dias,
        cliente_recurrente=cliente_recurrente,
        documentos_recibidos=documentos_recibidos or [],
        dias_desde_ultimo_contacto=dias_desde_ultimo_contacto,
    )
    result = recommend_credit(prospect)
    return json.dumps(result, ensure_ascii=False, default=str)


@tool
def guardar_prediagnostico(
    cotizacion_id: str,
    producto_sugerido_nombre: str,
    contexto_fira: str,
    documentos_faltantes: list[str],
    score_oportunidad: int,
    prioridad: str,
    riesgo_abandono: str,
    siguiente_accion: str,
    resumen_asesor: str,
) -> str:
    """
    Persiste el prediagnóstico en la tabla `prediagnosticos` de Supabase.
    Busca el servicio_id por nombre de producto antes de insertar.
    Devuelve el ID del registro creado.
    """
    # Buscar el servicio_id correspondiente al nombre del producto
    svc = (
        _supabase.table("servicios")
        .select("id")
        .ilike("nombre_servicio", f"%{producto_sugerido_nombre}%")
        .limit(1)
        .execute()
    )
    producto_id = svc.data[0]["id"] if svc.data else None

    row = {
        "cotizacion_id": cotizacion_id,
        "producto_sugerido_id": producto_id,
        "contexto_fira": contexto_fira,
        "documentos_faltantes": documentos_faltantes,
        "score_oportunidad": score_oportunidad,
        "prioridad": prioridad,
        "riesgo_abandono": riesgo_abandono,
        "siguiente_accion": siguiente_accion,
        "resumen_asesor": resumen_asesor,
        "es_aprobacion": False,
    }
    resp = _supabase.table("prediagnosticos").insert(row).execute()
    if resp.data:
        return json.dumps({"prediagnostico_id": resp.data[0]["id"]})
    return json.dumps({"error": "No se pudo guardar el prediagnóstico"})


@tool
def enviar_correo_asesor(
    asunto: str,
    cuerpo_html: str,
) -> str:
    """
    Envía un correo al asesor interno de Agrocapital con el resumen del
    prediagnóstico. El destinatario se toma de la variable ASESOR_EMAIL.
    """
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    asesor_email = os.environ["ASESOR_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = smtp_user
    msg["To"] = asesor_email
    msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [asesor_email], msg.as_string())
        return json.dumps({"enviado": True, "destinatario": asesor_email})
    except Exception as exc:
        logger.error("Error enviando correo: %s", exc)
        return json.dumps({"enviado": False, "error": str(exc)})


# ---------------------------------------------------------------------------
# Agente LangChain
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = dedent("""
    Eres AgroBot, un agente de análisis crediticio para Agrocapital,
    institución financiera especializada en el sector agropecuario mexicano.

    Cuando recibas un ID de cotización debes:

    1. Usar `obtener_cotizacion` para recuperar todos los datos del cliente
       (empresa, actividad, monto, contacto, etc.).

    2. Con esa información usar `evaluar_candidatura` para determinar:
       - Si el cliente ES o NO ES candidato a un crédito.
       - Qué producto le corresponde.
       - Score de oportunidad (0-100), prioridad y riesgo de abandono.

    3. Usar `guardar_prediagnostico` para persistir el resultado en Supabase.

    4. Redactar y enviar con `enviar_correo_asesor` un correo HTML profesional
       al asesor que incluya:
       - Nombre del cliente / empresa.
       - Veredicto claro: CANDIDATO ✅ o NO CANDIDATO ❌ (score < 40).
       - Producto recomendado y resumen.
       - Score, prioridad y riesgo de abandono.
       - Documentos faltantes (si hay).
       - Siguiente acción sugerida.
       - Nota: "Prediagnóstico comercial. No representa aprobación de crédito."

    Sé preciso, profesional y en español. No inventes datos que no estén en
    la cotización o en el resultado de las reglas.
""").strip()

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

_tools = [
    obtener_cotizacion,
    evaluar_candidatura,
    guardar_prediagnostico,
    enviar_correo_asesor,
]

_agent = create_tool_calling_agent(_llm, _tools, prompt)
_executor = AgentExecutor(agent=_agent, tools=_tools, verbose=True, max_iterations=10)

# ---------------------------------------------------------------------------
# FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(title="AgroBot Webhook", version="1.0.0")


class WebhookPayload(BaseModel):
    cotizacion_id: str
    # Supabase Database Webhooks pueden enviar campos extra; los ignoramos.
    class Config:
        extra = "allow"


@app.post("/webhook/cotizacion")
async def webhook_cotizacion(payload: WebhookPayload) -> dict[str, Any]:
    """
    Endpoint que Supabase llama cuando se inserta una nueva cotización.
    Configura el Database Webhook en Supabase apuntando a esta URL con:
      - Event: INSERT
      - Table: cotizaciones
      - HTTP Method: POST
      - Body: { "cotizacion_id": "{{record.id}}" }
    """
    cotizacion_id = payload.cotizacion_id
    logger.info("Webhook recibido para cotizacion_id=%s", cotizacion_id)

    try:
        result = await _executor.ainvoke({
            "input": (
                f"Se acaba de crear la cotización con ID: {cotizacion_id}. "
                "Analiza al cliente, evalúa su candidatura crediticia, "
                "guarda el prediagnóstico y notifica al asesor por correo."
            )
        })
        return {"status": "ok", "cotizacion_id": cotizacion_id, "output": result.get("output")}
    except Exception as exc:
        logger.exception("Error procesando cotización %s", cotizacion_id)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("agent_webhook:app", host="0.0.0.0", port=8000, reload=True)
