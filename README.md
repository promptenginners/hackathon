# AgroBot Agrocapital

Repositorio para el hackathon de agentes inteligentes Build Day 2026.

AgroBot es un bot de cotizacion y prediagnostico comercial para Agrocapital.
Recibe solicitudes por WhatsApp, recomienda productos financieros, genera datos
para toma de decision y puede enviar una salida al asesor por Gmail.

## Tecnologias decididas

- Base de datos: Supabase.
- Agente: LangChain.
- LLM: Gemini 3.1 Flash-Lite.
- Canal de entrada: WhatsApp.
- Salida operativa: Gmail.
- Contexto externo: API/Fuentes FIRA.
- Reglas de negocio: catalogo Agrocapital + contexto FIRA.


## Producto

Un bot de cotizacion que genere datos accionables para toma de decision:

- producto financiero sugerido.
- score de oportunidad.
- prioridad comercial.
- riesgo de abandono.
- documentos faltantes.
- siguiente accion recomendada.
- resumen para asesor.

## Estructura

- `src/agrobot_rules/catalog.py`: catalogo de productos y servicios de Agrocapital.
- `src/agrobot_rules/engine.py`: motor de recomendacion, scoring y siguiente accion.
- `src/agrobot_rules/tools.py`: tools listas para conectar con LangChain.
- `src/agrobot_rules/fira_client.py`: cliente preparado para una API FIRA futura.
- `src/agrobot_rules/gmail_client.py`: salida operativa por Gmail API.
- `docs/arquitectura.md`: stack tecnico y flujo de integraciones.
- `docs/reglas_negocio.md`: resumen de reglas para el equipo.
- `tests/test_engine.py`: pruebas basicas del motor.

## Uso rapido

```python
from agrobot_rules import ProspectInput, recommend_credit

result = recommend_credit(
    ProspectInput(
        destino_credito="insumos para maiz",
        actividad="agricola",
        monto_solicitado=600000,
        urgencia_dias=7,
    )
)

print(result["producto_sugerido"])
```

## Instalar para desarrollo

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test,agent]"
pytest
```

## Modelo del agente

El ejemplo usa Gemini 3.1 Flash-Lite por default:

```text
google_genai:gemini-3.1-flash-lite
```

Configura tu API key de Google AI Studio antes de correr el agente:

```powershell
$env:GOOGLE_API_KEY="tu_api_key"
python examples/agent_example.py
```

Para cambiar de modelo sin editar codigo:

```powershell
$env:CHAT_MODEL="google_genai:gemini-3.1-flash-lite"
```

## Salida por Gmail

La integracion usa Gmail API con OAuth y scope `gmail.send`.

1. Habilita Gmail API en Google Cloud.
2. Crea un OAuth Client de tipo Desktop app.
3. Descarga el archivo como `credentials.json` en la raiz del repo.
4. Configura el destinatario:

```powershell
$env:GMAIL_ADVISOR_TO="asesor@tu-dominio.com"
```

5. Ejecuta una prueba:

```powershell
python examples/gmail_send_example.py
```

La primera ejecucion abre el navegador para autorizar Gmail y genera `token.json`.
`credentials.json` y `token.json` no se suben a GitHub.

## Prueba de WhatsApp

Configura en `.env`:

```powershell
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+5216681234567
```

Luego ejecuta:

```powershell
python prueba_whatsapp.py
```

Si Twilio dice `sent` o `queued` pero no llega al celular, revisa:

- El celular debe estar unido al WhatsApp Sandbox de Twilio.
- Desde tu WhatsApp envia el codigo `join ...` que Twilio muestra en Sandbox.
- El numero destino debe incluir `whatsapp:` y codigo de pais.
- En Mexico normalmente usa formato `whatsapp:+52...` o `whatsapp:+521...` segun lo acepte tu sandbox.
- Revisa el estado final: `delivered`, `failed` o `undelivered`.
