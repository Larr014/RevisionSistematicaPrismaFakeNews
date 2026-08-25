#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visor interactivo de resultados - Revisión Sistemática Fase 2
Ejecutar: py -m streamlit run visor_fase2.py
"""

import json
import pathlib
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

try:
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    _WC_AVAILABLE = True
except ImportError:
    _WC_AVAILABLE = False

# Stopwords español + inglés para nubes
_STOPWORDS_ES = {
    "de","la","el","en","y","a","los","del","se","las","por","un","con","una",
    "para","es","al","lo","que","su","le","da","no","o","este","más","pero",
    "sus","ya","sobre","entre","cuando","todo","esta","ser","son","dos","también",
    "fue","había","era","muy","sin","hasta","hay","donde","han","puede","está",
    "sido","tiene","como","si","me","mi","nos","se","al","su","their","been",
    "the","of","and","to","in","a","is","for","on","with","are","that","this",
    "an","by","from","at","be","as","we","our","it","using","based","model",
    "paper","study","results","method","approach","proposed","show","new","two",
    "used","data","analysis","detection","classification","using","also","work",
}

st.set_page_config(
    page_title="Revisión Sistemática · Fase 2",
    page_icon="📚",
    layout="wide",
)

BASE = pathlib.Path(__file__).parent

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

ARCHIVOS = {
    "Todos (549)":          BASE / "clasificacion_pdfs_completos.json",
    "Alta relevancia (324)": BASE / "fase2_relevancia_alta.json",
    "Baja relevancia (225)": BASE / "fase2_relevancia_baja.json",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_field(a, *path, default=None):
    obj = a
    for key in path:
        if isinstance(obj, dict):
            obj = obj.get(key, default)
        else:
            return default
    return obj if obj is not None else default

def flatten(a):
    cl = a.get("clasificacion", {})
    vp = cl.get("variables_principales", {})
    va = cl.get("variables_adicionales", {})
    return {
        "id":               a.get("id", ""),
        "titulo":           a.get("titulo", "Sin título"),
        "autores":          ", ".join(a.get("autores", [])) or "—",
        "year":             a.get("year"),
        "abstract":         a.get("abstract", ""),
        "relevancia":       a.get("relevancia_general", 0.0),
        "metodos_esp":      vp.get("metodos_especifico", []),
        "metodos_gen":      vp.get("metodos_general", []),
        "metricas":         vp.get("metricas", []),
        "intenciones":      vp.get("intenciones", []),
        "datasets":         vp.get("dataset", []),
        "dataset_info":     vp.get("dataset_info", []),
        "plataforma":       va.get("plataforma", []),
        "linguistica":      va.get("linguistica", []),
        "temporal":         va.get("temporal"),
        "metodologica":     va.get("metodologica", []),
        "hallazgos_nuevos": a.get("hallazgos_nuevos", []),
    }

METODOS_LABELS = {
    "M1_LogisticRegression": "Logistic Regression",
    "M2_NaiveBayes": "Naive Bayes",
    "M3_DecisionTree": "Decision Tree",
    "M4_GradientBoosting": "Gradient Boosting",
    "M5_KNN": "KNN",
    "M6_SVM": "SVM",
    "M7_NeuralNetwork": "Neural Network",
    "M8_RandomForest": "Random Forest",
    "M9_NLP_Traditional": "NLP Tradicional",
    "M10_DeepLearning": "Deep Learning",
    "M11_LSTM": "LSTM",
    "M12_Transformer": "Transformer",
    "M13_BERT": "BERT",
    "M14_GraphNetwork": "Graph Network",
    "M15_Ensemble": "Ensemble",
    "M16_Clustering": "Clustering",
    "M17_TopicModeling": "Topic Modeling",
    "M18_SemanticAnalysis": "Semantic Analysis",
    "M19_SentimentAnalysis": "Sentiment Analysis",
    "M20_StylometryAnalysis": "Stylometry",
    "M21_HybridMethod": "Hybrid Method",
}

INTENCIONES_LABELS = {
    "I1_FakeNews": "Fake News",
    "I2_Manipulation": "Manipulation",
    "I3_Misinformation": "Misinformation",
    "I4_Satire": "Satire",
    "I5_Rumors": "Rumors",
    "I6_BotActivity": "Bot Activity",
    "I7_EmotionAnalysis": "Emotion Analysis",
    "I8_PolarityAnalysis": "Polarity Analysis",
    "I9_ToxicContent": "Toxic Content",
    "I10_Deepfakes": "Deepfakes",
    "I11_Coordinated_Behavior": "Coordinated Behavior",
    "I12_SuspiciousActivity": "Suspicious Activity",
    "I13_Credibility_Assessment": "Credibility Assessment",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("📚 Revisión Sistemática")
st.sidebar.markdown("**Métodos para identificar intenciones comunicativas en publicaciones digitales**")
st.sidebar.divider()

archivo_sel = st.sidebar.selectbox("Dataset", list(ARCHIVOS.keys()))
raw = load_json(ARCHIVOS[archivo_sel])
articulos_raw = raw.get("articulos", [])
df_all = [flatten(a) for a in articulos_raw]

st.sidebar.divider()
st.sidebar.subheader("Filtros")

# Relevancia
rel_min, rel_max = st.sidebar.slider("Relevancia", 0.0, 1.0, (0.0, 1.0), 0.05)

# Año
years = sorted(set(r["year"] for r in df_all if r["year"]))
year_min, year_max = st.sidebar.select_slider(
    "Año", options=years, value=(min(years), max(years))
) if years else (None, None)

# Métodos
todos_metodos = sorted(set(m for r in df_all for m in r["metodos_esp"]))
metodos_labels = [METODOS_LABELS.get(m, m) for m in todos_metodos]
metodo_sel_label = st.sidebar.multiselect("Método específico", metodos_labels)
metodo_sel = [todos_metodos[metodos_labels.index(l)] for l in metodo_sel_label]

# Intenciones
todas_intenc = sorted(set(i for r in df_all for i in r["intenciones"]))
intenc_labels = [INTENCIONES_LABELS.get(i, i) for i in todas_intenc]
intenc_sel_label = st.sidebar.multiselect("Intención", intenc_labels)
intenc_sel = [todas_intenc[intenc_labels.index(l)] for l in intenc_sel_label]

# Búsqueda texto
busqueda = st.sidebar.text_input("Buscar en título/abstract", "")

st.sidebar.divider()
solo_hallazgos = st.sidebar.checkbox("Solo con hallazgos nuevos")

# ── Aplicar filtros ────────────────────────────────────────────────────────────
filtrado = df_all

filtrado = [r for r in filtrado if rel_min <= r["relevancia"] <= rel_max]

if year_min and year_max:
    filtrado = [r for r in filtrado if r["year"] and year_min <= r["year"] <= year_max]

if metodo_sel:
    filtrado = [r for r in filtrado if any(m in r["metodos_esp"] for m in metodo_sel)]

if intenc_sel:
    filtrado = [r for r in filtrado if any(i in r["intenciones"] for i in intenc_sel)]

if busqueda:
    q = busqueda.lower()
    filtrado = [r for r in filtrado
                if q in r["titulo"].lower() or q in r["abstract"].lower()]

if solo_hallazgos:
    filtrado = [r for r in filtrado if r["hallazgos_nuevos"]]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Visor · Fase 2 — Clasificación de Artículos")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Artículos (dataset)", len(df_all))
col2.metric("Filtrados", len(filtrado))
col3.metric("Relevancia promedio", f"{sum(r['relevancia'] for r in filtrado)/len(filtrado):.2f}" if filtrado else "—")
col4.metric("Con hallazgos nuevos", sum(1 for r in filtrado if r["hallazgos_nuevos"]))

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📋 Tabla", "📈 Gráficos", "🔍 Detalle artículo", "📦 Datasets", "☁️ Nubes", "💡 Hallazgos", "🔬 Síntesis"])

# ─────────────────── TAB 1: TABLA ─────────────────────────────────────────────
with tab1:
    df_tabla = pd.DataFrame([{
        "ID":         r["id"],
        "Año":        r["year"],
        "Relevancia": r["relevancia"],
        "Título":     r["titulo"],
        "Métodos":    ", ".join(METODOS_LABELS.get(m, m) for m in r["metodos_esp"]),
        "Intenciones": ", ".join(INTENCIONES_LABELS.get(i, i) for i in r["intenciones"]),
        "Plataforma": ", ".join(r["plataforma"]),
        "Lengua":     ", ".join(r["linguistica"]),
    } for r in filtrado])

    st.dataframe(
        df_tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Relevancia": st.column_config.ProgressColumn("Relevancia", min_value=0, max_value=1, format="%.2f"),
            "Título": st.column_config.TextColumn("Título", width="large"),
        }
    )

    csv = df_tabla.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar CSV", csv, "articulos_filtrados.csv", "text/csv")

# ─────────────────── TAB 2: GRÁFICOS ──────────────────────────────────────────
with tab2:
    if not filtrado:
        st.info("Sin datos para los filtros actuales.")
    else:
        col_a, col_b = st.columns(2)

        # Distribución de relevancia
        with col_a:
            st.subheader("Distribución de relevancia")
            rel_vals = [r["relevancia"] for r in filtrado]
            fig = px.histogram(x=rel_vals, nbins=20, labels={"x": "Relevancia", "y": "Artículos"},
                               color_discrete_sequence=["#4C78A8"])
            fig.update_layout(bargap=0.05, height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Artículos por año
        with col_b:
            st.subheader("Artículos por año")
            year_counts = Counter(r["year"] for r in filtrado if r["year"])
            df_years = pd.DataFrame(sorted(year_counts.items()), columns=["Año", "Cantidad"])
            fig2 = px.bar(df_years, x="Año", y="Cantidad", color_discrete_sequence=["#54A24B"])
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)

        col_c, col_d = st.columns(2)

        # Top métodos
        with col_c:
            st.subheader("Métodos más frecuentes")
            metodo_counts = Counter(m for r in filtrado for m in r["metodos_esp"])
            df_met = pd.DataFrame(
                [(METODOS_LABELS.get(k, k), v) for k, v in metodo_counts.most_common(15)],
                columns=["Método", "Frecuencia"]
            )
            fig3 = px.bar(df_met, x="Frecuencia", y="Método", orientation="h",
                          color_discrete_sequence=["#E45756"])
            fig3.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig3, use_container_width=True)

        # Top intenciones
        with col_d:
            st.subheader("Intenciones más frecuentes")
            intenc_counts = Counter(i for r in filtrado for i in r["intenciones"])
            df_int = pd.DataFrame(
                [(INTENCIONES_LABELS.get(k, k), v) for k, v in intenc_counts.most_common(13)],
                columns=["Intención", "Frecuencia"]
            )
            fig4 = px.bar(df_int, x="Frecuencia", y="Intención", orientation="h",
                          color_discrete_sequence=["#F58518"])
            fig4.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig4, use_container_width=True)

        # Scatter relevancia vs año
        st.subheader("Relevancia por año")
        df_scatter = pd.DataFrame([{
            "Año": r["year"], "Relevancia": r["relevancia"],
            "Título": r["titulo"][:60], "ID": r["id"]
        } for r in filtrado if r["year"]])
        fig5 = px.strip(df_scatter, x="Año", y="Relevancia", hover_data=["Título", "ID"],
                        color_discrete_sequence=["#72B7B2"])
        fig5.update_layout(height=350)
        st.plotly_chart(fig5, use_container_width=True)

# ─────────────────── TAB 3: DETALLE ARTÍCULO ──────────────────────────────────
with tab3:
    if not filtrado:
        st.info("Sin artículos con los filtros actuales.")
    else:
        opciones = {f"[{r['relevancia']:.2f}] {r['titulo'][:80]} ({r['year']})": r for r in
                    sorted(filtrado, key=lambda x: -x["relevancia"])}
        sel = st.selectbox("Selecciona un artículo", list(opciones.keys()))
        r = opciones[sel]

        col_m, col_r = st.columns([3, 1])
        col_m.markdown(f"### {r['titulo']}")
        col_r.metric("Relevancia", f"{r['relevancia']:.2f}")

        st.markdown(f"**Autores:** {r['autores']}  \n**Año:** {r['year']}  \n**ID:** `{r['id']}`")
        st.markdown(f"**Abstract:** {r['abstract']}")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Métodos específicos**")
            for m in r["metodos_esp"]:
                st.markdown(f"- {METODOS_LABELS.get(m, m)} `{m}`")
            st.markdown("**Métodos generales**")
            for m in r["metodos_gen"]:
                st.markdown(f"- {m}")
            st.markdown("**Métricas**")
            for m in r["metricas"]:
                st.markdown(f"- `{m}`")

        with col2:
            st.markdown("**Intenciones**")
            for i in r["intenciones"]:
                st.markdown(f"- {INTENCIONES_LABELS.get(i, i)} `{i}`")
            st.markdown("**Plataforma**")
            st.markdown(", ".join(r["plataforma"]) or "—")
            st.markdown("**Lengua**")
            st.markdown(", ".join(r["linguistica"]) or "—")

        if r["dataset_info"]:
            st.divider()
            st.markdown("**Datasets utilizados**")
            for ds in r["dataset_info"]:
                nombre = ds.get("nombre", "?")
                url    = ds.get("url")
                ref    = ds.get("referencia", "")
                if url:
                    st.markdown(f"- **[{nombre}]({url})** — {ref}")
                else:
                    st.markdown(f"- **{nombre}** — {ref}")

        if r["hallazgos_nuevos"]:
            st.divider()
            st.markdown("**Hallazgos nuevos**")
            for h in r["hallazgos_nuevos"]:
                st.markdown(f"- {h}")

# ─────────────────── TAB 4: DATASETS ──────────────────────────────────────────
with tab4:
    st.subheader("Datasets referenciados en los artículos filtrados")

    dataset_counter = Counter(ds for r in filtrado for ds in r["datasets"])
    df_ds = pd.DataFrame(dataset_counter.most_common(40), columns=["Dataset", "Artículos"])

    fig_ds = px.bar(df_ds, x="Artículos", y="Dataset", orientation="h",
                    color_discrete_sequence=["#B279A2"])
    fig_ds.update_layout(height=max(400, len(df_ds) * 22),
                         yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_ds, use_container_width=True)

    st.subheader("Detalle con URLs")
    ds_detalle = {}
    for r in filtrado:
        for ds in r.get("dataset_info", []):
            nombre = ds.get("nombre", "?")
            if nombre not in ds_detalle:
                ds_detalle[nombre] = {"url": ds.get("url"), "ref": ds.get("referencia", ""), "count": 0}
            ds_detalle[nombre]["count"] += 1

    df_det = pd.DataFrame([
        {"Dataset": k, "Artículos": v["count"],
         "URL": v["url"] or "—", "Referencia": v["ref"][:80]}
        for k, v in sorted(ds_detalle.items(), key=lambda x: -x[1]["count"])
    ])
    st.dataframe(df_det, use_container_width=True, hide_index=True,
                 column_config={"URL": st.column_config.LinkColumn("URL")})

# ─────────────────── TAB 5: NUBES DE PALABRAS ─────────────────────────────────
with tab5:
    if not _WC_AVAILABLE:
        st.warning("Instala `wordcloud` y `matplotlib` para usar esta sección:\n```\npip install wordcloud matplotlib\n```")
    elif not filtrado:
        st.info("Sin datos para los filtros actuales.")
    else:
        def make_wordcloud(text, title):
            sw = _STOPWORDS_ES | STOPWORDS
            wc = WordCloud(
                width=900, height=420, background_color="white",
                stopwords=sw, colormap="viridis",
                max_words=120, collocations=False,
            ).generate(text)
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            ax.set_title(title, fontsize=13, pad=10)
            return fig

        nube_opts = ["Títulos", "Abstracts", "Hallazgos nuevos"]
        nube_sel = st.radio("Fuente de texto", nube_opts, horizontal=True)

        if nube_sel == "Títulos":
            corpus = " ".join(r["titulo"] for r in filtrado if r["titulo"])
        elif nube_sel == "Abstracts":
            corpus = " ".join(r["abstract"] for r in filtrado if r["abstract"])
        else:
            corpus = " ".join(h for r in filtrado for h in r["hallazgos_nuevos"])

        if corpus.strip():
            fig_wc = make_wordcloud(corpus, f"Nube de palabras — {nube_sel} ({len(filtrado)} artículos)")
            st.pyplot(fig_wc)
            plt.close(fig_wc)
        else:
            st.info("No hay texto disponible para la selección actual.")

        # Nube comparativa alta vs baja relevancia
        st.divider()
        st.subheader("Comparativa: alta vs baja relevancia")
        alta = [r for r in filtrado if r["relevancia"] >= 0.7]
        baja = [r for r in filtrado if r["relevancia"] < 0.7]
        if alta and baja:
            col_wc1, col_wc2 = st.columns(2)
            fuente_comp = st.selectbox("Texto para comparativa", ["Títulos", "Abstracts", "Hallazgos nuevos"], key="wc_comp")
            def _corpus(rows, fuente):
                if fuente == "Títulos":
                    return " ".join(r["titulo"] for r in rows)
                elif fuente == "Abstracts":
                    return " ".join(r["abstract"] for r in rows)
                return " ".join(h for r in rows for h in r["hallazgos_nuevos"])
            with col_wc1:
                t = _corpus(alta, fuente_comp)
                if t.strip():
                    fig_a = make_wordcloud(t, f"Alta relevancia (≥0.7) — {len(alta)} arts.")
                    st.pyplot(fig_a); plt.close(fig_a)
            with col_wc2:
                t = _corpus(baja, fuente_comp)
                if t.strip():
                    fig_b = make_wordcloud(t, f"Baja relevancia (<0.7) — {len(baja)} arts.")
                    st.pyplot(fig_b); plt.close(fig_b)

# ─────────────────── TAB 6: HALLAZGOS ─────────────────────────────────────────
with tab6:
    st.subheader("Hallazgos nuevos por artículo")

    hallazgos_rows = []
    for r in filtrado:
        for h in r["hallazgos_nuevos"]:
            hallazgos_rows.append({
                "Año":        r["year"],
                "Relevancia": r["relevancia"],
                "Hallazgo":   h,
                "Título":     r["titulo"],
                "ID":         r["id"],
            })

    if not hallazgos_rows:
        st.info("No hay hallazgos nuevos en los artículos filtrados.")
    else:
        busq_h = st.text_input("Buscar en hallazgos", "", key="busq_hallazgos")
        if busq_h:
            q = busq_h.lower()
            hallazgos_rows = [h for h in hallazgos_rows if q in h["Hallazgo"].lower() or q in h["Título"].lower()]

        st.caption(f"{len(hallazgos_rows)} hallazgos en {sum(1 for r in filtrado if r['hallazgos_nuevos'])} artículos")

        df_h = pd.DataFrame(hallazgos_rows)
        st.dataframe(
            df_h,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Relevancia": st.column_config.ProgressColumn("Relevancia", min_value=0, max_value=1, format="%.2f"),
                "Hallazgo":   st.column_config.TextColumn("Hallazgo", width="large"),
                "Título":     st.column_config.TextColumn("Título", width="medium"),
            }
        )

        # Top palabras en hallazgos
        st.divider()
        st.subheader("Frecuencia de términos en hallazgos")
        all_words = []
        for row in hallazgos_rows:
            words = re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,}\b", row["Hallazgo"].lower())
            all_words.extend([w for w in words if w not in _STOPWORDS_ES])
        if all_words:
            word_freq = Counter(all_words).most_common(25)
            df_wf = pd.DataFrame(word_freq, columns=["Término", "Frecuencia"])
            fig_wf = px.bar(df_wf, x="Frecuencia", y="Término", orientation="h",
                            color_discrete_sequence=["#3E7EBF"])
            fig_wf.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_wf, use_container_width=True)

        csv_h = df_h.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar hallazgos CSV", csv_h, "hallazgos.csv", "text/csv")

# ─────────────────── TAB 7: SÍNTESIS ──────────────────────────────────────────
with tab7:
    SINTESIS_PATH = BASE / "sintesis_hallazgos_revision.json"

    if not SINTESIS_PATH.exists():
        st.warning("No se encontró `sintesis_hallazgos_revision.json` en el directorio.")
    else:
        @st.cache_data
        def load_sintesis():
            with open(SINTESIS_PATH, encoding="utf-8") as f:
                return json.load(f)

        sint = load_sintesis()
        ejes = sint.get("ejes_tematicos", [])

        ROL_COLOR = {
            "tendencia":   "#2196F3",
            "limitacion":  "#FF5722",
            "brecha":      "#9C27B0",
            "oportunidad": "#4CAF50",
        }
        ROL_LABEL = {
            "tendencia":   "↗ Tendencia",
            "limitacion":  "⚠ Limitación",
            "brecha":      "○ Brecha",
            "oportunidad": "★ Oportunidad",
        }

        # ── Gap central ────────────────────────────────────────────────────────
        gap = sint.get("gap_central_identificado", "")
        if gap:
            st.markdown("### Gap central identificado")
            st.info(gap)
            st.divider()

        # ── Convergencias transversales ────────────────────────────────────────
        convergencias = sint.get("convergencias_transversales", [])
        if convergencias:
            with st.expander("🔗 Convergencias transversales entre ejes", expanded=False):
                for c in convergencias:
                    st.markdown(f"- {c}")
            st.divider()

        # ── Navegación cruzada ─────────────────────────────────────────────────
        st.markdown("### Ejes temáticos")
        eje_nombres = [f"{e['id']} — {e['eje']}" for e in ejes]
        eje_sel_label = st.selectbox("Ir a eje", ["(todos)"] + eje_nombres, key="eje_nav")

        ejes_mostrar = ejes if eje_sel_label == "(todos)" else [
            e for e in ejes if f"{e['id']} — {e['eje']}" == eje_sel_label
        ]

        for eje in ejes_mostrar:
            with st.expander(f"**{eje['id']}** — {eje['eje']}", expanded=(eje_sel_label != "(todos)")):
                st.markdown(f"*{eje.get('descripcion', '')}*")
                st.divider()

                sint_data = eje.get("sintesis", {})

                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    tendencias = sint_data.get("tendencias", [])
                    if tendencias:
                        st.markdown("**↗ Tendencias identificadas**")
                        for t in tendencias:
                            st.markdown(f"- {t}")

                    limitaciones = sint_data.get("limitaciones_identificadas", [])
                    if limitaciones:
                        st.markdown("**⚠ Limitaciones**")
                        for l in limitaciones:
                            st.markdown(f"- {l}")

                with col_s2:
                    brechas = sint_data.get("brechas", [])
                    if brechas:
                        st.markdown("**○ Brechas detectadas**")
                        for b in brechas:
                            st.markdown(f"- {b}")

                    preguntas = sint_data.get("preguntas_que_emergen", [])
                    if preguntas:
                        st.markdown("**? Preguntas que emergen**")
                        for p in preguntas:
                            st.markdown(f"- *{p}*")

                # Hallazgos representativos del eje
                h_eje = eje.get("hallazgos_representativos", [])
                if h_eje:
                    st.divider()
                    st.markdown(f"**Hallazgos representativos ({len(h_eje)})**")
                    for h in h_eje:
                        rol = h.get("rol", "tendencia")
                        color = ROL_COLOR.get(rol, "#888")
                        label = ROL_LABEL.get(rol, rol)
                        year = h.get("year", "")
                        st.markdown(
                            f"<span style='background:{color};color:white;padding:2px 7px;"
                            f"border-radius:4px;font-size:0.78em'>{label}</span> "
                            f"<span style='color:#888;font-size:0.85em'>({year})</span> "
                            f"{h.get('hallazgo', '')}",
                            unsafe_allow_html=True
                        )

                # Cruce con artículos filtrados del dataset activo
                ids_eje = {h.get("articulo_id", "") for h in h_eje}
                arts_cruce = [r for r in filtrado if r["id"] in ids_eje]
                if arts_cruce:
                    st.divider()
                    st.caption(f"{len(arts_cruce)} artículo(s) de este eje están en el dataset filtrado actual")
                    df_cruce = pd.DataFrame([{
                        "ID": r["id"], "Año": r["year"],
                        "Relevancia": r["relevancia"],
                        "Título": r["titulo"][:80],
                    } for r in arts_cruce])
                    st.dataframe(df_cruce, use_container_width=True, hide_index=True,
                                 column_config={"Relevancia": st.column_config.ProgressColumn(
                                     "Relevancia", min_value=0, max_value=1, format="%.2f")})
