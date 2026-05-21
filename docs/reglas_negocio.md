# Reglas de negocio: AgroBot Agrocapital + FIRA

## Principio

Agrocapital es la fuente principal para recomendar productos financieros y
generar una cotizacion preliminar.
FIRA se usa como fuente de contexto publico y sectorial, no como aprobador
automatico de credito.

## Productos Agrocapital

- Credito Refaccionario: maquinaria, terrenos agricolas, infraestructura, equipamiento y sistemas de riego.
- Capital de Trabajo: flujo efectivo para operacion, mantenimiento y administracion de proyectos agricolas, industriales, ganaderos y de pesca.
- Credito de Habilitacion o Avio: cultivos como maiz, frijol, trigo, papa, sorgo, garbanzo y frutales.
- Arrendamiento Puro: adquisicion o reposicion de parque vehicular.
- Financiamiento Rural: actividades economicas en poblaciones menores a 50,000 habitantes.
- Credito Empresarial: creacion, desarrollo y fortalecimiento de empresas agroindustriales.
- Credito Prendario: comercializacion de cosechas e inventarios como granos, semillas y fertilizantes.

## Salida del motor

El motor devuelve:

- Producto sugerido.
- Fuente del producto.
- Contexto FIRA.
- Plazo, comisiones y CAT cuando Agrocapital los publica.
- Datos base para cotizacion preliminar.
- Documentos faltantes.
- Score de oportunidad.
- Prioridad.
- Riesgo de abandono.
- Siguiente accion comercial.
- Resumen para asesor o envio por Gmail.

## Nota para demo

La respuesta siempre debe presentarse como prediagnostico comercial. No se debe
prometer aprobacion de credito.
