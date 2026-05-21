from __future__ import annotations

import os
from typing import Any

import requests


class FiraApiUnavailable(RuntimeError):
    pass


class FiraClient:
    """Cliente delgado para una API privada futura de FIRA."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("FIRA_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("FIRA_API_KEY")

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.configured:
            raise FiraApiUnavailable(
                "FIRA_BASE_URL and FIRA_API_KEY are not configured. Use reglas locales/RAG para la demo."
            )

        response = requests.get(
            f"{self.base_url}/{path.lstrip('/')}",
            params=params,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=8,
        )
        response.raise_for_status()
        return response.json()


def public_fira_context() -> dict[str, Any]:
    return {
        "rol": "FIRA opera como banca de segundo piso mediante intermediarios financieros autorizados.",
        "usos_demo": [
            "tipos de credito",
            "actividades financiables",
            "intermediarios financieros",
            "Agrocostos e informacion sectorial",
        ],
        "limite": "No se asume aprobacion automatica ni API publica transaccional.",
    }
