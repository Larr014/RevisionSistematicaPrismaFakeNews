#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visor interactivo — RSL Intenciones Comunicativas en Publicaciones Digitales (2020-2026)
Autor: Mg. Luis Rojas Rubio 

Ejecutar localmente:
    streamlit run app.py

Deploy: Streamlit Community Cloud → conectar repo GitHub, main file = app.py
"""

import json
import re
import pathlib
from collections import Counter

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    _WC = True
except ImportError:
    _WC = False

# ── Config ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RSL · Intenciones Comunicativas 2020–2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = pathlib.Path(__file__).parent  # root del repositorio

# ── Paleta ────────────────────────────────────────────────────────────────────
C = {
    "blue":   "#2563EB", "green":  "#16A34A", "red":    "#DC2626",
    "orange": "#EA580C", "purple": "#7C3AED", "teal":   "#0D9488",
    "gray":   "#6B7280", "yellow": "#CA8A04", "pink":   "#DB2777",
    "indigo": "#4F46E5",
}
SEQ_BLUES   = px.colors.sequential.Blues
QUAL_COLORS = [C["blue"], C["green"], C["red"], C["orange"], C["purple"],
               C["teal"], C["yellow"], C["pink"], C["indigo"], C["gray"]]

# ── Stopwords ─────────────────────────────────────────────────────────────────
SW = {
    "de","la","el","en","y","a","los","del","se","las","por","un","con","una",
    "para","es","al","lo","que","su","le","da","no","o","este","más","pero",
    "sus","ya","sobre","entre","cuando","todo","esta","ser","son","dos","también",
    "fue","había","era","muy","sin","hasta","hay","donde","han","puede","está",
    "sido","tiene","como","si","me","mi","nos","the","of","and","to","in","a",
    "is","for","on","with","are","that","this","an","by","from","at","be","as",
    "we","our","it","using","based","model","paper","study","results","method",
    "approach","proposed","show","new","two","used","data","analysis","detection",
    "classification","also","work","fake","news",
}

# ── Loaders ───────────────────────────────────────────────────────────────────
@st.cache_data
def load_json(path: pathlib.Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_corpus():
    raw = load_json(BASE / "clasificacion_pdfs_completos.json")
    return raw.get("articulos", [])

@st.cache_data
def load_tabla(name: str):
    return load_json(BASE / "tablas" / name)

# ── Labels ────────────────────────────────────────────────────────────────────
METODOS_L = {
    "M1_LogisticRegression":"Logistic Regression","M2_NaiveBayes":"Naive Bayes",
    "M3_DecisionTree":"Decision Tree","M4_GradientBoosting":"Gradient Boosting",
    "M5_KNN":"KNN","M6_SVM":"SVM","M7_NeuralNetwork":"Neural Network",
    "M8_RandomForest":"Random Forest","M9_NLP_Traditional":"NLP Tradicional",
    "M10_DeepLearning":"Deep Learning","M11_LSTM":"LSTM",
    "M12_Transformer":"Transformer","M13_BERT":"BERT",
    "M14_GraphNetwork":"Graph Network","M15_Ensemble":"Ensemble",
    "M16_Clustering":"Clustering","M17_TopicModeling":"Topic Modeling",
    "M18_SemanticAnalysis":"Semantic Analysis",
    "M19_SentimentAnalysis":"Sentiment Analysis",
    "M20_StylometryAnalysis":"Stylometry","M21_HybridMethod":"Hybrid Method",
}
INTENC_L = {
    "I1_FakeNews":"Fake News","I2_Manipulation":"Manipulación",
    "I3_Misinformation":"Misinformación","I4_Satire":"Sátira",
    "I5_Rumors":"Rumores","I6_BotActivity":"Bot Activity",
    "I7_EmotionAnalysis":"Análisis Emocional","I8_PolarityAnalysis":"Polaridad",
    "I9_ToxicContent":"Contenido Tóxico","I10_Deepfakes":"Deepfakes",
    "I11_Coordinated_Behavior":"Comportamiento Coordinado",
    "I12_SuspiciousActivity":"Actividad Sospechosa",
    "I13_Credibility_Assessment":"Credibilidad",
}

# ── Flatten artículo ──────────────────────────────────────────────────────────
def flatten(a: dict) -> dict:
    cl = a.get("clasificacion", {})
    vp = cl.get("variables_principales", {})
    va = cl.get("variables_adicionales", {})
    return {
        "id":          a.get("id", ""),
        "titulo":      a.get("titulo", "Sin título"),
        "autores":     ", ".join(a.get("autores", [])) or "—",
        "year":        a.get("year"),
        "abstract":    a.get("abstract", ""),
        "doi":         a.get("doi", ""),
        "relevancia":  a.get("relevancia_general", 0.0),
        "metodos_esp": vp.get("metodos_especifico", []),
        "metodos_gen": vp.get("metodos_general", []),
        "metricas":    vp.get("metricas", []),
        "intenciones": vp.get("intenciones", []),
        "datasets":    vp.get("dataset", []),
        "dataset_info":vp.get("dataset_info", []),
        "plataforma":  va.get("plataforma", []),
        "linguistica": va.get("linguistica", []),
        "metodologica":va.get("metodologica", []),
        "hallazgos":   a.get("hallazgos_nuevos", []),
    }

# ── Cargar y aplanar corpus ───────────────────────────────────────────────────
articulos_raw = load_corpus()
df_all = [flatten(a) for a in articulos_raw]
incluidos = [r for r in df_all if r["relevancia"] >= 0.4]

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.image("https://img.shields.io/badge/Corpus-324%20artículos-2563EB?style=flat-square")
st.sidebar.title("📚 RSL Intenciones Comunicativas")
st.sidebar.caption("Publicaciones digitales · 2020–2026")
st.sidebar.divider()

vista = st.sidebar.radio(
    "Vista de datos",
    ["Incluidos (324)", "Todos con PDF (549)", "Excluidos E3 (225)"],
    index=0,
)
if vista == "Incluidos (324)":
    base_filtro = incluidos
elif vista == "Todos con PDF (549)":
    base_filtro = df_all
else:
    base_filtro = [r for r in df_all if r["relevancia"] < 0.4]

st.sidebar.divider()
st.sidebar.subheader("Filtros")

rel_range = st.sidebar.slider("Relevancia LLM", 0.0, 1.0, (0.0, 1.0), 0.05)

years = sorted(set(r["year"] for r in base_filtro if r["year"]))
if years:
    year_range = st.sidebar.select_slider("Año", options=years, value=(min(years), max(years)))
else:
    year_range = (None, None)

todos_met = sorted(set(m for r in base_filtro for m in r["metodos_esp"]))
met_labels = [METODOS_L.get(m, m) for m in todos_met]
met_sel_l = st.sidebar.multiselect("Método", met_labels)
met_sel = [todos_met[met_labels.index(l)] for l in met_sel_l]

todas_int = sorted(set(i for r in base_filtro for i in r["intenciones"]))
int_labels = [INTENC_L.get(i, i) for i in todas_int]
int_sel_l = st.sidebar.multiselect("Intención", int_labels)
int_sel = [todas_int[int_labels.index(l)] for l in int_sel_l]

busqueda = st.sidebar.text_input("🔍 Buscar título / abstract")
solo_hallazgos = st.sidebar.checkbox("Solo con hallazgos nuevos")

# ── Aplicar filtros ───────────────────────────────────────────────────────────
filtrado = base_filtro
filtrado = [r for r in filtrado if rel_range[0] <= r["relevancia"] <= rel_range[1]]
if year_range[0]:
    filtrado = [r for r in filtrado if r["year"] and year_range[0] <= r["year"] <= year_range[1]]
if met_sel:
    filtrado = [r for r in filtrado if any(m in r["metodos_esp"] for m in met_sel)]
if int_sel:
    filtrado = [r for r in filtrado if any(i in r["intenciones"] for i in int_sel)]
if busqueda:
    q = busqueda.lower()
    filtrado = [r for r in filtrado if q in r["titulo"].lower() or q in r["abstract"].lower()]
if solo_hallazgos:
    filtrado = [r for r in filtrado if r["hallazgos"]]

# ══════════════════════════════════════════════════════════════════════════════
# HEADER + KPI
# ══════════════════════════════════════════════════════════════════════════════
st.title("📊 Visor · Intenciones Comunicativas en Publicaciones Digitales")
st.caption("Revisión Sistemática asistida por LLM · Luis Rojas Rubio · 2026")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Corpus total", "3.575", help="Artículos identificados en 6 bases de datos")
k2.metric("Elegibles E2", "373", help="Cribado semántico de metadatos (relevancia ≥ 0.40)")
k3.metric("Con PDF (E3)", "549", help="Texto completo analizado")
k4.metric("**Incluidos**", "324", help="Corpus final de síntesis (relevancia E3 ≥ 0.40)")
k5.metric("Filtrados ahora", len(filtrado))

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📋 Tabla",
    "📈 Gráficos",
    "🔥 Heatmap",
    "📅 Temporal",
    "🌍 Plataformas & Lengua",
    "🔬 PRISMA Flow",
    "🧪 Validación",
    "🔍 Detalle artículo",
    "📦 Datasets",
    "☁️ Nubes",
    "💡 Hallazgos",
    "🧠 Síntesis",
    "🔢 Granularidad",
    "🏷️ Hallazgos por Tema",
    "🎓 Tesis",
    "⚖️ E2 vs E3",
    "🫧 Clusters",
    "📚 Bibliografía",
    "🌳 TH9",
])

tab_tabla, tab_graficos, tab_heatmap, tab_temporal, tab_plataforma, \
tab_prisma, tab_validacion, tab_detalle, tab_datasets, tab_nubes, \
tab_hallazgos, tab_sintesis, tab_granularidad, tab_temas, tab_tesis, \
tab_e2e3, tab_clusters, tab_biblio, tab_th9 = tabs

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TABLA
# ══════════════════════════════════════════════════════════════════════════════
with tab_tabla:
    df_t = pd.DataFrame([{
        "ID":          r["id"],
        "Año":         r["year"],
        "Rel.":        r["relevancia"],
        "Título":      r["titulo"],
        "Métodos":     ", ".join(METODOS_L.get(m, m) for m in r["metodos_esp"]),
        "Intenciones": ", ".join(INTENC_L.get(i, i) for i in r["intenciones"]),
        "Plataforma":  ", ".join(r["plataforma"]),
        "Lengua":      ", ".join(r["linguistica"]),
        "Hallazgos":   len(r["hallazgos"]),
    } for r in filtrado])

    st.caption(f"{len(filtrado)} artículos · {len(df_t[df_t['Hallazgos']>0]) if not df_t.empty else 0} con hallazgos nuevos")
    st.dataframe(
        df_t, use_container_width=True, hide_index=True,
        column_config={
            "Rel.": st.column_config.ProgressColumn("Rel.", min_value=0, max_value=1, format="%.2f"),
            "Título": st.column_config.TextColumn("Título", width="large"),
            "Hallazgos": st.column_config.NumberColumn("💡", help="N° hallazgos nuevos"),
        }
    )
    if not df_t.empty:
        csv = df_t.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv, "corpus_filtrado.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GRÁFICOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_graficos:
    if not filtrado:
        st.info("Sin datos para los filtros actuales.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Distribución de relevancia LLM")
            fig = px.histogram(
                x=[r["relevancia"] for r in filtrado], nbins=20,
                labels={"x": "Relevancia", "y": "Artículos"},
                color_discrete_sequence=[C["blue"]]
            )
            fig.add_vline(x=0.4, line_dash="dash", line_color=C["red"],
                          annotation_text="Umbral 0.40", annotation_position="top right")
            fig.update_layout(bargap=0.05, height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Artículos por año")
            yc = Counter(r["year"] for r in filtrado if r["year"])
            df_y = pd.DataFrame(sorted(yc.items()), columns=["Año", "N"])
            fig2 = px.bar(df_y, x="Año", y="N", color_discrete_sequence=[C["green"]])
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)

        with c3:
            st.subheader("Métodos más frecuentes")
            mc = Counter(m for r in filtrado for m in r["metodos_esp"])
            df_m = pd.DataFrame(
                [(METODOS_L.get(k, k), v) for k, v in mc.most_common(15)],
                columns=["Método", "N"]
            )
            fig3 = px.bar(df_m, x="N", y="Método", orientation="h",
                          color_discrete_sequence=[C["red"]])
            fig3.update_layout(height=440, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.subheader("Intenciones más frecuentes")
            ic = Counter(i for r in filtrado for i in r["intenciones"])
            df_i = pd.DataFrame(
                [(INTENC_L.get(k, k), v) for k, v in ic.most_common(13)],
                columns=["Intención", "N"]
            )
            fig4 = px.bar(df_i, x="N", y="Intención", orientation="h",
                          color_discrete_sequence=[C["orange"]])
            fig4.update_layout(height=440, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig4, use_container_width=True)

        # Métricas de evaluación
        st.subheader("Métricas de evaluación más usadas")
        met_c = Counter(m for r in filtrado for m in r["metricas"])
        if met_c:
            df_met = pd.DataFrame(met_c.most_common(20), columns=["Métrica", "N"])
            fig_met = px.bar(df_met, x="N", y="Métrica", orientation="h",
                             color_discrete_sequence=[C["teal"]])
            fig_met.update_layout(height=380, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_met, use_container_width=True)

        # Scatter relevancia vs año
        st.subheader("Relevancia por año (distribución)")
        df_sc = pd.DataFrame([{
            "Año": r["year"], "Relevancia": r["relevancia"],
            "Título": r["titulo"][:60], "Intenciones": ", ".join(INTENC_L.get(i,i) for i in r["intenciones"][:2])
        } for r in filtrado if r["year"]])
        fig5 = px.strip(df_sc, x="Año", y="Relevancia", hover_data=["Título","Intenciones"],
                        color_discrete_sequence=[C["blue"]])
        fig5.add_hline(y=0.4, line_dash="dash", line_color=C["red"])
        fig5.update_layout(height=350)
        st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HEATMAP MÉTODO × INTENCIÓN
# ══════════════════════════════════════════════════════════════════════════════
with tab_heatmap:
    st.subheader("Tabla cruzada: Método × Intención comunicativa")
    st.caption("Frecuencia de co-ocurrencia en el corpus incluido (n=324). Fuente: tablas/02_cruzada_metodo_intencion.json")

    try:
        cruzada = load_tabla("02_cruzada_metodo_intencion.json")
        metodos_data = cruzada["metodos"]

        # Construir matriz
        all_intenciones = sorted({i["intencion"] for m in metodos_data for i in m.get("intenciones", [])})
        met_names = [m["metodo_label"] for m in metodos_data]
        int_names = [INTENC_L.get(i, i) for i in all_intenciones]

        matrix = []
        for m in metodos_data:
            int_dict = {i["intencion"]: i["cantidad"] for i in m.get("intenciones", [])}
            matrix.append([int_dict.get(i, 0) for i in all_intenciones])

        df_heat = pd.DataFrame(matrix, index=met_names, columns=int_names)

        # Filtro de umbral
        umbral = st.slider("Mostrar celdas con N ≥", 0, 100, 0, 5)
        df_show = df_heat.copy()
        df_show[df_show < umbral] = 0

        fig_heat = px.imshow(
            df_show,
            labels={"x": "Intención", "y": "Método", "color": "Co-ocurrencias"},
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto=True,
        )
        fig_heat.update_layout(
            height=600,
            xaxis={"side": "bottom", "tickangle": -30},
            coloraxis_colorbar={"title": "N arts."},
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Top combinaciones
        st.subheader("Top 15 combinaciones método–intención")
        combos = []
        for m in metodos_data:
            for i in m.get("intenciones", []):
                combos.append({
                    "Método": m["metodo_label"],
                    "Intención": INTENC_L.get(i["intencion"], i["intencion"]),
                    "N artículos": i["cantidad"],
                })
        df_combos = pd.DataFrame(combos).sort_values("N artículos", ascending=False).head(15)
        fig_cb = px.bar(
            df_combos, x="N artículos", y="Método", color="Intención",
            orientation="h", color_discrete_sequence=QUAL_COLORS,
        )
        fig_cb.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_cb, use_container_width=True)

    except Exception as e:
        st.error(f"No se pudo cargar la tabla cruzada: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TENDENCIA TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════
with tab_temporal:
    st.subheader("Evolución temporal del corpus (2020–2026)")
    st.caption("Fuente: tablas/03_evolucion_temporal.json · Clasificación LLM")

    try:
        temporal = load_tabla("03_evolucion_temporal.json")
        anos_data = temporal["anos"]

        df_temp = pd.DataFrame([{
            "Año":           d["ano"],
            "Total":         d["total_articulos"],
            "Binario":       d.get("enfoque_binario_n", 0),
            "Granular":      d.get("enfoque_granular_n", 0),
            "% Granular":    d.get("enfoque_granular_pct", 0),
        } for d in anos_data])

        c1, c2 = st.columns(2)

        with c1:
            fig_t1 = go.Figure()
            fig_t1.add_trace(go.Bar(name="Enfoque binario", x=df_temp["Año"], y=df_temp["Binario"],
                                    marker_color=C["gray"]))
            fig_t1.add_trace(go.Bar(name="Enfoque granular", x=df_temp["Año"], y=df_temp["Granular"],
                                    marker_color=C["blue"]))
            fig_t1.update_layout(
                barmode="stack", height=350, title="Artículos por año (binario vs granular)",
                xaxis_title="Año", yaxis_title="N artículos",
            )
            st.plotly_chart(fig_t1, use_container_width=True)

        with c2:
            fig_t2 = px.line(
                df_temp, x="Año", y="% Granular",
                markers=True, title="% Enfoque granular por año",
                color_discrete_sequence=[C["green"]],
            )
            fig_t2.add_hrule(y=50, line_dash="dash", line_color=C["red"],
                             annotation_text="50%")
            fig_t2.update_layout(height=350, yaxis_title="% granular")
            st.plotly_chart(fig_t2, use_container_width=True)

        # Top métodos por año (heatmap temporal)
        st.subheader("Top métodos por año")
        met_year = {}
        for d in anos_data:
            for m in d.get("metodos_top5", []):
                key = (d["ano"], m["metodo"])
                met_year[key] = m.get("cantidad", 0)

        all_met_y = sorted(set(k[1] for k in met_year))
        all_anos_y = sorted(set(k[0] for k in met_year))
        mat_y = [[met_year.get((a, m), 0) for m in all_met_y] for a in all_anos_y]

        fig_ty = px.imshow(
            mat_y, x=all_met_y, y=[str(a) for a in all_anos_y],
            labels={"x": "Método", "y": "Año", "color": "Artículos"},
            color_continuous_scale="Blues", text_auto=True, aspect="auto",
        )
        fig_ty.update_layout(height=300, xaxis={"tickangle": -30})
        st.plotly_chart(fig_ty, use_container_width=True)

    except Exception as e:
        st.error(f"Error cargando datos temporales: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PLATAFORMAS & LENGUA
# ══════════════════════════════════════════════════════════════════════════════
with tab_plataforma:
    st.subheader("Plataformas digitales estudiadas")

    try:
        plat_data = load_tabla("10_plataformas.json")["plataformas"]
        df_plat = pd.DataFrame([{
            "Plataforma": p["plataforma"],
            "Artículos":  p["cantidad_articulos"],
            "%":          p["porcentaje"],
        } for p in plat_data]).sort_values("Artículos", ascending=False)

        c1, c2 = st.columns([2, 1])
        with c1:
            fig_p = px.bar(
                df_plat.head(15), x="Artículos", y="Plataforma", orientation="h",
                color="Artículos", color_continuous_scale="Blues",
                text="Artículos",
            )
            fig_p.update_traces(textposition="outside")
            fig_p.update_layout(height=420, yaxis={"categoryorder": "total ascending"},
                                showlegend=False)
            st.plotly_chart(fig_p, use_container_width=True)

        with c2:
            fig_pie = px.pie(
                df_plat.head(8), values="Artículos", names="Plataforma",
                color_discrete_sequence=QUAL_COLORS, hole=0.35,
            )
            fig_pie.update_layout(height=420)
            st.plotly_chart(fig_pie, use_container_width=True)

    except Exception as e:
        st.warning(f"No se pudieron cargar plataformas: {e}")

    st.divider()
    st.subheader("Características lingüísticas")

    try:
        ling_raw = load_tabla("09_caracteristicas_linguisticas.json")
        caracteristicas = ling_raw.get("caracteristicas", [])
        if caracteristicas:
            df_ling = pd.DataFrame([{
                "Idioma":    c.get("idioma", c.get("linguistica", str(c))),
                "Artículos": c.get("cantidad_articulos", c.get("cantidad", 0)),
            } for c in caracteristicas if isinstance(c, dict)]).sort_values("Artículos", ascending=False)

            if not df_ling.empty:
                c1, c2 = st.columns([1, 1])
                with c1:
                    fig_l = px.bar(df_ling, x="Artículos", y="Idioma", orientation="h",
                                   color_discrete_sequence=[C["purple"]])
                    fig_l.update_layout(height=350, yaxis={"categoryorder": "total ascending"})
                    st.plotly_chart(fig_l, use_container_width=True)
                with c2:
                    fig_lp = px.pie(df_ling, values="Artículos", names="Idioma",
                                    color_discrete_sequence=QUAL_COLORS, hole=0.3)
                    fig_lp.update_layout(height=350)
                    st.plotly_chart(fig_lp, use_container_width=True)
        else:
            # Fallback: calcular desde corpus filtrado
            ling_c = Counter(l for r in filtrado for l in r["linguistica"])
            if ling_c:
                df_lf = pd.DataFrame(ling_c.most_common(15), columns=["Idioma", "N"])
                fig_lf = px.bar(df_lf, x="N", y="Idioma", orientation="h",
                                color_discrete_sequence=[C["purple"]])
                fig_lf.update_layout(height=350, yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_lf, use_container_width=True)

    except Exception as e:
        ling_c = Counter(l for r in filtrado for l in r["linguistica"])
        if ling_c:
            df_lf = pd.DataFrame(ling_c.most_common(15), columns=["Idioma", "N"])
            st.bar_chart(df_lf.set_index("Idioma"))

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PRISMA FLOW
# ══════════════════════════════════════════════════════════════════════════════
with tab_prisma:
    st.subheader("Flujo PRISMA 2020 — Proceso de selección")

    PRISMA = {
        "Identificados (6 BD)": 3575,
        "Elegibles E2\n(cribado metadatos)": 373,
        "Excluidos E2": 3202,
        "Con texto completo": 549,
        "Sin texto completo (CE5)": 3575 - 373 - (549 - 373),   # aprox
        "Incluidos E3\n(corpus final)": 324,
        "Excluidos E3": 225,
    }

    # Funnel de inclusión
    funnel_labels = [
        "Identificados\n(6 bases de datos)",
        "Elegibles E2\n(metadatos, relevancia ≥ 0.40)",
        "Con texto completo\n(PDF descargado)",
        "Incluidos en síntesis\n(texto completo, relevancia ≥ 0.40)",
    ]
    funnel_values = [3575, 373, 549, 324]
    funnel_colors = [C["blue"], C["teal"], C["green"], C["indigo"]]

    fig_funnel = go.Figure(go.Funnel(
        y=funnel_labels,
        x=funnel_values,
        textinfo="value+percent initial",
        marker={"color": funnel_colors},
        connector={"line": {"color": "#E5E7EB", "width": 2}},
    ))
    fig_funnel.update_layout(
        height=420, margin={"l": 220},
        title="Embudo de selección PRISMA",
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Tabla de exclusiones por etapa
    st.subheader("Criterios de exclusión")
    exclusiones = pd.DataFrame([
        {"Etapa": "Etapa 2 (metadatos)", "Criterio": "CE1 — Relevancia LLM < 0.40", "N": 2.480, "Tipo": "principal"},
        {"Etapa": "Etapa 2 (metadatos)", "Criterio": "CE2 — Sin intención comunicativa identificada", "N": 470, "Tipo": "secundario"},
        {"Etapa": "Etapa 2 (metadatos)", "Criterio": "CE3 — Sin método NLP/ML identificado", "N": 252, "Tipo": "secundario"},
        {"Etapa": "Etapa 2 (metadatos)", "Criterio": "CE4 — Fuera del período 2020–2026", "N": 0, "Tipo": "secundario"},
        {"Etapa": "Etapa 3 (texto completo)", "Criterio": "CE1 — Relevancia texto completo < 0.40", "N": 225, "Tipo": "principal"},
        {"Etapa": "Etapa 3 (texto completo)", "Criterio": "CE5 — Texto completo no disponible", "N": 3575-373-549, "Tipo": "acceso"},
    ])
    st.dataframe(exclusiones, use_container_width=True, hide_index=True)

    # Gráfico de retención por etapa
    st.subheader("Retención a través del pipeline")
    etapas = ["E1: Búsqueda", "E2: Metadatos", "E3: Texto completo", "Corpus final"]
    valores = [3575, 373, 549, 324]
    retencion = [100, 373/3575*100, 549/3575*100, 324/3575*100]

    c1, c2 = st.columns(2)
    with c1:
        fig_ret = px.bar(
            x=etapas, y=valores,
            labels={"x": "Etapa", "y": "N artículos"},
            color=valores, color_continuous_scale="Blues",
            text=valores,
        )
        fig_ret.update_traces(textposition="outside")
        fig_ret.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_ret, use_container_width=True)
    with c2:
        fig_pct = px.bar(
            x=etapas, y=retencion,
            labels={"x": "Etapa", "y": "% respecto al total inicial"},
            color=retencion, color_continuous_scale="Greens",
            text=[f"{v:.1f}%" for v in retencion],
        )
        fig_pct.update_traces(textposition="outside")
        fig_pct.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_pct, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — VALIDACIÓN INTER-EVALUADOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_validacion:
    st.subheader("Validación inter-evaluador (doble ciego, n=30)")
    st.caption("Comparación: Evaluador humano (Luis Rojas Rubio) vs pipeline LLM (Claude Sonnet 5)")

    # KPIs de validación
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Muestra", "30 artículos", help="Selección aleatoria estratificada")
    v2.metric("Acuerdo exacto", "43.3%", "13 de 30", help="Casos donde humano y LLM coinciden")
    v3.metric("Cohen's κ", "0.113", "Concordancia 'slight'", delta_color="off")
    v4.metric("κ ponderado lineal", "0.229", "Concordancia 'fair'", delta_color="off")

    st.divider()

    # Matriz de confusión
    st.subheader("Matriz de confusión (Humano × LLM)")
    st.caption("Filas = categoría humano · Columnas = categoría LLM · A=Alta, M=Media, B=Baja")

    conf_matrix = pd.DataFrame(
        [[4, 6, 0], [2, 7, 1], [0, 2, 3]],
        index=["Humano: Alta (10)", "Humano: Media (15)", "Humano: Baja (5)"],
        columns=["LLM: Alta", "LLM: Media", "LLM: Baja"],
    )

    fig_conf = px.imshow(
        conf_matrix,
        labels={"x": "Categoría LLM", "y": "Categoría Humano", "color": "N"},
        color_continuous_scale=["#EBF3FB", "#2563EB"],
        text_auto=True, aspect="auto",
    )
    fig_conf.update_layout(height=300, width=500)
    st.plotly_chart(fig_conf, use_container_width=False)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Distribución por categoría")
        cats = pd.DataFrame({
            "Categoría": ["Alta (A)", "Media (M)", "Baja (B)"],
            "Humano": [10, 15, 5],
            "LLM": [6, 15, 4],
        })
        fig_cat = px.bar(
            cats.melt(id_vars="Categoría", var_name="Evaluador", value_name="N"),
            x="Categoría", y="N", color="Evaluador", barmode="group",
            color_discrete_map={"Humano": C["blue"], "LLM": C["orange"]},
        )
        fig_cat.update_layout(height=300)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_b:
        st.subheader("Interpretación del kappa")
        kappa_interp = pd.DataFrame([
            {"Rango κ": "< 0.00", "Interpretación": "Sin acuerdo", "Este estudio": ""},
            {"Rango κ": "0.00–0.20", "Interpretación": "Slight ✓", "Este estudio": "← κ=0.113"},
            {"Rango κ": "0.21–0.40", "Interpretación": "Fair", "Este estudio": "← κw=0.229"},
            {"Rango κ": "0.41–0.60", "Interpretación": "Moderate", "Este estudio": ""},
            {"Rango κ": "0.61–0.80", "Interpretación": "Substantial", "Este estudio": ""},
            {"Rango κ": "> 0.80", "Interpretación": "Almost perfect", "Este estudio": ""},
        ])
        st.dataframe(kappa_interp, use_container_width=True, hide_index=True)

    st.info(
        "**Contexto:** El acuerdo modest (slight/fair) es esperable en sistemas de cribado semántico "
        "LLM sobre categorías ordinales subjetivas. El κ ponderado (0.229) indica que los desacuerdos "
        "son mayoritariamente adyacentes (A↔M, M↔B), no extremos (A↔B)."
    )

    # Discrepancias
    st.subheader("Tipos de discrepancia (17 casos)")
    disc = pd.DataFrame([
        {"Tipo": "LLM alta → Humano media (A→M)", "N": 6, "Tipo desacuerdo": "Adyacente"},
        {"Tipo": "LLM media → Humano alta (M→A)", "N": 2, "Tipo desacuerdo": "Adyacente"},
        {"Tipo": "LLM media → Humano baja (M→B)", "N": 2, "Tipo desacuerdo": "Adyacente"},
        {"Tipo": "LLM baja → Humano media (B→M)", "N": 2, "Tipo desacuerdo": "Adyacente"},
        {"Tipo": "LLM alta → Humano baja (A→B)", "N": 3, "Tipo desacuerdo": "Extremo"},
        {"Tipo": "LLM baja → Humano alta (B→A)", "N": 2, "Tipo desacuerdo": "Extremo"},
    ])
    fig_disc = px.bar(
        disc, x="N", y="Tipo", color="Tipo desacuerdo", orientation="h",
        color_discrete_map={"Adyacente": C["yellow"], "Extremo": C["red"]},
    )
    fig_disc.update_layout(height=320, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_disc, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — DETALLE ARTÍCULO
# ══════════════════════════════════════════════════════════════════════════════
with tab_detalle:
    if not filtrado:
        st.info("Sin artículos con los filtros actuales.")
    else:
        opciones = {
            f"[{r['relevancia']:.2f}] {r['titulo'][:80]} ({r['year']})": r
            for r in sorted(filtrado, key=lambda x: -x["relevancia"])
        }
        sel = st.selectbox("Selecciona un artículo", list(opciones.keys()))
        r = opciones[sel]

        col_m, col_r = st.columns([3, 1])
        col_m.markdown(f"### {r['titulo']}")
        col_r.metric("Relevancia LLM", f"{r['relevancia']:.2f}")

        st.markdown(f"**Autores:** {r['autores']}  \n**Año:** {r['year']}  \n**ID:** `{r['id']}`"
                    + (f"  \n**DOI:** {r['doi']}" if r['doi'] else ""))
        if r["abstract"]:
            with st.expander("Abstract", expanded=True):
                st.markdown(r["abstract"])
        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            if r["metodos_esp"]:
                st.markdown("**Métodos específicos**")
                for m in r["metodos_esp"]:
                    st.markdown(f"- {METODOS_L.get(m, m)}")
            if r["metodos_gen"]:
                st.markdown("**Métodos generales**")
                for m in r["metodos_gen"]: st.markdown(f"- {m}")
            if r["metricas"]:
                st.markdown("**Métricas de evaluación**")
                for m in r["metricas"]: st.markdown(f"- `{m}`")
            if r["metodologica"]:
                st.markdown("**Técnicas metodológicas**")
                for m in r["metodologica"]: st.markdown(f"- {m}")

        with c2:
            if r["intenciones"]:
                st.markdown("**Intenciones comunicativas**")
                for i in r["intenciones"]:
                    st.markdown(f"- {INTENC_L.get(i, i)}")
            if r["plataforma"]:
                st.markdown("**Plataforma(s)**")
                st.markdown(", ".join(r["plataforma"]))
            if r["linguistica"]:
                st.markdown("**Idioma(s)**")
                st.markdown(", ".join(r["linguistica"]))

        if r["dataset_info"]:
            st.divider()
            st.markdown("**Datasets utilizados**")
            for ds in r["dataset_info"]:
                nombre = ds.get("nombre", "?")
                url    = ds.get("url")
                ref    = ds.get("referencia", "")
                st.markdown(f"- **[{nombre}]({url})**{' — ' + ref if ref else ''}"
                            if url else f"- **{nombre}**{' — ' + ref if ref else ''}")

        if r["hallazgos"]:
            st.divider()
            st.markdown(f"**Hallazgos nuevos ({len(r['hallazgos'])})**")
            for h in r["hallazgos"]: st.markdown(f"- {h}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — DATASETS
# ══════════════════════════════════════════════════════════════════════════════
with tab_datasets:
    st.subheader("Datasets referenciados en el corpus filtrado")
    ds_cnt = Counter(ds for r in filtrado for ds in r["datasets"])
    if not ds_cnt:
        st.info("Sin datasets en los artículos filtrados.")
    else:
        df_ds = pd.DataFrame(ds_cnt.most_common(40), columns=["Dataset", "Artículos"])
        fig_ds = px.bar(df_ds, x="Artículos", y="Dataset", orientation="h",
                        color="Artículos", color_continuous_scale="Purples")
        fig_ds.update_layout(height=max(400, len(df_ds)*22),
                             yaxis={"categoryorder":"total ascending"}, showlegend=False)
        st.plotly_chart(fig_ds, use_container_width=True)

        st.subheader("Detalle con URLs")
        ds_det = {}
        for r in filtrado:
            for ds in r.get("dataset_info", []):
                nombre = ds.get("nombre", "?")
                if nombre not in ds_det:
                    ds_det[nombre] = {"url": ds.get("url"), "ref": ds.get("referencia",""), "n": 0}
                ds_det[nombre]["n"] += 1
        df_det = pd.DataFrame([
            {"Dataset": k, "Artículos": v["n"], "URL": v["url"] or "—", "Referencia": v["ref"][:80]}
            for k, v in sorted(ds_det.items(), key=lambda x: -x[1]["n"])
        ])
        st.dataframe(df_det, use_container_width=True, hide_index=True,
                     column_config={"URL": st.column_config.LinkColumn("URL")})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 10 — NUBES DE PALABRAS
# ══════════════════════════════════════════════════════════════════════════════
with tab_nubes:
    if not _WC:
        st.warning("Instala `wordcloud matplotlib` para usar esta sección:\n```\npip install wordcloud matplotlib\n```")
    elif not filtrado:
        st.info("Sin datos.")
    else:
        def make_wc(text, title):
            sw = SW | (STOPWORDS if _WC else set())
            wc = WordCloud(width=900, height=400, background_color="white",
                           stopwords=sw, colormap="viridis",
                           max_words=120, collocations=False).generate(text)
            fig, ax = plt.subplots(figsize=(9,4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            ax.set_title(title, fontsize=12, pad=8)
            return fig

        fuente = st.radio("Fuente", ["Títulos","Abstracts","Hallazgos nuevos"], horizontal=True)
        def corpus_txt(rows, f):
            if f=="Títulos": return " ".join(r["titulo"] for r in rows if r["titulo"])
            if f=="Abstracts": return " ".join(r["abstract"] for r in rows if r["abstract"])
            return " ".join(h for r in rows for h in r["hallazgos"])

        txt = corpus_txt(filtrado, fuente)
        if txt.strip():
            fig_wc = make_wc(txt, f"{fuente} — {len(filtrado)} artículos")
            st.pyplot(fig_wc); plt.close(fig_wc)

        st.divider()
        st.subheader("Alta (≥0.7) vs Baja (<0.7) relevancia")
        alta = [r for r in filtrado if r["relevancia"] >= 0.7]
        baja = [r for r in filtrado if r["relevancia"] < 0.7]
        fuente2 = st.selectbox("Texto", ["Títulos","Abstracts","Hallazgos nuevos"], key="wc2")
        if alta and baja:
            w1, w2 = st.columns(2)
            for col, rows, label in [(w1,alta,f"Alta ≥0.7 ({len(alta)} arts.)"),
                                      (w2,baja,f"Baja <0.7 ({len(baja)} arts.)")]:
                t = corpus_txt(rows, fuente2)
                if t.strip():
                    with col:
                        fig_wc2 = make_wc(t, label)
                        st.pyplot(fig_wc2); plt.close(fig_wc2)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 11 — HALLAZGOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_hallazgos:
    st.subheader("Hallazgos nuevos reportados por artículo")
    rows_h = [
        {"Año": r["year"], "Rel.": r["relevancia"],
         "Hallazgo": h, "Título": r["titulo"], "ID": r["id"]}
        for r in filtrado for h in r["hallazgos"]
    ]
    if not rows_h:
        st.info("No hay hallazgos nuevos en los artículos filtrados.")
    else:
        busq_h = st.text_input("Buscar en hallazgos", key="bh")
        if busq_h:
            q = busq_h.lower()
            rows_h = [h for h in rows_h if q in h["Hallazgo"].lower() or q in h["Título"].lower()]

        st.caption(f"{len(rows_h)} hallazgos · {sum(1 for r in filtrado if r['hallazgos'])} artículos")
        df_h = pd.DataFrame(rows_h)
        st.dataframe(df_h, use_container_width=True, hide_index=True,
                     column_config={
                         "Rel.": st.column_config.ProgressColumn("Rel.", min_value=0, max_value=1, format="%.2f"),
                         "Hallazgo": st.column_config.TextColumn("Hallazgo", width="large"),
                         "Título":   st.column_config.TextColumn("Título", width="medium"),
                     })

        st.divider()
        st.subheader("Términos más frecuentes en hallazgos")
        words = [w for row in rows_h
                 for w in re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,}\b", row["Hallazgo"].lower())
                 if w not in SW]
        if words:
            df_wf = pd.DataFrame(Counter(words).most_common(25), columns=["Término","N"])
            fig_wf = px.bar(df_wf, x="N", y="Término", orientation="h",
                            color_discrete_sequence=[C["indigo"]])
            fig_wf.update_layout(height=500, yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fig_wf, use_container_width=True)

        csv_h = df_h.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar hallazgos CSV", csv_h, "hallazgos.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 12 — SÍNTESIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_sintesis:
    SINT_PATH = BASE / "sintesis_hallazgos_revision.json"
    if not SINT_PATH.exists():
        st.warning("No se encontró `sintesis_hallazgos_revision.json`.")
    else:
        sint = load_json(SINT_PATH)
        ejes = sint.get("ejes_tematicos", [])

        ROL_COLOR = {"tendencia":"#2563EB","limitacion":"#DC2626",
                     "brecha":"#7C3AED","oportunidad":"#16A34A"}
        ROL_LABEL = {"tendencia":"↗ Tendencia","limitacion":"⚠ Limitación",
                     "brecha":"○ Brecha","oportunidad":"★ Oportunidad"}

        gap = sint.get("gap_central_identificado","")
        if gap:
            st.markdown("### Gap central identificado")
            st.info(gap)
            st.divider()

        conv = sint.get("convergencias_transversales",[])
        if conv:
            with st.expander("🔗 Convergencias transversales", expanded=False):
                for c in conv: st.markdown(f"- {c}")
            st.divider()

        st.markdown("### Ejes temáticos")
        eje_nombres = [f"{e['id']} — {e['eje']}" for e in ejes]
        eje_sel = st.selectbox("Ir a eje", ["(todos)"] + eje_nombres, key="eje_nav")

        ejes_show = ejes if eje_sel == "(todos)" else [
            e for e in ejes if f"{e['id']} — {e['eje']}" == eje_sel]

        for eje in ejes_show:
            with st.expander(f"**{eje['id']}** — {eje['eje']}", expanded=(eje_sel != "(todos)")):
                st.markdown(f"*{eje.get('descripcion','')}*")
                st.divider()
                sd = eje.get("sintesis",{})
                c1, c2 = st.columns(2)
                with c1:
                    for k, lbl in [("tendencias","**↗ Tendencias**"),
                                   ("limitaciones_identificadas","**⚠ Limitaciones**")]:
                        items = sd.get(k,[])
                        if items:
                            st.markdown(lbl)
                            for it in items: st.markdown(f"- {it}")
                with c2:
                    for k, lbl in [("brechas","**○ Brechas**"),
                                   ("preguntas_que_emergen","**? Preguntas emergentes**")]:
                        items = sd.get(k,[])
                        if items:
                            st.markdown(lbl)
                            for it in items: st.markdown(f"- *{it}*" if k=="preguntas_que_emergen" else f"- {it}")

                h_eje = eje.get("hallazgos_representativos",[])
                if h_eje:
                    st.divider()
                    st.markdown(f"**Hallazgos representativos ({len(h_eje)})**")
                    for h in h_eje:
                        rol = h.get("rol","tendencia")
                        st.markdown(
                            f"<span style='background:{ROL_COLOR.get(rol,'#888')};color:white;"
                            f"padding:2px 8px;border-radius:4px;font-size:.78em'>"
                            f"{ROL_LABEL.get(rol,rol)}</span> "
                            f"<span style='color:#6B7280;font-size:.85em'>({h.get('year','')})</span> "
                            f"{h.get('hallazgo','')}",
                            unsafe_allow_html=True,
                        )

                ids_eje = {h.get("articulo_id","") for h in h_eje}
                arts_cruce = [r for r in filtrado if r["id"] in ids_eje]
                if arts_cruce:
                    st.divider()
                    st.caption(f"{len(arts_cruce)} artículo(s) de este eje en el dataset filtrado")
                    df_cr = pd.DataFrame([{"ID":r["id"],"Año":r["year"],
                                           "Rel.":r["relevancia"],"Título":r["titulo"][:80]}
                                          for r in arts_cruce])
                    st.dataframe(df_cr, use_container_width=True, hide_index=True,
                                 column_config={"Rel.": st.column_config.ProgressColumn(
                                     "Rel.", min_value=0, max_value=1, format="%.2f")})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 13 — GRANULARIDAD
# ══════════════════════════════════════════════════════════════════════════════
with tab_granularidad:
    st.subheader("Granularidad de detección de intenciones")
    st.caption("¿Cuántas intenciones identifica cada artículo? Binario (N=1) vs granular (N≥2).")

    if not filtrado:
        st.info("Sin datos para los filtros actuales.")
    else:
        n_intenciones = [len(r["intenciones"]) for r in filtrado]
        cnt = Counter(n_intenciones)

        c1, c2 = st.columns([2, 1])
        with c1:
            df_g = pd.DataFrame(sorted(cnt.items()), columns=["N intenciones", "Artículos"])
            fig_g = px.bar(
                df_g, x="N intenciones", y="Artículos",
                color="N intenciones",
                color_continuous_scale="Blues",
                labels={"N intenciones": "N° intenciones por artículo", "Artículos": "N° artículos"},
                text="Artículos",
            )
            fig_g.update_traces(textposition="outside")
            fig_g.update_layout(height=400, showlegend=False, coloraxis_showscale=False)
            fig_g.add_vline(x=1.5, line_dash="dash", line_color=C["red"],
                            annotation_text="Umbral granular", annotation_position="top right")
            st.plotly_chart(fig_g, use_container_width=True)

        with c2:
            total = len(filtrado)
            binarios = cnt.get(0, 0) + cnt.get(1, 0)
            granulares = total - binarios
            sin_int = cnt.get(0, 0)
            media = sum(n_intenciones) / total if total else 0

            st.metric("Total artículos", total)
            st.metric("Sin intención detectada", sin_int)
            st.metric("Binarios (N=1)", cnt.get(1, 0), help="Solo 1 intención")
            st.metric("Granulares (N≥2)", granulares, help="2 o más intenciones")
            st.metric("Media intenciones", f"{media:.2f}")

        # Pie binario vs granular
        st.subheader("Distribución binario vs granular")
        df_pie = pd.DataFrame([
            {"Tipo": "Binario (N≤1)", "N": binarios},
            {"Tipo": "Granular (N≥2)", "N": granulares},
        ])
        fig_pie = px.pie(df_pie, values="N", names="Tipo",
                         color_discrete_sequence=[C["blue"], C["green"]])
        fig_pie.update_layout(height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

        # Distribución por año
        st.subheader("Media de intenciones por año")
        from collections import defaultdict
        year_ints = defaultdict(list)
        for r in filtrado:
            if r["year"]:
                year_ints[r["year"]].append(len(r["intenciones"]))
        df_yi = pd.DataFrame([
            {"Año": y, "Media": sum(v)/len(v), "N": len(v)}
            for y, v in sorted(year_ints.items())
        ])
        if not df_yi.empty:
            fig_yi = px.line(df_yi, x="Año", y="Media", markers=True,
                             hover_data=["N"],
                             color_discrete_sequence=[C["purple"]])
            fig_yi.add_hline(y=1.5, line_dash="dash", line_color=C["red"])
            fig_yi.update_layout(height=300)
            st.plotly_chart(fig_yi, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 14 — HALLAZGOS POR TEMA
# ══════════════════════════════════════════════════════════════════════════════
with tab_temas:
    st.subheader("Hallazgos agrupados por tema")
    st.caption("Fuente: tablas/12_hallazgos_nuevos.json · 8 temas temáticos del corpus")

    try:
        h12 = load_tabla("12_hallazgos_nuevos.json")
        temas_data = h12.get("temas", [])

        if not temas_data:
            st.warning("No hay temas en el archivo.")
        else:
            # KPI bar
            df_temas_kpi = pd.DataFrame([
                {"Tema": t["nombre"], "Hallazgos": t["total_hallazgos"], "Artículos": t["total_articulos"]}
                for t in temas_data
            ])
            fig_t = px.bar(df_temas_kpi, x="Hallazgos", y="Tema", orientation="h",
                           color="Artículos", color_continuous_scale="Blues",
                           text="Hallazgos")
            fig_t.update_traces(textposition="outside")
            fig_t.update_layout(height=380, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_t, use_container_width=True)

            st.divider()

            # Selector de tema
            nombres_temas = [f"{t['tema_id']} — {t['nombre']}" for t in temas_data]
            tema_sel = st.selectbox("Explorar tema", ["(todos)"] + nombres_temas, key="tema_sel")

            temas_show = temas_data if tema_sel == "(todos)" else [
                t for t in temas_data if f"{t['tema_id']} — {t['nombre']}" == tema_sel
            ]

            busq_tema = st.text_input("🔍 Buscar dentro de hallazgos", key="busq_tema")

            for t in temas_show:
                with st.expander(
                    f"**{t['tema_id']}** — {t['nombre']}  "
                    f"({t['total_hallazgos']} hallazgos · {t['total_articulos']} artículos)",
                    expanded=(tema_sel != "(todos)")
                ):
                    st.caption(t.get("descripcion", ""))
                    rq = t.get("rq_asociada", "")
                    if rq:
                        st.info(f"RQ: {rq}")

                    hallazgos_t = t.get("hallazgos", [])
                    if busq_tema:
                        hallazgos_t = [h for h in hallazgos_t if busq_tema.lower() in h.get("hallazgo","").lower()]

                    st.caption(f"Mostrando {len(hallazgos_t)} hallazgos")
                    for i, h in enumerate(hallazgos_t[:100]):
                        art = h.get("articulo", {})
                        st.markdown(
                            f"<small style='color:{C['gray']}'>[{art.get('year','')}] "
                            f"{art.get('titulo','')[:70]}…</small>  \n"
                            f"{h.get('hallazgo','')}",
                            unsafe_allow_html=True
                        )
                        if i < len(hallazgos_t) - 1:
                            st.divider()

    except FileNotFoundError:
        st.error("No se encontró tablas/12_hallazgos_nuevos.json")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 15 — HALLAZGOS RELEVANTES PARA LA TESIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_tesis:
    st.subheader("Hallazgos relevantes para la tesis doctoral")
    st.caption("870 hallazgos de 414 artículos organizados por criterio de alineación con el modelo propuesto.")

    TESIS_PATH = BASE / "hallazgos_relevantes_tesis.json"
    if not TESIS_PATH.exists():
        st.error("No se encontró hallazgos_relevantes_tesis.json")
    else:
        tesis_data = load_json(TESIS_PATH)
        meta_t = tesis_data.get("meta", {})
        hallazgos_t = tesis_data.get("hallazgos", [])
        criterios_dict = meta_t.get("criterios", {})

        # KPI
        k1t, k2t, k3t = st.columns(3)
        k1t.metric("Total hallazgos", meta_t.get("total_hallazgos_relevantes", 0))
        k2t.metric("Artículos fuente", meta_t.get("total_articulos_fuente", 0))
        k3t.metric("Criterios de alineación", len(criterios_dict))

        st.info(f"**Tesis:** {meta_t.get('tesis','')}")
        st.divider()

        # Filtros
        criterios_labels = {k: k.replace("_", " ").title() for k in criterios_dict}
        crit_sel = st.multiselect(
            "Filtrar por criterio",
            options=list(criterios_labels.keys()),
            format_func=lambda x: criterios_labels[x],
            key="tesis_crit"
        )
        busq_tesis = st.text_input("🔍 Buscar en hallazgos o título", key="busq_tesis")

        # Distribución por criterio
        from collections import defaultdict
        crit_count = defaultdict(int)
        for h in hallazgos_t:
            for c in h.get("criterios", []):
                crit_count[c] += 1

        df_crit = pd.DataFrame([
            {"Criterio": criterios_labels.get(k, k), "N": v}
            for k, v in sorted(crit_count.items(), key=lambda x: -x[1])
        ])
        if not df_crit.empty:
            fig_crit = px.bar(df_crit, x="N", y="Criterio", orientation="h",
                              color_discrete_sequence=[C["indigo"]], text="N")
            fig_crit.update_traces(textposition="outside")
            fig_crit.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_crit, use_container_width=True)

        st.divider()

        # Tabla de hallazgos filtrada
        h_show = hallazgos_t
        if crit_sel:
            h_show = [h for h in h_show if any(c in h.get("criterios", []) for c in crit_sel)]
        if busq_tesis:
            q = busq_tesis.lower()
            h_show = [h for h in h_show if q in h.get("hallazgo","").lower() or q in h.get("titulo","").lower()]

        st.caption(f"{len(h_show)} hallazgos · ordenados por relevancia")
        h_show_sorted = sorted(h_show, key=lambda x: -x.get("relevancia_general", 0))

        df_ht = pd.DataFrame([{
            "Año": h.get("year"),
            "Rel.": h.get("relevancia_general", 0),
            "Criterios": ", ".join(h.get("criterios", [])),
            "N crit.": h.get("num_criterios", 0),
            "Hallazgo": h.get("hallazgo", "")[:120],
            "Título": h.get("titulo", "")[:80],
        } for h in h_show_sorted[:300]])

        if not df_ht.empty:
            st.dataframe(
                df_ht, use_container_width=True, hide_index=True,
                column_config={
                    "Rel.": st.column_config.ProgressColumn("Rel.", min_value=0, max_value=1, format="%.2f"),
                    "N crit.": st.column_config.NumberColumn("★"),
                    "Hallazgo": st.column_config.TextColumn("Hallazgo", width="large"),
                }
            )

        # Expandir detalles para los top
        if h_show_sorted:
            st.divider()
            st.subheader("Detalle de hallazgos (top por relevancia)")
            for h in h_show_sorted[:20]:
                crits = h.get("criterios", [])
                with st.expander(
                    f"[{h.get('year','')}] {h.get('titulo','')[:80]}… "
                    f"(★{h.get('num_criterios',0)} criterios · Rel. {h.get('relevancia_general',0):.2f})",
                    expanded=False
                ):
                    st.markdown(f"**Hallazgo:** {h.get('hallazgo','')}")
                    if crits:
                        st.markdown("**Criterios de alineación:**")
                        for c in crits:
                            desc = criterios_dict.get(c, "")
                            st.markdown(f"- `{c}`: {desc}")
                    cols = h.get("intenciones", [])
                    if cols:
                        st.caption("Intenciones: " + ", ".join(INTENC_L.get(i,i) for i in cols))

# ══════════════════════════════════════════════════════════════════════════════
# TAB 16 — COMPARATIVA E2 vs E3
# ══════════════════════════════════════════════════════════════════════════════
with tab_e2e3:
    st.subheader("Comparativa E2 vs E3: ¿El abstract predice bien el texto completo?")
    st.caption("Relevancia E2 (cribado de metadatos) vs E3 (análisis de texto completo PDF).")

    try:
        e2_data = load_json(BASE / "clasificacion_claude.json")
        e2_arts = {a["id"]: a.get("relevancia_general", 0) for a in e2_data.get("articulos", [])}

        e3_arts = load_corpus()
        e3_rel = {a.get("id",""): a.get("relevancia_general", 0) for a in e3_arts}

        comunes = [(aid, e2_arts[aid], e3_rel[aid]) for aid in e2_arts if aid in e3_rel]
        df_e2e3 = pd.DataFrame(comunes, columns=["ID", "Rel_E2", "Rel_E3"])
        df_e2e3["Diferencia"] = df_e2e3["Rel_E3"] - df_e2e3["Rel_E2"]
        df_e2e3["Resultado"] = df_e2e3.apply(
            lambda r: "Sobreestimado" if r["Diferencia"] < -0.15
            else ("Subestimado" if r["Diferencia"] > 0.15 else "Consistente"),
            axis=1
        )

        # KPI
        k1e, k2e, k3e, k4e = st.columns(4)
        k1e.metric("Total comparados", len(df_e2e3))
        k2e.metric("Consistentes", len(df_e2e3[df_e2e3["Resultado"]=="Consistente"]))
        k3e.metric("Sobreestimados E2", len(df_e2e3[df_e2e3["Resultado"]=="Sobreestimado"]),
                   help="Abstract parecía más relevante que el texto completo")
        k4e.metric("Subestimados E2", len(df_e2e3[df_e2e3["Resultado"]=="Subestimado"]),
                   help="El PDF resultó más relevante que el abstract")

        # Scatter E2 vs E3
        fig_e2e3 = px.scatter(
            df_e2e3, x="Rel_E2", y="Rel_E3",
            color="Resultado",
            color_discrete_map={
                "Consistente": C["green"],
                "Sobreestimado": C["red"],
                "Subestimado": C["blue"],
            },
            labels={"Rel_E2": "Relevancia E2 (abstract)", "Rel_E3": "Relevancia E3 (PDF)"},
            hover_data=["ID", "Diferencia"],
            opacity=0.6,
        )
        fig_e2e3.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                           line={"dash": "dash", "color": C["gray"]})
        fig_e2e3.add_hline(y=0.4, line_dash="dot", line_color=C["red"],
                           annotation_text="Umbral E3")
        fig_e2e3.add_vline(x=0.4, line_dash="dot", line_color=C["orange"],
                           annotation_text="Umbral E2")
        fig_e2e3.update_layout(height=500)
        st.plotly_chart(fig_e2e3, use_container_width=True)

        # Histograma de diferencias
        st.subheader("Distribución de diferencias (E3 − E2)")
        fig_diff = px.histogram(
            df_e2e3, x="Diferencia", nbins=30,
            color_discrete_sequence=[C["purple"]],
            labels={"Diferencia": "E3 − E2", "count": "Artículos"},
        )
        fig_diff.add_vline(x=0, line_dash="dash", line_color=C["gray"])
        fig_diff.add_vline(x=0.15, line_dash="dot", line_color=C["blue"],
                           annotation_text="Umbral subestimado")
        fig_diff.add_vline(x=-0.15, line_dash="dot", line_color=C["red"],
                           annotation_text="Umbral sobreestimado")
        fig_diff.update_layout(height=300)
        st.plotly_chart(fig_diff, use_container_width=True)

        # Tabla de casos extremos
        col_s, col_su = st.columns(2)
        with col_s:
            st.markdown("**🔴 Más sobreestimados (E2 >> E3)**")
            df_sobre = df_e2e3[df_e2e3["Resultado"]=="Sobreestimado"].nsmallest(10, "Diferencia")
            st.dataframe(df_sobre[["ID","Rel_E2","Rel_E3","Diferencia"]].round(2),
                         hide_index=True, use_container_width=True)
        with col_su:
            st.markdown("**🔵 Más subestimados (E2 << E3)**")
            df_subes = df_e2e3[df_e2e3["Resultado"]=="Subestimado"].nlargest(10, "Diferencia")
            st.dataframe(df_subes[["ID","Rel_E2","Rel_E3","Diferencia"]].round(2),
                         hide_index=True, use_container_width=True)

    except FileNotFoundError as e:
        st.error(f"Archivo no encontrado: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 17 — CLUSTERS DE MÉTODOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_clusters:
    st.subheader("Clusters de métodos")
    st.caption("4 grupos de métodos similares identificados en el corpus. Fuente: tablas/06_clusters_metodo.json")

    try:
        clust_data = load_tabla("06_clusters_metodo.json")
        clusters = clust_data.get("clusters", [])

        if not clusters:
            st.warning("No hay clusters en el archivo.")
        else:
            # Bubble chart
            df_cl = pd.DataFrame([{
                "Cluster": c["nombre"],
                "Artículos": c["cantidad_articulos"],
                "% corpus": c["porcentaje"],
                "Métodos": ", ".join(c.get("metodos_incluidos", [])[:3]),
                "Años": f"{c['anos_rango'][0]}–{c['anos_rango'][1]}" if c.get("anos_rango") else "—",
                "Intenciones": ", ".join(i.get("intencion","") if isinstance(i, dict) else i
                                         for i in c.get("intenciones_principales", [])[:3]),
            } for c in clusters])

            fig_bub = px.scatter(
                df_cl,
                x="% corpus", y="Cluster",
                size="Artículos",
                color="Cluster",
                color_discrete_sequence=QUAL_COLORS,
                hover_data=["Artículos", "Métodos", "Años", "Intenciones"],
                size_max=70,
                labels={"% corpus": "% del corpus", "Cluster": ""},
            )
            fig_bub.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_bub, use_container_width=True)

            # Cards por cluster
            cols_cl = st.columns(min(len(clusters), 2))
            for idx, c in enumerate(clusters):
                with cols_cl[idx % 2]:
                    int_list = c.get("intenciones_principales", [])
                    int_str = ", ".join(
                        i.get("intencion","") if isinstance(i, dict) else i
                        for i in int_list[:4]
                    )
                    anos = c.get("anos_rango", ["?","?"])
                    st.markdown(
                        f"<div style='border:1px solid #e5e7eb;border-radius:8px;padding:12px;margin-bottom:8px'>"
                        f"<b style='color:{QUAL_COLORS[idx % len(QUAL_COLORS)]}'>{c['nombre']}</b><br>"
                        f"<small>{c['cantidad_articulos']} artículos · {c['porcentaje']}% · {anos[0]}–{anos[1]}</small><br>"
                        f"<hr style='margin:6px 0'>"
                        f"<b>Métodos:</b> {', '.join(c.get('metodos_incluidos',[]))}<br>"
                        f"<b>Intenciones:</b> {int_str}</div>",
                        unsafe_allow_html=True
                    )

            # Tabla artículos representativos por cluster
            st.divider()
            st.subheader("Artículos representativos por cluster")
            cl_sel = st.selectbox(
                "Seleccionar cluster",
                [c["nombre"] for c in clusters],
                key="cl_sel"
            )
            cl_obj = next(c for c in clusters if c["nombre"] == cl_sel)
            reps = cl_obj.get("articulos_representativos", []) or cl_obj.get("todos_articulos", [])
            if reps:
                df_reps = pd.DataFrame([{
                    "ID": a.get("id",""),
                    "Año": a.get("year",""),
                    "Rel.": a.get("relevancia_general", 0),
                    "Título": a.get("titulo","")[:90],
                } for a in reps[:20]])
                st.dataframe(df_reps, hide_index=True, use_container_width=True,
                             column_config={"Rel.": st.column_config.ProgressColumn(
                                 "Rel.", min_value=0, max_value=1, format="%.2f")})

    except FileNotFoundError:
        st.error("No se encontró tablas/06_clusters_metodo.json")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 18 — BIBLIOGRAFÍA (índice buscable + BibTeX)
# ══════════════════════════════════════════════════════════════════════════════
with tab_biblio:
    st.subheader("Índice bibliográfico")
    st.caption("324 artículos con búsqueda y exportación BibTeX. Fuente: tablas/08_indice_referencias.json")

    try:
        ref_data = load_tabla("08_indice_referencias.json")
        mapeo = ref_data.get("mapeo", [])

        busq_bib = st.text_input("🔍 Buscar título, autor o DOI", key="busq_bib")
        year_bib = st.slider("Año", 2020, 2026, (2020, 2026), key="year_bib")

        refs_show = mapeo
        if busq_bib:
            q = busq_bib.lower()
            refs_show = [r for r in refs_show if
                         q in r.get("titulo","").lower() or
                         q in " ".join(r.get("autores",[])).lower() or
                         q in r.get("bibtex_key","").lower()]
        refs_show = [r for r in refs_show if year_bib[0] <= (r.get("year") or 0) <= year_bib[1]]
        refs_show = sorted(refs_show, key=lambda x: -(x.get("relevancia") or 0))

        st.caption(f"{len(refs_show)} referencias")

        df_bib = pd.DataFrame([{
            "Año": r.get("year"),
            "Rel.": r.get("relevancia", 0),
            "Clave BibTeX": r.get("bibtex_key",""),
            "Título": r.get("titulo","")[:90],
            "Autores": ", ".join(r.get("autores",[]))[:60],
            "Cluster": r.get("cluster_metodo",""),
        } for r in refs_show])

        st.dataframe(
            df_bib, use_container_width=True, hide_index=True,
            column_config={
                "Rel.": st.column_config.ProgressColumn("Rel.", min_value=0, max_value=1, format="%.2f"),
                "Título": st.column_config.TextColumn("Título", width="large"),
            }
        )

        # Exportar BibTeX
        st.divider()
        st.subheader("Exportar BibTeX")
        if st.button("📋 Generar BibTeX de referencias filtradas"):
            bibtex_lines = []
            for r in refs_show:
                key = r.get("bibtex_key", r.get("id","ref"))
                autores = " and ".join(r.get("autores",[]))
                titulo = r.get("titulo","").replace("{","").replace("}","")
                year = r.get("year","")
                bibtex_lines.append(
                    f"@article{{{key},\n"
                    f"  author = {{{autores}}},\n"
                    f"  title  = {{{titulo}}},\n"
                    f"  year   = {{{year}}},\n"
                    f"}}"
                )
            bibtex_str = "\n\n".join(bibtex_lines)
            st.code(bibtex_str, language="bibtex")
            st.download_button(
                "⬇️ Descargar .bib",
                bibtex_str.encode("utf-8"),
                "referencias_filtradas.bib",
                "text/plain"
            )

    except FileNotFoundError:
        st.error("No se encontró tablas/08_indice_referencias.json")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 19 — TH9 SUNBURST
# ══════════════════════════════════════════════════════════════════════════════
with tab_th9:
    st.subheader("Taxonomía de hallazgos TH9 — Subcategorías")
    st.caption("TH9 es la categoría más grande (703 hallazgos). Se subcategorizó inductivamente en TH9a, TH9b, TH9c.")

    TH9_PATH = BASE / "paper" / "th9_subcategorias.json"
    if not TH9_PATH.exists():
        st.error("No se encontró paper/th9_subcategorias.json")
    else:
        th9 = load_json(TH9_PATH)
        meta9 = th9.get("meta", {})
        th_counts = meta9.get("th_counts", {})

        # KPI
        k1h, k2h, k3h, k4h = st.columns(4)
        k1h.metric("Total hallazgos", meta9.get("total_hallazgos", 0))
        k2h.metric("TH1–TH8", meta9.get("th1_th8_total", 0))
        k3h.metric("TH9 total", meta9.get("th9_total", 0))
        k4h.metric("TH9 % del total",
                   f"{meta9.get('th9_total',0)/meta9.get('total_hallazgos',1)*100:.1f}%")

        st.divider()

        # Sunburst TH1–TH9 con subcategorías
        th9a_n = meta9.get("th9a_metodos_terminologia_inglesa", 0)
        th9b_n = meta9.get("th9b_contexto_disciplinar", 0)
        th9c_n = meta9.get("th9c_residual", 0)

        labels = ["Todos los hallazgos"]
        parents = [""]
        values = [meta9.get("total_hallazgos", 0)]
        colors_sun = ["#f3f4f6"]

        # TH1-TH8
        for k, v in th_counts.items():
            labels.append(k)
            parents.append("Todos los hallazgos")
            values.append(v)
            colors_sun.append(C["blue"])

        # TH9 como nodo
        labels.append("TH9")
        parents.append("Todos los hallazgos")
        values.append(meta9.get("th9_total", 0))
        colors_sun.append(C["purple"])

        # TH9 subcategorías
        subcat_map = {
            "TH9a — Métodos/Terminología": (th9a_n, C["indigo"]),
            "TH9b — Contexto disciplinar": (th9b_n, C["teal"]),
            "TH9c — Residual":             (th9c_n, C["gray"]),
        }
        for name, (n, color) in subcat_map.items():
            labels.append(name)
            parents.append("TH9")
            values.append(n)
            colors_sun.append(color)

        fig_sun = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker={"colors": colors_sun},
            branchvalues="total",
            hovertemplate="<b>%{label}</b><br>N: %{value}<br>%{percentRoot:.1%} del total<extra></extra>",
        ))
        fig_sun.update_layout(height=550, margin={"t": 10, "b": 10, "l": 10, "r": 10})
        st.plotly_chart(fig_sun, use_container_width=True)

        # Barras TH1–TH9
        st.subheader("Distribución TH1–TH9")
        all_counts = dict(th_counts)
        all_counts["TH9"] = meta9.get("th9_total", 0)
        df_th = pd.DataFrame(sorted(all_counts.items()), columns=["Categoría", "N"])
        fig_th = px.bar(df_th, x="Categoría", y="N",
                        color="Categoría",
                        color_discrete_sequence=QUAL_COLORS + [C["purple"]],
                        text="N")
        fig_th.update_traces(textposition="outside")
        fig_th.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_th, use_container_width=True)

        # Tabla TH9 subcategorías
        st.subheader("Detalle subcategorías TH9")
        df_sub = pd.DataFrame([
            {"Subcategoría": "TH9a — Métodos/Terminología inglesa",
             "N": th9a_n, "%": f"{th9a_n/meta9.get('th9_total',1)*100:.1f}%",
             "Descripción": "Hallazgos sobre denominación técnica en inglés de métodos y conceptos"},
            {"Subcategoría": "TH9b — Contexto disciplinar",
             "N": th9b_n, "%": f"{th9b_n/meta9.get('th9_total',1)*100:.1f}%",
             "Descripción": "Hallazgos sobre campo disciplinar, área o dominio de aplicación"},
            {"Subcategoría": "TH9c — Residual",
             "N": th9c_n, "%": f"{th9c_n/meta9.get('th9_total',1)*100:.1f}%",
             "Descripción": "Hallazgos que no encajan en categorías anteriores"},
        ])
        st.dataframe(df_sub, hide_index=True, use_container_width=True)

        # Explorador de hallazgos TH9a/b/c
        st.divider()
        st.subheader("Explorar hallazgos por subcategoría")
        subcat_sel = st.radio("Subcategoría", ["TH9a", "TH9b", "TH9c"], horizontal=True)
        subcat_key = {"TH9a": "th9a", "TH9b": "th9b", "TH9c": "th9c"}[subcat_sel]
        hallazgos_th9 = th9.get(subcat_key, [])

        busq_th9 = st.text_input("🔍 Filtrar hallazgos", key="busq_th9")
        if busq_th9:
            hallazgos_th9 = [h for h in hallazgos_th9 if busq_th9.lower() in str(h).lower()]

        st.caption(f"{len(hallazgos_th9)} hallazgos en {subcat_sel}")

        if hallazgos_th9:
            sample = hallazgos_th9[:50]
            if isinstance(sample[0], dict):
                df_th9h = pd.DataFrame(sample)
            else:
                df_th9h = pd.DataFrame({"hallazgo": sample})
            st.dataframe(df_th9h, hide_index=True, use_container_width=True)
