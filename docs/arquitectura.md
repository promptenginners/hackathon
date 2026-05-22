# Arquitectura: AgroBot

## Stack decidido

- BD: Supabase.
- Agente: LangChain.
- LLM: Gemini 3.1 Flash-Lite.
- Canal de entrada: Telegram.
- Salida: Gmail.
- Fuente externa: FIRA.
- Reglas de negocio: productos Agrocapital y contexto FIRA.

## API key

La API key de Gemini no debe guardarse en GitHub. Configurala en `.env` usando
la variable `GOOGLE_API_KEY`, tomando como base `.env.example`.

## Flujo principal

1. El prospecto o asesor envia la solicitud por Telegram.
2. LangChain orquesta AgroBot.
3. Gemini interpreta la solicitud y detecta datos faltantes.
4. AgroBot consulta las reglas de negocio de Agrocapital.
5. AgroBot revisa documentos recibidos por Telegram cuando existan.
6. AgroBot consulta contexto FIRA cuando necesita validar informacion sectorial.
7. Supabase guarda lead, cotizacion, score, documentos faltantes y siguiente accion.
8. AgroBot genera resumen para el asesor.
9. Gmail envia la salida operativa al equipo comercial.

La integracion de Telegram queda a cargo de otro integrante del equipo. El
contrato esperado para este modulo es recibir los datos del prospecto ya
estructurados o una conversacion que el agente pueda diagnosticar.

## Revision de documentos

El modulo de documentos sigue el patron del `agent_demo.py` del starter kit:
recibe un evento de documento, valida existencia/tipo/datos esperados y emite un
reporte accionable. En AgroBot no se usa S3 ni OCR pesado por default; Telegram
debe entregar el archivo descargado o texto extraido.

Entrada esperada desde Telegram:

- `nombre_prospecto`
- `producto_sugerido`
- `documentos`: lista con `tipo`, `archivo_local` o `texto`
- `datos_esperados`: RFC, nombre, monto u otros datos a verificar

Salida:

- estado documental: `completo`, `incompleto` o `requiere_revision`
- documentos faltantes
- datos verificados
- siguiente accion

## Salida por Gmail

AgroBot usa la API de Gmail con OAuth y el permiso `gmail.send`. Para la demo:

1. Habilitar Gmail API en Google Cloud.
2. Configurar pantalla de consentimiento OAuth.
3. Crear un OAuth Client de tipo Desktop app.
4. Descargar el JSON como `credentials.json` en la raiz del repo.
5. Ejecutar `python examples/gmail_send_example.py` para generar `token.json`.

`credentials.json` y `token.json` estan ignorados por Git porque contienen
secretos locales.

## Datos minimos para Supabase

Tabla sugerida `leads`:

- `id`
- `nombre`
- `telefono`
- `correo`
- `municipio`
- `estado`
- `actividad`
- `destino_credito`
- `monto_solicitado`
- `producto_sugerido`
- `score_oportunidad`
- `prioridad`
- `riesgo_abandono`
- `documentos_faltantes`
- `siguiente_accion`
- `resumen_asesor`
- `created_at`
- `updated_at`

Tabla sugerida `cotizaciones`:

- `id`
- `lead_id`
- `producto`
- `monto`
- `plazo_referencial`
- `comisiones_referenciales`
- `cat_referencial`
- `fuente_producto`
- `contexto_fira`
- `nota`
- `created_at`

## Variables de entorno

Ver `.env.example`.

## Nota sobre FIRA

FIRA se usa como fuente de contexto publico o API si el equipo obtiene
credenciales. AgroBot no debe prometer aprobacion de credito.
