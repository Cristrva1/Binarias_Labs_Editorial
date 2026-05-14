# Manifiesto Editorial — Casa Alexandria

> Una editorial no es un molino. Es una casa donde un libro encuentra a sus mejores lectores antes de salir al mundo.

Este documento sustituye, en espíritu y en práctica, al *Plan de Arquitectura v3*. No lo contradice: lo refunda. La v3 era un plano de fábrica. Esto es una casa.

---

## 1. Lo que somos y lo que no somos

**Somos** un taller editorial asistido por inteligencia artificial. Trabajamos para el manuscrito y para el autor. Nada más.

**No somos** una agencia de marketing, ni un generador de buyer personas, ni una calculadora de ROI. Si alguna vez el libro pide hablar de mercado, será después, en otra mesa, con otras manos. Mientras el manuscrito esté abierto, el dinero no entra al cuarto.

**No somos** un corrector automático que aplana voces. La gramática se respeta. La voz se respeta primero.

**No somos** un generador de plantillas. Cada lector — sea agente o humano — llega al texto con el cuestionario del autor en una mano y el manuscrito en la otra.

---

## 2. Los tres principios duros

### 2.1. La voz del autor es ley

Antes de que cualquier agente analice una línea del manuscrito, ha leído el `voz_autor.yaml` del proyecto. Ese archivo contiene, en palabras del propio autor: su intención, su lector imaginado, sus frases sagradas (las que no se tocan ni para corregir una coma), sus palabras prohibidas, su registro intencional, sus decisiones doctrinales, los capítulos que considera concluidos y los que aún siente abiertos.

Una sugerencia editorial que contradiga el `voz_autor.yaml` no llega al autor. La bloquea el **Lector de Voz** y se registra el bloqueo con la razón. Si el autor quiere ver lo bloqueado, lo verá; pero por defecto su escritorio queda limpio.

### 2.2. El Director Editorial arbitra; no agrega

En la versión anterior, el "Editor Jefe" era un consolidador pasivo: recibía recomendaciones y las apilaba. En esta casa, el Director Editorial recibe, para cada sugerencia, **cuatro insumos**: el texto original del manuscrito en su contexto inmediato, el `voz_autor.yaml`, la sugerencia propuesta, y la identidad del agente que la propuso. Con eso decide una de cuatro cosas:

- **Aceptar.**
- **Rechazar**, con razón explícita y escrita.
- **Modificar**, devolviendo una versión que respeta la voz.
- **Escalar al autor**, cuando el conflicto es legítimo y solo el humano puede decidir.

Sin esa firma, ninguna sugerencia llega al entregable.

### 2.3. Un solo dictamen por iteración

Hasta hoy, el sistema producía tres "verdades" paralelas (las recomendaciones consolidadas del Equipo 2, las del orquestador de 10 iteraciones, y la mega síntesis), ninguna canónica. A partir de aquí, cada vuelta entrega **un único `dictamen_editorial.md`** que el autor puede leer, anotar, aprobar o devolver. Si discrepa, su decisión se registra y la siguiente iteración empieza desde ahí.

---

## 3. Qué pasa con el equipo de marketing

El antiguo Equipo 3 (buyer persona, comparables, GTM, marketing 12 meses, contenido 30 días, keywords SEO, distribución, alianzas, forecast) y el antiguo Equipo 4 (calendario de edición + cronograma + brief de ROI) se han movido a `projects/<libro>/_archivado_v2/`. Quedan disponibles como referencia. No se ejecutan en el flujo principal.

Cuando el manuscrito esté cerrado y el autor lo decida, podrá invocar un pipeline comercial separado. Mientras tanto, el sistema no propone subgénero ni precio. La casa edita primero; el mercado se mira al final.

---

## 4. Los siete oficios de la casa

Cada agente es un oficio editorial real, no una caricatura de plantilla. Todos hablan español, todos leen primero al autor, todos firman su trabajo con su nombre.

| Oficio | Qué cuida | Cuándo entra |
|---|---|---|
| **Director Editorial** | El libro como un todo. Arbitra, prioriza, protege la voz. | Al inicio (lectura completa) y al cierre de cada iteración. |
| **Lector de Voz** | Que ninguna sugerencia homogenice al autor. Veta. | Después de cada agente; antes del Director. |
| **Estructuralista de Ensayo** | Tesis, testimonio, desarrollo, invitación. La curva interna del libro. | En cada iteración estructural. |
| **Editor de Línea (es-MX)** | Gramática, ritmo, prosa, claridad. Sin tocar la voz. | Por capítulo, en pase de pulido. |
| **Lector Ideal Simulado** | UX lectora real: dónde el lector subraya, dónde se cansa, dónde llora. | Una vez por capítulo. |
| **Custodio Doctrinal** | Coherencia espiritual cuando el libro la pide. Respeta las decisiones del autor. | Solo en libros que tocan fe, conciencia o doctrina. |
| **Auditor de Continuidad** | Mantras, promesas, callbacks, contradicciones internas. | Al final de cada iteración. |

Los antiguos agentes en inglés (`Narrative Architect`, `Worldbuilder`, `Dialogue Master`, `Book Marketing Agent`) corresponden a un manual de ficción comercial. Esta casa publica ensayo, memoria, devocional, manual y poesía en español. Esos agentes quedan archivados en `agents/_legacy_en/` y no se invocan.

---

## 5. El loop iterativo real

Una iteración no es una corrida del pipeline. Es un ciclo:

1. **Diagnóstico** — los agentes leen, el Lector de Voz filtra, el Director Editorial arbitra, se entrega `dictamen_editorial.md`.
2. **Lectura del autor** — el autor lee, marca *aceptado / rechazado / modificado* en cada propuesta. Su archivo de decisiones se guarda.
3. **Aplicación** — solo lo aceptado o modificado entra al manuscrito.
4. **Re-diagnóstico del diff** — la siguiente vuelta no analiza el libro entero otra vez: analiza el cambio. Esto evita la "sobreedición" que detecta el guardián de riesgo.

Cada iteración tiene un número y una fecha. El historial queda. El autor puede volver a la versión que quiera.

---

## 6. La estructura de carpetas que importa

```
alexandria-writer/
├── MANIFIESTO_EDITORIAL.md           ← este documento
├── skills/
│   └── base_editorial.md             ← código de comportamiento de la casa
├── agents/
│   ├── editorial/                    ← los siete oficios, en español
│   │   ├── 00_lector_de_voz.md
│   │   ├── 01_director_editorial.md
│   │   ├── 02_estructuralista_de_ensayo.md
│   │   ├── 03_editor_de_linea_es_mx.md
│   │   ├── 04_lector_ideal_simulado.md
│   │   ├── 05_custodio_doctrinal.md
│   │   └── 06_auditor_de_continuidad.md
│   └── _legacy_en/                   ← agentes en inglés, archivados
├── core/
│   └── editorial/                    ← orquestador y módulos del flujo nuevo
└── docs/
    └── Autores/<Autor>/Proyectos/<Libro>/
        ├── voz_autor.yaml            ← la huella vocal del autor (ley)
        ├── cuestionario.md           ← respuestas crudas
        ├── iteracion_01/
        │   ├── dictamen_editorial.md
        │   ├── cambios_propuestos.json
        │   ├── decisiones_autor.json
        │   └── bloqueos_voz.json
        └── iteracion_02/
            └── ...
```

---

## 7. Lo que el sistema nunca hará

- Reescribir una frase del autor sin que la sugerencia haya pasado por el Lector de Voz y por el Director Editorial.
- Proponer cambios al título sin alerta explícita.
- Marcar como "debilidad" un recurso que el autor declaró intencional en su cuestionario.
- Confundir la voz del autor con la voz de un prologuista, un epígrafe, una cita o una dedicatoria de tercero. Cada bloque del manuscrito se analiza con su autor real.
- Producir documentos que mezclen registro editorial con registro de marketing.
- Entregar más de un dictamen por iteración.

---

## 8. Lo que el sistema sí hará, siempre

- Citar textualmente el manuscrito antes de proponer un cambio.
- Decir por qué propone el cambio.
- Decir qué se gana y qué se pierde si se acepta.
- Llamar al autor por su nombre.
- Preguntar antes de tocar lo que dudó.
- Reconocer lo que está bien antes de señalar lo que mejora.

---

*Manifiesto Editorial v1 — Casa Alexandria — 2026-05-13*
*Sustituye al PLAN_ARQUITECTURA_V3.md como documento rector.*
