# Agentes archivados — versión en inglés (v1, mayo 2026)

Estos ocho agentes formaban el primer modelo de Alexandria Writer. Se escribieron en inglés y con el marco de **ficción comercial**: arcos de tres actos, *hero's journey*, *worldbuilding fantasy*, *dialogue tags*, *book launch* tipo Amazon.

Funcionan razonablemente bien para una novela de género en inglés. **No funcionan** para los libros que esta casa publica — ensayo, memoria, devocional, manual y poesía en español — y, peor, **homogenizan la voz del autor** porque están calibrados al promedio del best-seller anglosajón.

Quedan aquí como referencia histórica. No los invoca el sistema editorial actual. La nueva familia de agentes vive en `agents/editorial/` y se rige por el `MANIFIESTO_EDITORIAL.md` y por `skills/base_editorial.md`.

| Archivo legacy | Reemplazo en `agents/editorial/` |
|---|---|
| narrative-arch/writer-narrative-arch.md | 02_estructuralista_de_ensayo.md |
| character-dev/writer-character-dev.md | (no aplica para no-ficción; queda fuera) |
| dialogue/writer-dialogue.md | (no aplica para ensayo confesional; queda fuera) |
| style-tone/writer-style-tone.md | 03_editor_de_linea_es_mx.md |
| worldbuilding/writer-worldbuilding.md | (no aplica; queda fuera) |
| research/writer-research.md | (puede reactivarse si el libro lo pide; por ahora queda fuera) |
| marketing/writer-marketing.md | (movido a pipeline comercial opcional, no editorial) |
| audio/writer-audio.md | (utilidad, no agente editorial; se reactivará como herramienta) |

Si en el futuro la casa publica también narrativa en inglés, estos agentes pueden volver al flujo, pero pasados por el mismo Lector de Voz y el mismo Director Editorial: ningún agente trabaja sin `voz_autor.yaml` y ningún agente entrega directamente al autor sin el filtro de la casa.
