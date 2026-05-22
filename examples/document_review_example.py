import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from agrobot_rules.document_validator import DocumentInput, DocumentReviewRequest, review_credit_documents


if __name__ == "__main__":
    result = review_credit_documents(
        DocumentReviewRequest(
            nombre_prospecto="Rancho La Esperanza",
            producto_sugerido="Credito Refaccionario",
            documentos=[
                DocumentInput(tipo="identificacion", texto="INE de Rancho La Esperanza"),
                DocumentInput(tipo="comprobante fiscal", texto="RFC: RLE010101ABC"),
                DocumentInput(tipo="cotizacion", texto="Cotizacion sistema de riego por 800000 MXN"),
            ],
            datos_esperados={"RFC": "RLE010101ABC"},
        )
    )
    print(result)
