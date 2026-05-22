from agrobot_rules.document_validator import DocumentInput, DocumentReviewRequest, review_credit_documents


def test_review_documents_detects_missing_documents() -> None:
    result = review_credit_documents(
        DocumentReviewRequest(
            nombre_prospecto="Rancho La Esperanza",
            producto_sugerido="Credito Refaccionario",
            documentos=[
                DocumentInput(tipo="identificacion", texto="INE vigente"),
                DocumentInput(tipo="comprobante fiscal", texto="RFC: RLE010101ABC"),
            ],
            datos_esperados={"RFC": "RLE010101ABC"},
        )
    )

    assert result["estado_documental"] == "incompleto"
    assert "cotizacion" in result["documentos_faltantes"]
    assert result["datos_verificados"]["RFC"] is True


def test_review_documents_marks_complete_when_all_required_present() -> None:
    result = review_credit_documents(
        DocumentReviewRequest(
            nombre_prospecto="Agro Norte",
            documentos=[
                DocumentInput(tipo="identificacion", texto="INE"),
                DocumentInput(tipo="comprobante fiscal", texto="RFC ANO010101ZZZ"),
                DocumentInput(tipo="comprobante domicilio", texto="Domicilio fiscal"),
                DocumentInput(tipo="cotizacion", texto="Cotizacion maquinaria"),
                DocumentInput(tipo="documentos del predio", texto="Predio agricola"),
                DocumentInput(tipo="estados financieros", texto="Balance general"),
            ],
        )
    )

    assert result["estado_documental"] == "completo"
    assert result["documentos_faltantes"] == []
