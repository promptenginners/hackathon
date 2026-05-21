from __future__ import annotations

import base64
import os
from email.message import EmailMessage
from pathlib import Path
from typing import Any

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
SCOPES = [GMAIL_SEND_SCOPE]


class GmailConfigurationError(RuntimeError):
    pass


def create_email_message(
    to: str,
    subject: str,
    body: str,
    sender: str | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message.set_content(body)
    if sender:
        message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    return message


def encode_message(message: EmailMessage) -> str:
    return base64.urlsafe_b64encode(message.as_bytes()).decode()


def load_gmail_credentials(
    token_path: str | os.PathLike[str] | None = None,
    credentials_path: str | os.PathLike[str] | None = None,
) -> Any:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as error:
        raise GmailConfigurationError(
            'Faltan dependencias de Gmail API. Instala con: pip install -e ".[agent]"'
        ) from error

    token_file = Path(token_path or os.getenv("GMAIL_TOKEN_PATH", "token.json"))
    credentials_file = Path(credentials_path or os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"))

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds

    if not credentials_file.exists():
        raise GmailConfigurationError(
            f"No se encontro {credentials_file}. Descarga el OAuth Client JSON de Google Cloud "
            "y guardalo como credentials.json, o define GMAIL_CREDENTIALS_PATH."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
    creds = flow.run_local_server(port=0)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


def send_gmail_message(
    to: str,
    subject: str,
    body: str,
    sender: str | None = None,
    token_path: str | os.PathLike[str] | None = None,
    credentials_path: str | os.PathLike[str] | None = None,
) -> dict:
    try:
        from googleapiclient.discovery import build
    except ImportError as error:
        raise GmailConfigurationError(
            'Faltan dependencias de Gmail API. Instala con: pip install -e ".[agent]"'
        ) from error

    creds = load_gmail_credentials(token_path=token_path, credentials_path=credentials_path)
    service = build("gmail", "v1", credentials=creds)
    message = create_email_message(to=to, subject=subject, body=body, sender=sender)
    result = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": encode_message(message)})
        .execute()
    )
    return {
        "status": "sent",
        "message_id": result.get("id"),
        "thread_id": result.get("threadId"),
        "to": to,
        "subject": subject,
    }


def build_advisor_summary_email(
    lead_name: str,
    advisor_email: str,
    recommendation: dict,
) -> dict:
    subject = f"AgroBot - Resumen de oportunidad: {lead_name}"
    body = "\n".join(
        [
            "Resumen generado por AgroBot",
            "",
            f"Prospecto: {lead_name}",
            f"Producto sugerido: {recommendation.get('producto_sugerido', 'N/D')}",
            f"Prioridad: {recommendation.get('prioridad', 'N/D')}",
            f"Score: {recommendation.get('score_oportunidad', 'N/D')}",
            f"Riesgo de abandono: {recommendation.get('riesgo_abandono', 'N/D')}",
            f"Siguiente accion: {recommendation.get('siguiente_accion', 'N/D')}",
            "",
            "Documentos faltantes:",
            ", ".join(recommendation.get("documentos_faltantes") or ["Sin faltantes detectados"]),
            "",
            "Nota:",
            recommendation.get("nota", "Prediagnostico comercial. No representa aprobacion de credito."),
        ]
    )
    return {"to": advisor_email, "subject": subject, "body": body}
