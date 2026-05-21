from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProspectInput:
    destino_credito: str
    actividad: str
    poblacion_menor_50000: bool = False
    tiene_inventario_garantia: bool = False
    monto_solicitado: float | None = None
    urgencia_dias: int | None = None
    cliente_recurrente: bool = False
    documentos_recibidos: list[str] = field(default_factory=list)
    dias_desde_ultimo_contacto: int | None = None
