from __future__ import annotations

try:
    from langchain_core.tools import tool
except ImportError:  # pragma: no cover
    def tool(func):  # type: ignore
        return func

from agrobot_rules.catalog import AGROCAPITAL_SERVICES
from agrobot_rules.engine import recommend_credit
from agrobot_rules.fira_client import public_fira_context
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
