# Base de Datos de Comparables — Alexandria Writer v3

Esta carpeta contiene los libros de referencia por género/subgénero,
usados por `m6_benchmarking.py` para calibrar el percentil editorial.

## Estructura

Cada género tiene su propio archivo JSON:

```
data/comparables/
├── README.md                    ← este archivo
├── autoayuda_espiritual.json    ← ejemplo incluido
├── ensayo_personal.json
├── desarrollo_personal.json
├── memoirs.json
└── no_ficcion_narrativa.json
```

## Formato de cada archivo

```json
{
  "genero": "nombre del género",
  "descripcion": "descripción breve",
  "comparables": [
    {
      "titulo": "Título del libro",
      "autor": "Nombre del autor",
      "editorial": "Editorial",
      "año": 2022,
      "paginas": 240,
      "palabras_aprox": 65000,
      "metricas_referencia": {
        "gravedad_editorial_estimada": 1.8,
        "estabilidad_voz_estimada": 0.85,
        "densidad_problemas_estimada": 2.5
      },
      "notas": "Por qué es comparable y qué representa en el mercado."
    }
  ]
}
```

## Cómo agregar comparables

1. Editá o creá el archivo JSON correspondiente al género.
2. Las métricas `*_estimada` son estimaciones editoriales (no métricas del sistema).
3. Usá libros reales y publicados como referencia; no inventés títulos.

## Importante

Estos datos son privados del proyecto. No subir a repositorios públicos
sin revisar que no contengan información sensible de autores.
