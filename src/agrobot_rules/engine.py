from __future__ import annotations

from agrobot_rules.catalog import AGROCAPITAL_PRODUCTS, REQUIRED_DOCUMENTS
from agrobot_rules.models import ProspectInput


def _normalize(value: str) -> str:
    return value.strip().casefold()


def _contains_any(text: str, keywords: list[str]) -> bool:
    normalized = _normalize(text)
    return any(keyword in normalized for keyword in keywords)


def _missing_documents(received: list[str]) -> list[str]:
    received_set = {_normalize(document) for document in received}
    return [document for document in REQUIRED_DOCUMENTS if _normalize(document) not in received_set]


def _score_prospect(prospect: ProspectInput, missing_docs: list[str]) -> int:
    score = 45

    if prospect.monto_solicitado and prospect.monto_solicitado >= 500_000:
        score += 15
    elif prospect.monto_solicitado and prospect.monto_solicitado >= 100_000:
        score += 8

    if prospect.urgencia_dias is not None:
        if prospect.urgencia_dias <= 7:
            score += 15
        elif prospect.urgencia_dias <= 30:
            score += 8

    if prospect.cliente_recurrente:
        score += 10

    score += max(0, 18 - (len(missing_docs) * 3))

    if prospect.dias_desde_ultimo_contacto is not None:
        if prospect.dias_desde_ultimo_contacto >= 7:
            score -= 12
        elif prospect.dias_desde_ultimo_contacto >= 3:
            score -= 6

    return max(0, min(100, score))


def _priority(score: int) -> str:
    if score >= 80:
        return "Alta"
    if score >= 50:
        return "Media"
    return "Baja"


def _abandonment_risk(prospect: ProspectInput, missing_docs: list[str]) -> str:
    stale = prospect.dias_desde_ultimo_contacto is not None and prospect.dias_desde_ultimo_contacto >= 5
    urgent = prospect.urgencia_dias is not None and prospect.urgencia_dias <= 7

    if stale and (urgent or len(missing_docs) >= 4):
        return "Alto"
    if stale or len(missing_docs) >= 3:
        return "Medio"
    return "Bajo"


def _recommend_product(prospect: ProspectInput) -> tuple[str, list[str]]:
    destination = prospect.destino_credito
    activity = prospect.actividad

    ordered_rules = [
        "credito_refaccionario",
        "credito_avio",
        "capital_trabajo",
        "arrendamiento_puro",
        "credito_prendario",
        "credito_empresarial",
        "financiamiento_rural",
    ]

    if prospect.tiene_inventario_garantia:
        return "credito_prendario", ["El prospecto puede usar inventarios o cosechas como garantia."]

    for product_key in ordered_rules:
        product = AGROCAPITAL_PRODUCTS[product_key]
        if _contains_any(destination, product["use_cases"]) or _contains_any(activity, product["use_cases"]):
            return product_key, [f"Coincide con destino/actividad: {product['summary']}"]

    if prospect.poblacion_menor_50000:
        return "financiamiento_rural", ["La actividad se desarrolla en una poblacion menor a 50,000 habitantes."]

    return "revision_manual", ["No hubo coincidencia clara; debe revisarlo un asesor."]


def recommend_credit(prospect: ProspectInput) -> dict:
    product_key, reasons = _recommend_product(prospect)
    missing_docs = _missing_documents(prospect.documentos_recibidos)
    score = _score_prospect(prospect, missing_docs)
    priority = _priority(score)
    risk = _abandonment_risk(prospect, missing_docs)

    if product_key == "revision_manual":
        product = {
            "name": "Revision manual por asesor",
            "summary": "El caso requiere diagnostico comercial.",
            "term": "Sujeto a analisis.",
            "fees": None,
            "cat": None,
            "source": "Agrocapital",
            "source_url": "https://agrocapital.com.mx/productos-y-servicios.html",
        }
    else:
        product = AGROCAPITAL_PRODUCTS[product_key]

    if priority == "Alta":
        next_action = "Asignar asesor y llamar hoy."
    elif missing_docs:
        next_action = "Solicitar documentos faltantes y programar seguimiento."
    else:
        next_action = "Enviar informacion del producto y nutrir la oportunidad."

    return {
        "producto_sugerido": product["name"],
        "fuente_producto": "Agrocapital",
        "contexto_fira": _fira_context_for(product["name"]),
        "resumen_producto": product["summary"],
        "plazo_referencial": product["term"],
        "comisiones_referenciales": product["fees"],
        "cat_referencial": product["cat"],
        "url_fuente": product["source_url"],
        "razones": reasons,
        "documentos_faltantes": missing_docs,
        "score_oportunidad": score,
        "prioridad": priority,
        "riesgo_abandono": risk,
        "siguiente_accion": next_action,
        "nota": "Prediagnostico comercial. No representa aprobacion de credito.",
    }


def _fira_context_for(product_name: str) -> str:
    if product_name in {"Credito de Habilitacion o Avio", "Capital de Trabajo"}:
        return "FIRA contempla creditos de avio y/o capital de trabajo para insumos, materias primas, jornales y gastos directos de produccion."
    if product_name == "Credito Refaccionario":
        return "FIRA contempla credito refaccionario para inversiones fijas; el plazo maximo general publicado es de 15 anos."
    if product_name == "Credito Prendario":
        return "FIRA contempla credito prendario para comercializacion y liquidez respaldada con inventarios pignorables."
    if product_name == "Arrendamiento Puro":
        return "FIRA contempla arrendamiento financiero y puro para bienes de activo fijo elegibles."
    if product_name == "Financiamiento Rural":
        return "FIRA contempla financiamiento rural para actividades economicas licitas en localidades de hasta 50,000 habitantes."
    return "FIRA opera como banca de segundo piso mediante intermediarios financieros autorizados."
