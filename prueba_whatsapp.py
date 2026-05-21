import os
from dotenv import load_dotenv
from twilio.rest import Client

# 1. Cargar las llaves ocultas del archivo .env
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
numero_twilio = os.getenv("TWILIO_WHATSAPP_NUMBER") # Ej: 'whatsapp:+14155238886'

print("DEBUG SID:", account_sid)
print("DEBUG TOKEN:", str(auth_token)[:5] + "...") # Solo imprimimos los primeros 5 caracteres por seguridad

# 2. Inicializar el motor de Twilio
cliente = Client(account_sid, auth_token)

# 3. Disparar el mensaje de prueba
try:
    print("Enviando mensaje de prueba...")
    mensaje = cliente.messages.create(
        from_=numero_twilio,
        body="🚀 ¡Hackathon mode ON! Si estás leyendo esto, la conexión de Twilio funciona al 100%.",
        
        # AQUÍ PON TU NÚMERO DE CELULAR PERSONAL (con código de país)
        to="whatsapp:+526682410777" 
    )
    print(f"✅ ¡Éxito brutal! Mensaje enviado. ID: {mensaje.sid}")
    
except Exception as e:
    print(f"❌ Error al enviar el mensaje: {e}")