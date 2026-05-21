from agrobot_rules.gmail_client import build_advisor_summary_email, create_email_message, encode_message


def test_create_and_encode_email_message() -> None:
    message = create_email_message(
        to="asesor@example.com",
        subject="AgroBot prueba",
        body="Resumen de oportunidad",
        sender="agrobot@example.com",
    )

    encoded = encode_message(message)

    assert message["To"] == "asesor@example.com"
    assert message["Subject"] == "AgroBot prueba"
    assert encoded


def test_build_advisor_summary_email() -> None:
    email = build_advisor_summary_email(
        lead_name="Rancho La Esperanza",
        advisor_email="asesor@example.com",
        recommendation={
            "producto_sugerido": "Credito Refaccionario",
            "prioridad": "Alta",
            "score_oportunidad": 91,
            "riesgo_abandono": "Medio",
            "siguiente_accion": "Llamar hoy.",
            "documentos_faltantes": ["cotizacion"],
        },
    )

    assert email["to"] == "asesor@example.com"
    assert "Rancho La Esperanza" in email["subject"]
    assert "Credito Refaccionario" in email["body"]
