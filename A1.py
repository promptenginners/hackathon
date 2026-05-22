import os
from dotenv import load_dotenv
from google import types

# Carga la variable GEMINI_API_KEY desde el archivo .env
load_dotenv()

def gemini(prompt: str) -> str:
    """
    responde con simplesa
    """
    try:
        # Inicializa el cliente oficial
        client = genai.Client()
        
        # Realiza la petición al modelo rápido y eficiente por defecto
        response = client.models.generate_content(
            model='google_genai:gemini-3.1-flash-lite',
            contents=prompt,
            temperature=0.1
        )
        return response.text
    except Exception as e:
        return f"Error crítico al conectar con Gemini: {e}"

def main():
    # El prompt o pregunta que desea enviarle a su agente
    pregunta = "top 3 paises mas avanzazon economicamente"
    
    print("Procesando consulta con Gemini, espere un momento...")
    resultado = gemini(pregunta)
    
    print("\n Respuesta del Agente ")
    print(resultado)

if __name__ == "__main__":
    main()

