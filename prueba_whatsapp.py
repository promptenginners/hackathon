import os
import time

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
numero_twilio = os.getenv("TWILIO_WHATSAPP_FROM") or os.getenv("TWILIO_WHATSAPP_NUMBER")
numero_destino = os.getenv("TWILIO_WHATSAPP_TO")

PLACEHOLDER_VALUES = {
    "tu_account_sid",
    "tu_auth_token",
    "tu_account_sid_de_twilio",
    "tu_auth_token_de_twilio",
}

if not account_sid or not auth_token or not numero_twilio or not numero_destino:
    raise SystemExit(
        "Faltan variables. Configura TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
        "TWILIO_WHATSAPP_FROM y TWILIO_WHATSAPP_TO en .env"
    )

if account_sid in PLACEHOLDER_VALUES or auth_token in PLACEHOLDER_VALUES:
    raise SystemExit(
        "Tus credenciales de Twilio siguen como ejemplo. Copia el Account SID y Auth Token reales "
        "desde Twilio Console > Account Info y pegalos en .env."
    )

if not account_sid.startswith("AC"):
    raise SystemExit("TWILIO_ACCOUNT_SID debe empezar con 'AC'. Revisa el valor en .env.")

if not numero_twilio.startswith("whatsapp:") or not numero_destino.startswith("whatsapp:"):
    raise SystemExit("Los numeros deben iniciar con 'whatsapp:', ejemplo whatsapp:+5216681234567")

try:
    cliente = Client(account_sid, auth_token)

    print("Enviando mensaje de prueba...")
    mensaje = cliente.messages.create(
        from_=numero_twilio,
        body="AgroBot: prueba de conexion por WhatsApp desde Twilio.",
        to=numero_destino,
    )
    print(f"Mensaje aceptado por Twilio. SID: {mensaje.sid}")
    print(f"Estado inicial: {mensaje.status}")

    for intento in range(1, 7):
        time.sleep(2)
        estado = cliente.messages(mensaje.sid).fetch()
        print(f"Estado {intento}: {estado.status}")

        if estado.status in {"delivered", "read"}:
            print("Entregado correctamente.")
            break

        if estado.status in {"failed", "undelivered"}:
            print("Twilio no pudo entregar el mensaje.")
            print(f"Error code: {estado.error_code}")
            print(f"Error message: {estado.error_message}")
            break
    else:
        print("Twilio acepto el mensaje, pero aun no confirma entrega.")
        print("Revisa que tu celular este unido al WhatsApp Sandbox de Twilio.")

except Exception as error:
    print(f"Error al enviar el mensaje: {error}")
