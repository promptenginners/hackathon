# Arquitectura: AgroBot

## Stack decidido

- BD: Supabase.
- Agente: LangChain.
- LLM: Gemini 3.1 Flash-Lite.
- Canal de entrada: interfaz o API interna.
- Salida: Gmail.
- Fuente externa: FIRA.
- Reglas de negocio: productos Agrocapital y contexto FIRA.

## API key

La API key de Gemini no debe guardarse en GitHub. Configurala en `.env` usando
la variable `GOOGLE_API_KEY`, tomando como base `.env.example`.

## Flujo principal

1. El prospecto o asesor captura la solicitud en la interfaz o API interna.
2. LangChain orquesta AgroBot.
3. Gemini interpreta la solicitud y detecta datos faltantes.
4. AgroBot consulta las reglas de negocio de Agrocapital.
5. AgroBot consulta contexto FIRA cuando necesita validar informacion sectorial.
6. Supabase guarda lead, cotizacion, score, documentos faltantes y siguiente accion.
7. AgroBot genera resumen para el asesor.
8. Gmail envia la salida operativa al equipo comercial.

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
