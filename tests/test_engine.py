from agrobot_rules import ProspectInput, recommend_credit


def test_recommends_avio_for_insumos() -> None:
    result = recommend_credit(
        ProspectInput(
            destino_credito="insumos para el proximo ciclo agricola",
            actividad="maiz",
            documentos_recibidos=["identificacion", "comprobante fiscal"],
        )
    )

    assert result["producto_sugerido"] == "Credito de Habilitacion o Avio"
    assert result["fuente_producto"] == "Agrocapital"


def test_recommends_refaccionario_for_riego() -> None:
    result = recommend_credit(
        ProspectInput(
            destino_credito="sistema de riego y maquinaria",
            actividad="agricola",
            monto_solicitado=800_000,
            urgencia_dias=5,
            cliente_recurrente=True,
            documentos_recibidos=[
                "identificacion",
                "comprobante fiscal",
                "comprobante domicilio",
                "cotizacion",
            ],
        )
    )

    assert result["producto_sugerido"] == "Credito Refaccionario"
    assert result["prioridad"] == "Alta"


def test_recommends_prendario_when_inventory_guarantee_exists() -> None:
    result = recommend_credit(
        ProspectInput(
            destino_credito="comercializacion de cosecha",
            actividad="granos",
            tiene_inventario_garantia=True,
        )
    )

    assert result["producto_sugerido"] == "Credito Prendario"


def test_recommends_rural_for_small_town_without_clear_match() -> None:
    result = recommend_credit(
        ProspectInput(
            destino_credito="abrir negocio local",
            actividad="comercio rural",
            poblacion_menor_50000=True,
        )
    )

    assert result["producto_sugerido"] == "Financiamiento Rural"
