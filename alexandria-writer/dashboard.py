#!/usr/bin/env python3
"""
Alexandria Writer — Dashboard Editorial v3
===========================================
Interfaz visual para navegar los resultados del pipeline v3.

Uso:
  pip install streamlit
  streamlit run alexandria-writer/dashboard.py

Desde la raíz del proyecto:
  streamlit run alexandria-writer/dashboard.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ─── Path setup ───
WRITER_DIR = Path(__file__).parent
CORE_DIR = WRITER_DIR / "core"
PROJECT_ROOT = WRITER_DIR.parent
sys.path.insert(0, str(CORE_DIR))

try:
    import streamlit as st
except ImportError:
    print("Streamlit no instalado. Ejecutá: pip install streamlit")
    sys.exit(1)

from config_v3 import ProyectoPaths, listar_autores, listar_libros_de_autor

# ─── Page config ───
st.set_page_config(
    page_title="Alexandria Writer · Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS mínimo ───
st.markdown("""
<style>
.metric-card {
    background: #1e293b; border-radius: 8px; padding: 16px;
    margin: 4px 0; border-left: 3px solid #3b82f6;
}
.hallazgo-critico { border-left-color: #ef4444; }
.hallazgo-fortaleza { border-left-color: #22c55e; }
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.75rem; font-weight: 600; margin-right: 4px;
}
.badge-critico { background: #7f1d1d; color: #fca5a5; }
.badge-alto { background: #78350f; color: #fcd34d; }
.badge-medio { background: #1e3a5f; color: #93c5fd; }
.badge-fortaleza { background: #14532d; color: #86efac; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers de carga ─────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def cargar_hallazgos(paths_tuple) -> List[Dict]:
    paths = ProyectoPaths(*paths_tuple)
    ruta = paths.hallazgos_path()
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=30)
def cargar_metricas(paths_tuple) -> Dict:
    paths = ProyectoPaths(*paths_tuple)
    ruta = paths.metricas_editoriales_path()
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=30)
def cargar_backlog(paths_tuple) -> List[Dict]:
    paths = ProyectoPaths(*paths_tuple)
    ruta = paths.backlog_path()
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("backlog", [])


@st.cache_data(ttl=30)
def cargar_riesgos(paths_tuple) -> List[Dict]:
    paths = ProyectoPaths(*paths_tuple)
    ruta = paths.riesgos_detectados_path()
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("riesgos", [])


@st.cache_data(ttl=30)
def cargar_benchmark(paths_tuple) -> Dict:
    paths = ProyectoPaths(*paths_tuple)
    ruta = paths.benchmark_path()
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def guardar_decision(paths: ProyectoPaths, hallazgo_id: str, decision: str, nota: str = "") -> bool:
    """Persiste la decisión del autor en decisiones_autor.json dentro de m1_diagnostico."""
    ruta = paths.m1_diagnostico / "decisiones_autor.json"
    decisiones: Dict = {}
    if ruta.exists():
        with open(ruta, encoding="utf-8") as f:
            decisiones = json.load(f)
    decisiones[hallazgo_id] = {
        "decision": decision,
        "nota": nota,
        "timestamp": datetime.now().isoformat(),
    }
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(decisiones, f, indent=2, ensure_ascii=False)
    return True


def cargar_decisiones(paths: ProyectoPaths) -> Dict:
    ruta = paths.m1_diagnostico / "decisiones_autor.json"
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


# ─── Sidebar: selección de proyecto ──────────────────────────────────────────

with st.sidebar:
    st.title("📚 Alexandria Writer")
    st.caption("Dashboard Editorial v3")
    st.divider()

    autores = listar_autores()
    if not autores:
        st.warning("No hay autores registrados en `docs/Autores/`.")
        st.stop()

    autor_sel = st.selectbox("Autor", autores)
    libros = listar_libros_de_autor(autor_sel)

    if not libros:
        st.warning(f"No hay proyectos para `{autor_sel}`.")
        st.stop()

    libro_sel = st.selectbox("Libro / Proyecto", libros)

    paths = ProyectoPaths(autor=autor_sel, libro_id=libro_sel)
    paths_key = (autor_sel, libro_sel)

    st.divider()
    st.caption(f"Ruta: `{paths.proyecto_dir.relative_to(PROJECT_ROOT)}`")

    pagina = st.radio(
        "Sección",
        ["📊 Métricas", "🔍 Hallazgos", "📋 Backlog", "⚠️ Riesgos",
         "📈 Benchmark", "✅ Decisiones", "📄 Entregables"],
        label_visibility="collapsed",
    )

# ─── Carga de datos ───────────────────────────────────────────────────────────

hallazgos = cargar_hallazgos(paths_key)
metricas = cargar_metricas(paths_key)
backlog = cargar_backlog(paths_key)
riesgos = cargar_riesgos(paths_key)
benchmark = cargar_benchmark(paths_key)
decisiones = cargar_decisiones(paths)

# ─── Header ───────────────────────────────────────────────────────────────────

st.title(f"📖 {libro_sel}")
st.caption(f"Autor: {autor_sel} · {len(hallazgos)} hallazgos")

if not hallazgos and not metricas:
    st.info("Aún no hay datos para este proyecto. Ejecutá el pipeline v3 primero.")
    st.code(f"python core/pipeline_maestro_v3.py --autor {autor_sel} --libro {libro_sel}")
    st.stop()


# ─── MÉTRICAS ─────────────────────────────────────────────────────────────────

if pagina == "📊 Métricas":
    st.header("Métricas Editoriales")

    if metricas:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Gravedad Editorial", f"{metricas.get('gravedad_editorial', 0):.2f} / 5")
        c2.metric("Estabilidad de Voz", f"{metricas.get('estabilidad_voz', 0):.0%}")
        c3.metric("Total Hallazgos", metricas.get("total_hallazgos", 0))
        c4.metric("Alta Severidad (≥3)", metricas.get("hallazgos_severidad_alta", 0))

        st.divider()
        c5, c6 = st.columns(2)
        c5.metric("Densidad Problemas", f"{metricas.get('densidad_problemas', 0):.1f} / 1000 palabras")
        c6.metric("Total Palabras (aprox.)", f"{metricas.get('total_palabras', 0):,}")

        # Estado semáforo
        gravedad = metricas.get("gravedad_editorial", 0)
        voz = metricas.get("estabilidad_voz", 0)
        if gravedad < 2.0 and voz >= 0.80:
            st.success("✅ El libro está en buen estado editorial.")
        elif gravedad < 3.0 and voz >= 0.65:
            st.warning("⚠️ El libro necesita trabajo focalizado antes de publicar.")
        else:
            st.error("🔴 El libro requiere revisión estructural antes de publicar.")
    else:
        st.info("Ejecutá M1 para ver las métricas.")

    # Densidad por capítulo
    densidad_path = paths.m1_diagnostico / "densidad_problemas_por_capitulo.md"
    if densidad_path.exists():
        st.subheader("Densidad por Capítulo")
        st.markdown(densidad_path.read_text(encoding="utf-8"))


# ─── HALLAZGOS ────────────────────────────────────────────────────────────────

elif pagina == "🔍 Hallazgos":
    st.header("Hallazgos Editoriales")

    if not hallazgos:
        st.info("Ejecutá M1 para generar hallazgos.")
        st.stop()

    # Filtros
    col1, col2, col3 = st.columns(3)
    tipos_disponibles = sorted({h.get("tipo", "?") for h in hallazgos})
    tipo_filtro = col1.multiselect("Tipo", tipos_disponibles, default=tipos_disponibles)
    sev_min = col2.slider("Severidad mínima", 1, 5, 1)
    solo_sin_decision = col3.checkbox("Solo sin decisión", value=False)

    filtrados = [
        h for h in hallazgos
        if h.get("tipo") in tipo_filtro
        and h.get("severidad", 1) >= sev_min
        and (not solo_sin_decision or h.get("id") not in decisiones)
    ]
    filtrados = sorted(filtrados, key=lambda h: -(h.get("severidad", 1) * h.get("confianza", 0)))

    st.caption(f"Mostrando {len(filtrados)} de {len(hallazgos)} hallazgos")

    for h in filtrados[:50]:
        sev = h.get("severidad", 1)
        tipo = h.get("tipo", "?")
        color = "critico" if sev >= 4 else "alto" if sev == 3 else "fortaleza" if tipo == "fortaleza" else "medio"

        dec = decisiones.get(h.get("id", ""), {})
        dec_label = {"aceptado": "✅", "rechazado": "❌", "modificado": "✏️"}.get(dec.get("decision", ""), "")

        with st.expander(
            f"{dec_label} **{h.get('id')}** · {tipo.upper()} · Sev {sev}/5 · {h.get('descripcion', '')[:80]}…"
        ):
            cols = st.columns([3, 1])
            with cols[0]:
                if h.get("cita_textual"):
                    st.markdown(f"> *{h['cita_textual'][:300]}*")
                st.markdown(f"**Hallazgo:** {h.get('descripcion', '')}")
                if h.get("intervencion_sugerida"):
                    st.markdown(f"**Intervención:** {h.get('intervencion_sugerida', '')}")
                st.caption(f"Chunk: {h.get('chunk_ref')} · Pág. {h.get('pagina_aprox')} · Confianza: {h.get('confianza', 0):.0%}")
            with cols[1]:
                nueva_dec = st.selectbox(
                    "Decisión",
                    ["pendiente", "aceptado", "rechazado", "modificado"],
                    index=["pendiente", "aceptado", "rechazado", "modificado"].index(
                        dec.get("decision", "pendiente")
                    ),
                    key=f"dec_{h.get('id')}",
                )
                nota = st.text_input("Nota", value=dec.get("nota", ""), key=f"nota_{h.get('id')}")
                if st.button("Guardar", key=f"btn_{h.get('id')}"):
                    guardar_decision(paths, h.get("id"), nueva_dec, nota)
                    cargar_decisiones.clear() if hasattr(cargar_decisiones, "clear") else None
                    st.success("Guardado")
                    st.rerun()


# ─── BACKLOG ──────────────────────────────────────────────────────────────────

elif pagina == "📋 Backlog":
    st.header("Backlog Priorizado")

    if not backlog:
        st.info("Ejecutá M4 para generar el backlog.")
        st.stop()

    # Resumen
    pendientes = [b for b in backlog if b.get("estado") == "pendiente"]
    st.caption(f"{len(pendientes)} ítems pendientes · {len(backlog)} total")

    for item in backlog[:40]:
        sev = item.get("severidad", 1)
        score = item.get("score_editorial", 0)
        rank = item.get("rank", "?")
        tipo = item.get("tipo", "?")
        dec = decisiones.get(item.get("id", ""), {})
        dec_ico = {"aceptado": "✅", "rechazado": "❌", "modificado": "✏️"}.get(dec.get("decision", ""), "⬜")

        with st.expander(
            f"{dec_ico} **#{rank}** · [{item.get('id')}] {tipo.upper()} · "
            f"Score {score:.2f} · {item.get('descripcion', '')[:70]}…"
        ):
            st.markdown(f"**Descripción:** {item.get('descripcion', '')}")
            if item.get("cita_textual"):
                st.markdown(f"> *{item['cita_textual'][:200]}*")
            if item.get("intervencion_sugerida"):
                st.markdown(f"**Acción:** {item.get('intervencion_sugerida', '')}")
            st.caption(
                f"Chunk: {item.get('chunk_ref')} · "
                f"Sev: {sev}/5 · Confianza: {item.get('confianza', 0):.0%}"
            )


# ─── RIESGOS ──────────────────────────────────────────────────────────────────

elif pagina == "⚠️ Riesgos":
    st.header("Control de Riesgo")

    if not riesgos:
        st.info("Ejecutá M5 para ver el análisis de riesgo.")
        st.stop()

    activos = [r for r in riesgos if r.get("activado")]
    if activos:
        st.error(f"🔴 {len(activos)} guardián(es) activado(s)")
    else:
        st.success("✅ Todos los guardianes en verde")

    for r in riesgos:
        activado = r.get("activado", False)
        icono = "🔴" if activado else "✅"
        with st.expander(f"{icono} **{r.get('tipo', '?').replace('_', ' ').title()}**"):
            st.markdown(r.get("descripcion", ""))
            if activado and r.get("recomendacion"):
                st.warning(f"**Acción requerida:** {r.get('recomendacion')}")
            afectados = r.get("hallazgos_afectados", [])
            if afectados:
                st.caption(f"Hallazgos afectados: {', '.join(afectados[:10])}")


# ─── BENCHMARK ────────────────────────────────────────────────────────────────

elif pagina == "📈 Benchmark":
    st.header("Benchmarking y Posicionamiento")

    if not benchmark:
        st.info("Ejecutá M6 para ver el benchmark.")
        st.stop()

    posicion = benchmark.get("posicion", {})
    resumen = posicion.get("resumen", {})

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Percentil Editorial",
        f"{resumen.get('percentil_editorial_estimado', '?')}º",
    )
    c2.metric(
        "Listo para Lanzar",
        "Sí ✅" if resumen.get("listo_para_lanzar") else "No ❌",
    )
    c3.metric("Alta Severidad", resumen.get("hallazgos_alta_severidad", "?"))

    st.divider()
    grav = posicion.get("gravedad_editorial", {})
    voz = posicion.get("estabilidad_voz", {})
    dens = posicion.get("densidad_problemas", {})

    col1, col2, col3 = st.columns(3)
    col1.info(f"**Gravedad:** {grav.get('valor', 0):.2f} → {grav.get('label', '')}")
    col2.info(f"**Voz:** {voz.get('valor', 0):.0%} → {voz.get('label', '')}")
    col3.info(f"**Densidad:** {dens.get('valor', 0):.1f} → {dens.get('label', '')}")

    posic_path = paths.m6_benchmarking / "posicionamiento_relativo.md"
    if posic_path.exists():
        st.subheader("Análisis de Posicionamiento")
        st.markdown(posic_path.read_text(encoding="utf-8"))


# ─── DECISIONES ───────────────────────────────────────────────────────────────

elif pagina == "✅ Decisiones":
    st.header("Decisiones del Autor")

    total = len(hallazgos)
    con_decision = {k: v for k, v in decisiones.items() if v.get("decision") != "pendiente"}
    aceptados = sum(1 for v in con_decision.values() if v.get("decision") == "aceptado")
    rechazados = sum(1 for v in con_decision.values() if v.get("decision") == "rechazado")
    modificados = sum(1 for v in con_decision.values() if v.get("decision") == "modificado")
    pendientes_n = total - len(con_decision)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pendientes", pendientes_n)
    c2.metric("Aceptados ✅", aceptados)
    c3.metric("Rechazados ❌", rechazados)
    c4.metric("Modificados ✏️", modificados)

    if con_decision:
        st.divider()
        st.subheader("Registro de decisiones")
        for hid, dec in sorted(con_decision.items()):
            icon = {"aceptado": "✅", "rechazado": "❌", "modificado": "✏️"}.get(dec.get("decision"), "")
            nota = dec.get("nota", "")
            ts = dec.get("timestamp", "")[:16]
            st.markdown(f"{icon} **{hid}** — *{dec.get('decision')}* · {ts}" + (f" · Nota: {nota}" if nota else ""))

    st.divider()
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        if st.button("⬇️ Exportar decisiones como JSON"):
            st.download_button(
                "Descargar decisiones_autor.json",
                data=json.dumps(decisiones, indent=2, ensure_ascii=False),
                file_name=f"decisiones_autor_{libro_sel}.json",
                mime="application/json",
            )

    with col_exp2:
        if st.button("📄 Generar Plan de Edición (.md + .docx)"):
            try:
                from exportar_plan import ejecutar as exportar_plan
                with st.spinner("Generando plan…"):
                    ok = exportar_plan(autor_sel, libro_sel)
                if ok:
                    st.success("✅ Plan generado en `m7_output_profesional/plan_edicion_*.md` y `.docx`")
                else:
                    st.error("Sin hallazgos para exportar.")
            except Exception as e:
                st.error(f"Error: {e}")


# ─── ENTREGABLES ──────────────────────────────────────────────────────────────

elif pagina == "📄 Entregables":
    st.header("Entregables Finales")

    docs_m7 = [
        ("brief_final_ejecutivo.md", "⚡ Brief Final Ejecutivo"),
        ("diagnostico_desarrollo.md", "📋 Diagnóstico de Desarrollo"),
        ("plan_intervencion.md", "🗂️ Plan de Intervención"),
        ("estrategia_publicacion.md", "🚀 Estrategia de Publicación"),
        ("memo_adquisicion.md", "📨 Memo de Adquisición"),
    ]

    # También mostrar outputs del pipeline editorial (iteraciones)
    iter_dir = paths.proyecto_dir.parent.parent / "Proyectos" / libro_sel
    iteraciones = sorted(iter_dir.glob("iteracion_*/")) if iter_dir.exists() else []

    tab1, tab2 = st.tabs(["Pipeline v3 (M7)", "Pipeline Editorial (iteraciones)"])

    with tab1:
        disponibles = [(nombre, titulo) for nombre, titulo in docs_m7
                       if (paths.m7_output_profesional / nombre).exists()]
        if not disponibles:
            st.info("Ejecutá M7 para generar los entregables finales.")
        else:
            doc_sel = st.selectbox("Documento", [t for _, t in disponibles])
            nombre_sel = next(n for n, t in disponibles if t == doc_sel)
            contenido = (paths.m7_output_profesional / nombre_sel).read_text(encoding="utf-8")
            st.markdown(contenido)
            st.download_button(
                f"⬇️ Descargar {nombre_sel}",
                data=contenido,
                file_name=nombre_sel,
                mime="text/markdown",
            )

    with tab2:
        if not iteraciones:
            st.info("No hay iteraciones del pipeline editorial para este proyecto.")
        else:
            iter_nombres = [i.name for i in iteraciones]
            iter_sel = st.selectbox("Iteración", iter_nombres, index=len(iter_nombres) - 1)
            iter_path = iter_dir / iter_sel

            archivos_iter = list(iter_path.glob("*.md")) + list(iter_path.glob("*.json"))
            if not archivos_iter:
                st.info("La iteración no tiene archivos generados.")
            else:
                arch_nombres = [a.name for a in archivos_iter]
                arch_sel = st.selectbox("Archivo", arch_nombres)
                ruta_arch = iter_path / arch_sel
                contenido_arch = ruta_arch.read_text(encoding="utf-8")
                if arch_sel.endswith(".json"):
                    try:
                        st.json(json.loads(contenido_arch))
                    except Exception:
                        st.code(contenido_arch)
                else:
                    st.markdown(contenido_arch)
                st.download_button(
                    f"⬇️ Descargar {arch_sel}",
                    data=contenido_arch,
                    file_name=arch_sel,
                )
