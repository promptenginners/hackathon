from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agrobot_rules.catalog import REQUIRED_DOCUMENTS


@dataclass(frozen=True)
class DocumentInput:
    tipo: str
    archivo_local: str | None = None
    texto: str | None = None


@dataclass(frozen=True)
class DocumentReviewRequest:
    nombre_prospecto: str
    producto_sugerido: str | None = None
    documentos: list[DocumentInput] = field(default_factory=list)
    datos_esperados: dict[str, str] = field(default_factory=dict)


def _normalize(value: str) -> str:
    return value.strip().casefold()


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf_file(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError('Para leer PDF instala el extra: pip install -e ".[docs]"') from error

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_document_text(document: DocumentInput) -> str:
    if document.texto:
        return document.texto

    if not document.archivo_local:
        return ""

    path = Path(document.archivo_local)
    if not path.exists():
        return ""

    suffix = path.suffix.casefold()
    if suffix in {".txt", ".md", ".csv"}:
        return _read_text_file(path)
    if suffix == ".pdf":
        return _read_pdf_file(path)

    return ""


def review_credit_documents(request: DocumentReviewRequest) -> dict[str, Any]:
    received_types = {_normalize(document.tipo) for document in request.documentos}
    required_types = {_normalize(document) for document in REQUIRED_DOCUMENTS}

    missing_documents = [
        document for document in REQUIRED_DOCUMENTS if _normalize(document) not in received_types
    ]
    unexpected_documents = [
        document.tipo for document in request.documentos if _normalize(document.tipo) not in required_types
    ]

    extracted_text_by_type: dict[str, str] = {}
    unreadable_documents: list[str] = []
    for document in request.documentos:
        text = extract_document_text(document)
        if text:
            extracted_text_by_type[document.tipo] = text
        elif document.archivo_local:
            unreadable_documents.append(document.tipo)

    all_text = "\n".join(extracted_text_by_type.values()).casefold()
    data_matches = {
        key: _normalize(value) in all_text
        for key, value in request.datos_esperados.items()
        if value
    }
    missing_expected_data = [key for key, matched in data_matches.items() if not matched]

    if missing_documents or missing_expected_data or unreadable_documents:
        status = "incompleto"
    elif unexpected_documents:
        status = "requiere_revision"
    else:
        status = "completo"

    if status == "completo":
        next_action = "Continuar con evaluacion comercial y preparar propuesta."
    elif status == "requiere_revision":
        next_action = "Revisar documentos no esperados antes de avanzar."
    else:
        next_action = "Solicitar documentos o datos faltantes al prospecto."

    return {
        "prospecto": request.nombre_prospecto,
        "producto_sugerido": request.producto_sugerido,
        "estado_documental": status,
        "documentos_recibidos": [document.tipo for document in request.documentos],
        "documentos_faltantes": missing_documents,
        "documentos_no_esperados": unexpected_documents,
        "documentos_no_legibles": unreadable_documents,
        "datos_verificados": data_matches,
        "datos_esperados_faltantes": missing_expected_data,
        "siguiente_accion": next_action,
        "nota": "Revision documental preliminar. No sustituye validacion legal o crediticia formal.",
    }
