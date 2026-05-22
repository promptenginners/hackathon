from __future__ import annotations

try:
    from langchain_core.tools import tool
except ImportError:  # pragma: no cover
    def tool(func):  # type: ignore
        return func

from agrobot_rules.catalog import AGROCAPITAL_SERVICES
from agrobot_rules.document_validator import DocumentInput, DocumentReviewRequest, review_credit_documents
from agrobot_rules.engine import recommend_credit
from agrobot_rules.fira_client import public_fira_context
from agrobot_rules.gmail_client import build_advisor_summary_email, send_gmail_message
from agrobot_rules.models import ProspectInput


@tool
def recomendar_credito_agrocapital(
    destino_credito: str,
    actividad: str,
    poblacion_menor_50000: bool = False,
    tiene_inventario_garantia: bool = False,
    monto_solicitado: float | None = None,
    urgencia_dias: int | None = None,
    cliente_recurrente: bool = False,
    documentos_recibidos: list[str] | None = None,
    dias_desde_ultimo_contacto: int | None = None,
) -> dict:
    """Recomienda un producto financiero de Agrocapital y calcula score comercial."""

    prospect = ProspectInput(
        destino_credito=destino_credito,
        actividad=actividad,
        poblacion_menor_50000=poblacion_menor_50000,
        tiene_inventario_garantia=tiene_inventario_garantia,
        monto_solicitado=monto_solicitado,
        urgencia_dias=urgencia_dias,
        cliente_recurrente=cliente_recurrente,
        documentos_recibidos=documentos_recibidos or [],
        dias_desde_ultimo_contacto=dias_desde_ultimo_contacto,
    )
    return recommend_credit(prospect)


@tool
def consultar_contexto_fira(consulta: str) -> dict:
    """Devuelve contexto publico de FIRA para orientar al agente sin aprobar credito."""

    context = public_fira_context()
    context["consulta"] = consulta
    context["respuesta"] = (
        "Usa FIRA como fuente de contexto: credito, garantias, apoyos, intermediarios, "
        "Agrocostos e informacion sectorial. Para productos comerciales de la demo, usa Agrocapital."
    )
    return context


@tool
def consultar_servicios_agrocapital() -> dict:
    """Devuelve los servicios publicados por Agrocapital para complementar la recomendacion."""

    return {
        "fuente": "Agrocapital",
        "url": "https://agrocapital.com.mx/productos-y-servicios.html",
        "servicios": AGROCAPITAL_SERVICES,
    }


@tool
def enviar_resumen_asesor_gmail(
    nombre_prospecto: str,
    correo_asesor: str,
    recomendacion: dict,
) -> dict:
    """Envia por Gmail el resumen operativo de una oportunidad al asesor comercial."""

    email = build_advisor_summary_email(
        lead_name=nombre_prospecto,
        advisor_email=correo_asesor,
        recommendation=recomendacion,
    )
    return send_gmail_message(**email)


@tool
def revisar_documentos_credito(
    nombre_prospecto: str,
    documentos: list[dict],
    producto_sugerido: str | None = None,
    datos_esperados: dict | None = None,
) -> dict:
    """Revisa documentos recibidos para un expediente de credito Agrocapital."""

    request = DocumentReviewRequest(
        nombre_prospecto=nombre_prospecto,
        producto_sugerido=producto_sugerido,
        documentos=[
            DocumentInput(
                tipo=str(document.get("tipo", "")),
                archivo_local=document.get("archivo_local"),
                texto=document.get("texto"),
            )
            for document in documentos
        ],
        datos_esperados={str(key): str(value) for key, value in (datos_esperados or {}).items()},
    )
    return review_credit_documents(request)
