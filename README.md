# AgroBot Agrocapital

Repositorio para el hackathon de agentes inteligentes Build Day 2026.

Este modulo contiene la parte de reglas de negocio para recomendar productos
financieros de Agrocapital y entregar contexto publico de FIRA al agente.

## Estructura

- `src/agrobot_rules/catalog.py`: catalogo de productos y servicios de Agrocapital.
- `src/agrobot_rules/engine.py`: motor de recomendacion, scoring y siguiente accion.
- `src/agrobot_rules/tools.py`: tools listas para conectar con LangChain.
- `src/agrobot_rules/fira_client.py`: cliente preparado para una API FIRA futura.
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
