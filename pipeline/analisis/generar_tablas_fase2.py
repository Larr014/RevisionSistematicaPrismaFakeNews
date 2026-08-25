#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera 13 tablas JSON a partir de fase2_relevancia_alta.json.

Tablas 01-03, 05-10: versión estándar + versión _h (con hallazgos_nuevos embebidos)
Tablas 04, 11, 12, 13: una sola versión

Cada entrada de artículo incluye: id, bibtex_key, titulo, autores, year, relevancia
La versión _h agrega además: hallazgos_nuevos

Output: tablas/  (mismo directorio que el script original)
"""

import json
import os
import re
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

INPUT_FILE  = r"C:\Users\Luis Rojas\.openclaw\workspace\fase2_relevancia_alta.json"
OUTPUT_DIR  = r"C:\Users\Luis Rojas\.openclaw\workspace\tablas"
FECHA       = datetime.now().strftime("%Y-%m-%d")

Path(OUTPUT_DIR).mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def make_bibtex_key(art):
    """Genera clave BibTeX: apellido1+año+palabra_clave (ej. yang2024stylometry)."""
    autores = art.get("autores", [])
    year    = art.get("year", "")
    titulo  = art.get("titulo", "")

    if autores:
        apellido = autores[0].split()[-1].lower()
        apellido = unicodedata.normalize("NFKD", apellido)
        apellido = "".join(c for c in apellido if unicodedata.category(c) != "Mn")
        apellido = re.sub(r"[^a-z]", "", apellido)
    else:
        apellido = "unknown"

    stop = {"a", "an", "the", "of", "in", "on", "for", "and", "or", "to",
            "with", "using", "based", "towards", "toward", "via", "from",
            "new", "novel", "approach", "method", "detection", "analysis"}
    words   = re.sub(r"[^a-zA-Z\s]", "", titulo).lower().split()
    keyword = next((w for w in words if w not in stop and len(w) > 2),
                   words[0] if words else "paper")
    keyword = keyword[:12]

    return f"{apellido}{year}{keyword}"


def make_art_ref(art, include_hallazgos=False):
    """Referencia compacta de un artículo para embeber en las tablas."""
    ref = {
        "id":          art["id"],
        "bibtex_key":  make_bibtex_key(art),
        "titulo":      art["titulo"],
        "autores":     art.get("autores", []),
        "year":        art.get("year"),
        "relevancia":  art.get("relevancia_general", 0),
    }
    if include_hallazgos:
        ref["hallazgos_nuevos"] = art.get("hallazgos_nuevos", [])
    return ref


def save_json(obj, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

LABELS = {
    # Métodos específicos
    "M1_LogisticRegression":  "Regresión Logística",
    "M2_NaiveBayes":          "Naive Bayes",
    "M4_GradientBoosting":    "Gradient Boosting",
    "M5_KNN":                 "K-Nearest Neighbors",
    "M6_SVM":                 "SVM",
    "M7_NeuralNetwork":       "Red Neuronal",
    "M8_RandomForest":        "Random Forest",
    "M9_NLP_Traditional":     "NLP Tradicional",
    "M10_DeepLearning":       "Deep Learning",
    "M11_LSTM":               "LSTM/RNN",
    "M12_Transformer":        "Transformer",
    "M13_BERT":               "BERT",
    "M14_GraphNetwork":       "Graph Neural Network",
    "M15_Ensemble":           "Ensemble",
    "M16_AttentionMechanism": "Mecanismo de Atención",
    "M17_CNN":                "CNN",
    "M18_AutoML":             "AutoML",
    "M19_SentimentAnalysis":  "Análisis de Sentimiento",
    "M20_StylometryAnalysis": "Análisis Estilométrico",
    "M21_HybridMethod":       "Método Híbrido",
    "M22_RulesBased":         "Basado en Reglas",
    "M23_FeatureEngineering": "Feature Engineering",
    # Métodos generales
    "Machine Learning":       "Machine Learning",
    "Deep Learning":          "Deep Learning",
    "NLP":                    "NLP",
    "Statistical Analysis":   "Análisis Estadístico",
    "Linguistic Analysis":    "Análisis Lingüístico",
    "Graph Analysis":         "Análisis de Grafos",
    "Hybrid":                 "Híbrido",
    # Intenciones
    "I1_FakeNews":              "Fake News",
    "I2_Manipulation":          "Manipulación",
    "I3_Misinformation":        "Desinformación",
    "I4_Satire":                "Sátira",
    "I5_Rumors":                "Rumores",
    "I6_BotActivity":           "Actividad de Bots",
    "I7_EmotionAnalysis":       "Análisis de Emociones",
    "I8_PolarityAnalysis":      "Análisis de Polaridad",
    "I9_ToxicContent":          "Contenido Tóxico",
    "I10_Deepfakes":            "Deepfakes",
    "I11_Coordinated_Behavior": "Comportamiento Coordinado",
    "I12_SuspiciousActivity":   "Actividad Sospechosa",
    "I13_Credibility_Assessment": "Evaluación de Credibilidad",
    # Plataformas
    "P1_Twitter":   "Twitter/X",
    "P2_Facebook":  "Facebook",
    "P3_News":      "Noticias Online",
    "P4_Reddit":    "Reddit",
    "P5_Instagram": "Instagram",
    "P6_YouTube":   "YouTube",
    "P7_TikTok":    "TikTok",
    "P8_Telegram":  "Telegram",
    "P9_WhatsApp":  "WhatsApp",
    "P10_Multiple": "Múltiples Plataformas",
    "P11_General":  "General/No especificado",
    # Lingüística
    "L1_English":      "Inglés",
    "L2_Spanish":      "Español",
    "L3_Chinese":      "Chino",
    "L4_Arabic":       "Árabe",
    "L5_French":       "Francés",
    "L6_German":       "Alemán",
    "L7_Multilingual": "Multilingüe",
    "L8_NotSpecified": "No especificado",
    # Métricas
    "D1_Precision_Recall": "Precisión/Recall",
    "D2_F1Score":          "F1-Score",
    "D3_Accuracy":         "Accuracy",
    "D4_AUC_ROC":          "AUC-ROC",
    "D5_Confusion_Matrix": "Matriz de Confusión",
}


def get_label(codigo):
    return LABELS.get(codigo, codigo)


# ---------------------------------------------------------------------------
# Definiciones de clusters y temas
# ---------------------------------------------------------------------------

DL_METODOS     = ["M10_DeepLearning", "M11_LSTM", "M12_Transformer", "M13_BERT",
                   "M7_NeuralNetwork", "M17_CNN", "M16_AttentionMechanism"]
ML_METODOS     = ["M1_LogisticRegression", "M2_NaiveBayes", "M4_GradientBoosting",
                   "M5_KNN", "M6_SVM", "M8_RandomForest", "M15_Ensemble", "M18_AutoML"]
NLP_METODOS    = ["M9_NLP_Traditional", "M19_SentimentAnalysis", "M20_StylometryAnalysis",
                   "M22_RulesBased", "M23_FeatureEngineering"]
HYBRID_METODOS = ["M14_GraphNetwork", "M21_HybridMethod"]

CLUSTERS_METODO = [
    ("CL_M1_DeepLearning",    "Deep Learning",              DL_METODOS),
    ("CL_M2_MachineLearning", "Machine Learning",           ML_METODOS),
    ("CL_M3_NLP",             "NLP / Análisis Lingüístico", NLP_METODOS),
    ("CL_M4_HybridGraph",     "Híbrido / Grafos",           HYBRID_METODOS),
]

INTENCIONES_ORDEN = [
    "I1_FakeNews", "I3_Misinformation", "I13_Credibility_Assessment",
    "I2_Manipulation", "I7_EmotionAnalysis", "I5_Rumors",
    "I8_PolarityAnalysis", "I9_ToxicContent", "I6_BotActivity",
    "I10_Deepfakes", "I4_Satire", "I11_Coordinated_Behavior", "I12_SuspiciousActivity",
]

CARACTERISTICAS_MAP = {
    "M10_DeepLearning":       "Representaciones profundas (Deep Learning)",
    "M11_LSTM":               "Características secuenciales (LSTM/RNN)",
    "M12_Transformer":        "Embeddings contextuales (Transformer)",
    "M13_BERT":               "Embeddings contextuales (BERT)",
    "M14_GraphNetwork":       "Características de grafo (GNN)",
    "M15_Ensemble":           "Combinación de características (Ensemble)",
    "M16_AttentionMechanism": "Mecanismo de atención",
    "M17_CNN":                "Características convolucionales (CNN)",
    "M19_SentimentAnalysis":  "Polaridad y sentimiento",
    "M20_StylometryAnalysis": "Características estilométricas",
    "M21_HybridMethod":       "Características multimodales (Híbrido)",
    "M1_LogisticRegression":  "TF-IDF + Vectorización",
    "M2_NaiveBayes":          "Frecuencia de palabras",
    "M4_GradientBoosting":    "TF-IDF + Vectorización",
    "M6_SVM":                 "TF-IDF + Vectorización",
    "M7_NeuralNetwork":       "Representaciones profundas (NN)",
    "M8_RandomForest":        "TF-IDF + Vectorización",
    "M9_NLP_Traditional":     "Palabras clave + Patrones lingüísticos",
    "M22_RulesBased":         "Reglas y patrones definidos manualmente",
    "M23_FeatureEngineering": "Ingeniería de características manual",
}

TEMAS_HALLAZGOS = [
    {
        "id": "TH1",
        "nombre": "Métodos y algoritmos emergentes",
        "descripcion": "Nuevos clasificadores, variantes de modelos y arquitecturas no cubiertas en la taxonomía base",
        "keywords": ["clasificador", "algoritmo", "xgboost", "adaboost", "lightgbm", "catboost",
                     "deberta", "roberta", "llama", "gpt-4", "mistral", "chatgpt",
                     "modelo", "arquitectura", "red neur"],
        "rq": "RQ1",
    },
    {
        "id": "TH2",
        "nombre": "Taxonomías y esquemas de clasificación de intención",
        "descripcion": "Nuevas formas de categorizar intenciones comunicativas o desinformación",
        "keywords": ["intencion", "intenci", "categoria", "tipo de", "hoax", "propaganda",
                     "satira", "satire", "engano", "esquema", "taxonom"],
        "rq": "RQ3",
    },
    {
        "id": "TH3",
        "nombre": "Características lingüísticas y estilométricas",
        "descripcion": "Features textuales, métricas de estilo y análisis lingüístico no estándar",
        "keywords": ["lexic", "sintact", "estilometr", "stylom", "readability", "flesch",
                     "gunning", "yule", "mtld", "n-gram", "tf-idf", "tfidf",
                     "embedding", "feature", "caracteristic", "legibilid"],
        "rq": "RQ1",
    },
    {
        "id": "TH4",
        "nombre": "Evaluación, benchmarks y datasets",
        "descripcion": "Nuevas métricas de evaluación, datasets novedosos o benchmarks específicos del dominio",
        "keywords": ["dataset", "corpus", "benchmark", "evaluacion", "evalua",
                     "metrica", "medida", "conjunto de dato", "datos etiquetados"],
        "rq": "RQ1",
    },
    {
        "id": "TH5",
        "nombre": "Limitaciones y brechas identificadas",
        "descripcion": "Gaps explícitos, problemas no resueltos y limitaciones metodológicas reportadas",
        "keywords": ["limitacion", "limitaci", "no puede", "no detecta", "dificultad",
                     "sesgo", "bias", "gap", "carencia", "no resuelto"],
        "rq": "Pregunta Principal",
    },
    {
        "id": "TH6",
        "nombre": "Arquitecturas especializadas y enfoques novedosos",
        "descripcion": "Métodos de grafos, multimodales, few-shot, inductive learning y otros enfoques avanzados",
        "keywords": ["grafo", "graph", "multimodal", "cross-lingual", "transfer",
                     "few-shot", "zero-shot", "inductiv", "heterog", "meta-path",
                     "knowledge graph", "propagacion", "propagaci", "cascada"],
        "rq": "RQ1",
    },
    {
        "id": "TH7",
        "nombre": "Análisis multilingüe y cross-cultural",
        "descripcion": "Hallazgos sobre procesamiento en múltiples idiomas o análisis comparativo entre culturas",
        "keywords": ["multilingu", "multilingue", "cross-lingual", "idioma", "arabic",
                     "chinese", "spanish", "hindi", "urdu", "portuguese", "lengua"],
        "rq": "RQ3",
    },
    {
        "id": "TH8",
        "nombre": "Patrones de comportamiento y propagación",
        "descripcion": "Patrones temporales, redes sociales, comportamiento coordinado y análisis de difusión",
        "keywords": ["propagacion", "propagaci", "difusion", "difusi", "temporal",
                     "timeline", "patron", "comportamiento", "bot", "coordinado",
                     "red social", "usuario"],
        "rq": "RQ2",
    },
]


# ---------------------------------------------------------------------------
# Funciones de tabla
# ---------------------------------------------------------------------------

def tabla1_distribuciones(data, include_hallazgos=False):
    articulos = data["articulos"]
    n = len(articulos)

    buckets = {
        "metodos_especificos": defaultdict(list),
        "metodos_generales":   defaultdict(list),
        "intenciones":         defaultdict(list),
        "metricas":            defaultdict(list),
        "plataformas":         defaultdict(list),
        "linguistica":         defaultdict(list),
    }

    for art in articulos:
        ref = make_art_ref(art, include_hallazgos)
        vp  = art["clasificacion"]["variables_principales"]
        va  = art["clasificacion"]["variables_adicionales"]

        for m in (vp.get("metodos_especifico") or []):
            buckets["metodos_especificos"][m].append(ref)
        for m in (vp.get("metodos_general") or []):
            buckets["metodos_generales"][m].append(ref)
        for i in (vp.get("intenciones") or []):
            buckets["intenciones"][i].append(ref)
        for me in (vp.get("metricas") or []):
            buckets["metricas"][me].append(ref)
        for p in (va.get("plataforma") or []):
            buckets["plataformas"][p].append(ref)
        for l in (va.get("linguistica") or []):
            buckets["linguistica"][l].append(ref)

    distribuciones = {}
    for cat, items in buckets.items():
        distribuciones[cat] = sorted([
            {
                "codigo":     k,
                "nombre":     get_label(k),
                "cantidad":   len(v),
                "porcentaje": round(100 * len(v) / n, 1),
                "articulos":  sorted(v, key=lambda x: x["relevancia"], reverse=True),
            }
            for k, v in items.items()
        ], key=lambda x: x["cantidad"], reverse=True)

    return {
        "tipo":                   "distribuciones_agregadas",
        "fecha_generacion":       FECHA,
        "fuente":                 "fase2_relevancia_alta.json",
        "total_articulos":        n,
        "con_hallazgos_embebidos": include_hallazgos,
        "distribuciones":         distribuciones,
    }


def tabla2_cruzada(data, include_hallazgos=False):
    articulos = data["articulos"]
    cruzada   = defaultdict(lambda: defaultdict(list))

    for art in articulos:
        ref       = make_art_ref(art, include_hallazgos)
        vp        = art["clasificacion"]["variables_principales"]
        metodos   = vp.get("metodos_especifico") or ["Sin_Metodo"]
        intenciones = vp.get("intenciones") or ["Sin_Intencion"]

        for m in metodos:
            for i in intenciones:
                cruzada[m][i].append(ref)

    metodos_ordenados = sorted(
        cruzada.keys(),
        key=lambda m: sum(len(v) for v in cruzada[m].values()),
        reverse=True,
    )

    return {
        "tipo":                   "cruzada_metodo_intencion",
        "fuente":                 "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos": include_hallazgos,
        "metodos": [
            {
                "metodo":          m,
                "metodo_label":    get_label(m),
                "total_articulos": sum(len(v) for v in cruzada[m].values()),
                "intenciones": sorted([
                    {
                        "intencion":       i,
                        "intencion_label": get_label(i),
                        "cantidad":        len(arts),
                        "articulos":       sorted(arts, key=lambda x: x["relevancia"], reverse=True),
                    }
                    for i, arts in cruzada[m].items()
                ], key=lambda x: x["cantidad"], reverse=True),
            }
            for m in metodos_ordenados
        ],
    }


def tabla3_temporal(data, include_hallazgos=False):
    articulos = data["articulos"]
    temporal  = defaultdict(lambda: {
        "total": 0, "binario": 0, "granular": 0,
        "articulos": [],
        "metodos": defaultdict(list),
        "intenciones": defaultdict(list),
    })

    for art in articulos:
        year = art.get("year")
        if not year:
            continue
        ref = make_art_ref(art, include_hallazgos)
        vp  = art["clasificacion"]["variables_principales"]
        intenciones = vp.get("intenciones") or []

        temporal[year]["total"] += 1
        temporal[year]["articulos"].append(ref)
        if len(intenciones) <= 1:
            temporal[year]["binario"] += 1
        else:
            temporal[year]["granular"] += 1

        for m in (vp.get("metodos_especifico") or []):
            temporal[year]["metodos"][m].append(ref)
        for i in intenciones:
            temporal[year]["intenciones"][i].append(ref)

    anos = []
    for year in sorted(temporal.keys()):
        d     = temporal[year]
        total = d["total"]
        anos.append({
            "ano":                 year,
            "total_articulos":     total,
            "enfoque_binario_n":   d["binario"],
            "enfoque_binario_pct": round(100 * d["binario"] / total, 1),
            "enfoque_granular_n":  d["granular"],
            "enfoque_granular_pct": round(100 * d["granular"] / total, 1),
            "metodos_top5": sorted(
                [{"metodo": get_label(k), "cantidad": len(v), "articulos": v}
                 for k, v in d["metodos"].items()],
                key=lambda x: x["cantidad"], reverse=True,
            )[:5],
            "intenciones_top5": sorted(
                [{"intencion": get_label(k), "cantidad": len(v), "articulos": v}
                 for k, v in d["intenciones"].items()],
                key=lambda x: x["cantidad"], reverse=True,
            )[:5],
            "articulos": d["articulos"],
        })

    return {
        "tipo":                   "evolucion_temporal",
        "fuente":                 "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos": include_hallazgos,
        "anos":                   anos,
    }


def tabla4_resumen_agregado(data):
    articulos = data["articulos"]
    n         = len(articulos)
    relevs    = [a.get("relevancia_general", 0) for a in articulos]
    years     = [a["year"] for a in articulos if a.get("year")]

    con_metodo    = sum(1 for a in articulos if a["clasificacion"]["variables_principales"].get("metodos_especifico"))
    con_intencion = sum(1 for a in articulos if a["clasificacion"]["variables_principales"].get("intenciones"))
    alta_rel      = sum(1 for r in relevs if r >= 0.8)
    media_rel     = sum(1 for r in relevs if 0.6 <= r < 0.8)
    baja_rel      = sum(1 for r in relevs if r < 0.6)
    total_hall    = sum(len(a.get("hallazgos_nuevos", [])) for a in articulos)
    con_hall      = sum(1 for a in articulos if a.get("hallazgos_nuevos"))

    return {
        "tipo":               "resumen_agregado",
        "fuente":             "fase2_relevancia_alta.json",
        "fecha_generacion":   FECHA,
        "total_articulos":    n,
        "rango_temporal":     f"{min(years)}-{max(years)}" if years else "N/A",
        "estadisticas": {
            "con_metodo":              con_metodo,
            "con_metodo_pct":          round(100 * con_metodo / n, 1),
            "con_intencion":           con_intencion,
            "con_intencion_pct":       round(100 * con_intencion / n, 1),
            "relevancia_promedio":     round(sum(relevs) / n, 2),
            "relevancia_alta_n":       alta_rel,
            "relevancia_alta_pct":     round(100 * alta_rel / n, 1),
            "relevancia_media_n":      media_rel,
            "relevancia_media_pct":    round(100 * media_rel / n, 1),
            "relevancia_baja_n":       baja_rel,
            "relevancia_baja_pct":     round(100 * baja_rel / n, 1),
            "con_hallazgos_nuevos":    con_hall,
            "total_hallazgos_nuevos":  total_hall,
            "promedio_hallazgos_por_articulo": round(total_hall / n, 1),
        },
    }


def tabla5_detecciones_agregadas(data, include_hallazgos=False):
    articulos = data["articulos"]
    patrones  = defaultdict(list)

    for art in articulos:
        ref        = make_art_ref(art, include_hallazgos)
        vp         = art["clasificacion"]["variables_principales"]
        metodos    = tuple(sorted(vp.get("metodos_especifico") or []))
        intenciones = tuple(sorted(vp.get("intenciones") or []))
        patrones[(metodos, intenciones)].append(ref)

    top = sorted(patrones.items(), key=lambda x: len(x[1]), reverse=True)[:25]

    return {
        "tipo":                   "detecciones_agregadas",
        "fuente":                 "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos": include_hallazgos,
        "patrones_frecuentes": [
            {
                "metodos":           [get_label(m) for m in ms] if ms else ["Sin método"],
                "intenciones":       [get_label(i) for i in is_] if is_ else ["Sin intención"],
                "cantidad_articulos": len(arts),
                "porcentaje":        round(100 * len(arts) / len(articulos), 1),
                "articulos":         arts,
            }
            for (ms, is_), arts in top
        ],
    }


def tabla6_clusters_metodo(data, include_hallazgos=False):
    articulos       = data["articulos"]
    metodo_a_cluster = {m: cid for cid, _, ms in CLUSTERS_METODO for m in ms}

    clusters = {
        cid: {"nombre": nombre, "metodos_lista": ms, "articulos": [],
              "intenciones": Counter(), "anos": Counter()}
        for cid, nombre, ms in CLUSTERS_METODO
    }

    for art in articulos:
        ref  = make_art_ref(art, include_hallazgos)
        vp   = art["clasificacion"]["variables_principales"]
        metodos = vp.get("metodos_especifico") or []

        asignado = set()
        for m in metodos:
            cid = metodo_a_cluster.get(m)
            if cid:
                clusters[cid]["articulos"].append(ref)
                clusters[cid]["intenciones"].update(vp.get("intenciones") or [])
                if art.get("year"):
                    clusters[cid]["anos"][art["year"]] += 1
                asignado.add(cid)

    result_clusters = []
    for cid, nombre, ms in CLUSTERS_METODO:
        c = clusters[cid]
        n = len(c["articulos"])
        if n == 0:
            continue
        anos = c["anos"]
        result_clusters.append({
            "cluster_id":           cid,
            "nombre":               nombre,
            "metodos_incluidos":    [get_label(m) for m in c["metodos_lista"]],
            "cantidad_articulos":   n,
            "porcentaje":           round(100 * n / len(articulos), 1),
            "intenciones_principales": [
                {"nombre": get_label(i), "cantidad": c["intenciones"][i]}
                for i, _ in c["intenciones"].most_common(5)
            ],
            "anos_rango":           f"{min(anos.keys())}-{max(anos.keys())}" if anos else "N/A",
            "articulos_representativos": sorted(
                c["articulos"], key=lambda x: x["relevancia"], reverse=True
            )[:5],
            "todos_articulos":      c["articulos"],
        })

    return {
        "tipo":                   "clusters_metodo",
        "fuente":                 "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos": include_hallazgos,
        "clusters":               result_clusters,
    }


def tabla7_clusters_intencion(data, include_hallazgos=False):
    articulos = data["articulos"]
    buckets   = defaultdict(list)
    stats     = defaultdict(lambda: {"metodos": Counter(), "anos": Counter()})

    for art in articulos:
        ref  = make_art_ref(art, include_hallazgos)
        vp   = art["clasificacion"]["variables_principales"]
        ints = vp.get("intenciones") or ["Sin_Intencion"]

        for i in ints:
            buckets[i].append(ref)
            stats[i]["metodos"].update(vp.get("metodos_especifico") or [])
            if art.get("year"):
                stats[i]["anos"][art["year"]] += 1

    orden = INTENCIONES_ORDEN + [k for k in buckets if k not in INTENCIONES_ORDEN]

    result_clusters = []
    for intencion in orden:
        if intencion not in buckets:
            continue
        arts = buckets[intencion]
        n    = len(arts)
        anos = stats[intencion]["anos"]
        result_clusters.append({
            "cluster_id":      f"CL_{intencion}",
            "intencion":       intencion,
            "nombre":          get_label(intencion),
            "cantidad_articulos": n,
            "porcentaje":      round(100 * n / len(articulos), 1),
            "metodos_principales": [
                {"nombre": get_label(m), "cantidad": stats[intencion]["metodos"][m]}
                for m, _ in stats[intencion]["metodos"].most_common(5)
            ],
            "anos_rango":      f"{min(anos.keys())}-{max(anos.keys())}" if anos else "N/A",
            "articulos_representativos": sorted(arts, key=lambda x: x["relevancia"], reverse=True)[:5],
            "todos_articulos": arts,
        })

    return {
        "tipo":                   "clusters_intencion",
        "fuente":                 "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos": include_hallazgos,
        "clusters":               result_clusters,
    }


def tabla8_indice_referencias(data, include_hallazgos=False):
    articulos = data["articulos"]
    mapeo     = []

    for art in articulos:
        ref  = make_art_ref(art, include_hallazgos)
        vp   = art["clasificacion"]["variables_principales"]
        metodos    = vp.get("metodos_especifico") or []
        intenciones = vp.get("intenciones") or []

        cluster_metodo = "CL_SinCluster"
        for cid, _, ms in CLUSTERS_METODO:
            if any(m in ms for m in metodos):
                cluster_metodo = cid
                break

        cluster_intencion = f"CL_{intenciones[0]}" if intenciones else "CL_SinIntencion"

        mapeo.append({
            **ref,
            "metodos":            [get_label(m) for m in metodos],
            "intenciones":        [get_label(i) for i in intenciones],
            "cluster_metodo":     cluster_metodo,
            "cluster_intencion":  cluster_intencion,
        })

    mapeo.sort(key=lambda x: x["relevancia"], reverse=True)

    return {
        "tipo":                   "indice_referencias",
        "fuente":                 "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos": include_hallazgos,
        "total_articulos":        len(articulos),
        "mapeo":                  mapeo,
    }


def tabla9_caracteristicas(data, include_hallazgos=False):
    articulos      = data["articulos"]
    feature_arts   = defaultdict(list)
    metodol_count  = Counter()

    for art in articulos:
        ref  = make_art_ref(art, include_hallazgos)
        vp   = art["clasificacion"]["variables_principales"]
        va   = art["clasificacion"]["variables_adicionales"]
        metodos = vp.get("metodos_especifico") or []

        seen = set()
        for m in metodos:
            feat = CARACTERISTICAS_MAP.get(m)
            if feat and feat not in seen:
                feature_arts[feat].append(ref)
                seen.add(feat)

        for met in (va.get("metodologica") or []):
            if met:
                metodol_count[met] += 1

    caracteristicas = sorted([
        {
            "nombre":           feat,
            "cantidad_articulos": len(arts),
            "porcentaje":       round(100 * len(arts) / len(articulos), 1),
            "articulos":        sorted(arts, key=lambda x: x["relevancia"], reverse=True),
        }
        for feat, arts in feature_arts.items()
    ], key=lambda x: x["cantidad_articulos"], reverse=True)

    tecnicas_top20 = [
        {"tecnica": t, "frecuencia": c}
        for t, c in metodol_count.most_common(20)
    ]

    return {
        "tipo":                     "caracteristicas_linguisticas",
        "fuente":                   "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos":  include_hallazgos,
        "caracteristicas":          caracteristicas,
        "tecnicas_metodologicas_top20": tecnicas_top20,
    }


def tabla10_plataformas(data, include_hallazgos=False):
    articulos  = data["articulos"]
    plat_arts  = defaultdict(list)
    plat_stats = defaultdict(lambda: {"metodos": Counter(), "intenciones": Counter()})

    for art in articulos:
        ref  = make_art_ref(art, include_hallazgos)
        vp   = art["clasificacion"]["variables_principales"]
        va   = art["clasificacion"]["variables_adicionales"]
        plats = va.get("plataforma") or ["Sin_Plataforma"]

        for p in plats:
            plat_arts[p].append(ref)
            plat_stats[p]["metodos"].update(vp.get("metodos_especifico") or [])
            plat_stats[p]["intenciones"].update(vp.get("intenciones") or [])

    plataformas_result = sorted([
        {
            "codigo":          p,
            "plataforma":      get_label(p),
            "cantidad_articulos": len(arts),
            "porcentaje":      round(100 * len(arts) / len(articulos), 1),
            "metodos_principales": [
                {"nombre": get_label(m), "cantidad": plat_stats[p]["metodos"][m]}
                for m, _ in plat_stats[p]["metodos"].most_common(5)
            ],
            "intenciones_principales": [
                {"nombre": get_label(i), "cantidad": plat_stats[p]["intenciones"][i]}
                for i, _ in plat_stats[p]["intenciones"].most_common(5)
            ],
            "articulos": sorted(arts, key=lambda x: x["relevancia"], reverse=True),
        }
        for p, arts in plat_arts.items()
    ], key=lambda x: x["cantidad_articulos"], reverse=True)

    return {
        "tipo":                   "plataformas",
        "fuente":                 "fase2_relevancia_alta.json",
        "con_hallazgos_embebidos": include_hallazgos,
        "plataformas":            plataformas_result,
    }


def tabla11_limitaciones(data):
    articulos = data["articulos"]
    n         = len(articulos)

    def art_ref(a):
        return {
            "id":         a["id"],
            "bibtex_key": make_bibtex_key(a),
            "titulo":     a["titulo"],
            "year":       a.get("year"),
            "relevancia": a.get("relevancia_general", 0),
        }

    kw_lim = ["limitacion", "limitaci", "no puede", "no detecta",
               "dificultad", "sesgo", "bias", "gap", "carencia", "no resuelto"]

    lim1 = [a for a in articulos
             if len(a["clasificacion"]["variables_principales"].get("intenciones") or []) >= 2
             and len(a["clasificacion"]["variables_principales"].get("metodos_especifico") or []) == 1]

    lim2 = [a for a in articulos
             if not (a["clasificacion"]["variables_principales"].get("intenciones"))]

    lim3 = [a for a in articulos
             if (a["clasificacion"]["variables_adicionales"].get("linguistica") or []) == ["L1_English"]]

    lim4 = [a for a in articulos
             if not a["clasificacion"]["variables_adicionales"].get("plataforma")
             or set(a["clasificacion"]["variables_adicionales"]["plataforma"]).issubset({"P11_General", "P10_Multiple"})]

    lim5 = [a for a in articulos
             if any(any(kw in h.lower() for kw in kw_lim)
                    for h in (a.get("hallazgos_nuevos") or []))]

    limitaciones = [
        {
            "id":          "LIM1",
            "nombre":      "Granularidad sin soporte metodológico múltiple",
            "descripcion": "Artículos que detectan ≥2 intenciones pero emplean un único método — la granularidad no está respaldada por diversidad metodológica",
            "cantidad":    len(lim1),
            "porcentaje":  round(100 * len(lim1) / n, 1),
            "impacto":     "Alto",
            "rq":          "RQ2",
            "articulos_evidencia": [art_ref(a) for a in sorted(lim1, key=lambda x: x.get("relevancia_general", 0), reverse=True)],
        },
        {
            "id":          "LIM2",
            "nombre":      "Alta relevancia sin clasificación de intención",
            "descripcion": "Artículos que superan el umbral de relevancia pero no asignan ninguna intención comunicativa",
            "cantidad":    len(lim2),
            "porcentaje":  round(100 * len(lim2) / n, 1),
            "impacto":     "Alto",
            "rq":          "Pregunta Principal",
            "articulos_evidencia": [art_ref(a) for a in lim2],
        },
        {
            "id":          "LIM3",
            "nombre":      "Sesgo monolingüe (solo inglés)",
            "descripcion": "Artículos exclusivamente en inglés sin transferencia a otros idiomas — limita generalización de los métodos",
            "cantidad":    len(lim3),
            "porcentaje":  round(100 * len(lim3) / n, 1),
            "impacto":     "Medio-Alto",
            "rq":          "RQ3",
            "articulos_evidencia": [art_ref(a) for a in sorted(lim3, key=lambda x: x.get("relevancia_general", 0), reverse=True)],
        },
        {
            "id":          "LIM4",
            "nombre":      "Falta de especificidad de plataforma",
            "descripcion": "Artículos sin plataforma específica o con clasificación genérica — dificulta la aplicabilidad contextual",
            "cantidad":    len(lim4),
            "porcentaje":  round(100 * len(lim4) / n, 1),
            "impacto":     "Medio",
            "rq":          "RQ1",
            "articulos_evidencia": [art_ref(a) for a in sorted(lim4, key=lambda x: x.get("relevancia_general", 0), reverse=True)[:20]],
        },
        {
            "id":          "LIM5",
            "nombre":      "Limitaciones explícitas reportadas en los propios hallazgos",
            "descripcion": "Artículos cuyos hallazgos_nuevos mencionan limitaciones, sesgos o gaps — evidencia directa extraída de los PDFs",
            "cantidad":    len(lim5),
            "porcentaje":  round(100 * len(lim5) / n, 1),
            "impacto":     "Alto",
            "rq":          "Pregunta Principal",
            "articulos_evidencia": [art_ref(a) for a in sorted(lim5, key=lambda x: x.get("relevancia_general", 0), reverse=True)],
        },
    ]

    return {
        "tipo":             "limitaciones_documentadas",
        "fuente":           "fase2_relevancia_alta.json",
        "fecha_generacion": FECHA,
        "total_articulos":  n,
        "limitaciones":     limitaciones,
    }


def tabla12_hallazgos_nuevos(data):
    articulos = data["articulos"]

    todos = []
    for art in articulos:
        ref = make_art_ref(art, False)
        for h in (art.get("hallazgos_nuevos") or []):
            todos.append({"hallazgo": h, "articulo": ref})

    usados = set()
    temas_resultado = []

    for tema in TEMAS_HALLAZGOS:
        kws      = tema["keywords"]
        matching = []
        for idx, entry in enumerate(todos):
            if idx in usados:
                continue
            if any(kw in entry["hallazgo"].lower() for kw in kws):
                matching.append(entry)
                usados.add(idx)

        arts_unicos = {}
        for entry in matching:
            aid = entry["articulo"]["id"]
            if aid not in arts_unicos:
                arts_unicos[aid] = {**entry["articulo"], "hallazgos_tema": []}
            arts_unicos[aid]["hallazgos_tema"].append(entry["hallazgo"])

        temas_resultado.append({
            "tema_id":          tema["id"],
            "nombre":           tema["nombre"],
            "descripcion":      tema["descripcion"],
            "rq_asociada":      tema["rq"],
            "total_hallazgos":  len(matching),
            "total_articulos":  len(arts_unicos),
            "hallazgos":        matching,
            "articulos_con_hallazgos": sorted(
                list(arts_unicos.values()),
                key=lambda x: x["relevancia"], reverse=True,
            ),
        })

    no_clasif = [e for idx, e in enumerate(todos) if idx not in usados]

    return {
        "tipo":                  "hallazgos_nuevos_tematicos",
        "fuente":                "fase2_relevancia_alta.json",
        "fecha_generacion":      FECHA,
        "total_hallazgos":       len(todos),
        "total_clasificados":    len(usados),
        "total_no_clasificados": len(no_clasif),
        "temas":                 temas_resultado,
        "hallazgos_no_clasificados": no_clasif,
    }


def tabla13_datasets_referencias(data):
    articulos = data["articulos"]
    ds_map    = defaultdict(lambda: {"referencias": [], "urls": [], "articulos": []})

    for art in articulos:
        ref = make_art_ref(art, False)
        vp  = art["clasificacion"]["variables_principales"]

        for ds in (vp.get("dataset_info") or []):
            nombre = (ds.get("nombre") or "").strip()
            if not nombre:
                continue
            nombre_norm = re.sub(r"\s*\(.*?\)", "", nombre).strip()
            entry = ds_map[nombre_norm]
            ref_txt = ds.get("referencia")
            if ref_txt and ref_txt not in entry["referencias"]:
                entry["referencias"].append(ref_txt)
            url = ds.get("url")
            if url and url not in entry["urls"]:
                entry["urls"].append(url)
            if not any(a["id"] == ref["id"] for a in entry["articulos"]):
                entry["articulos"].append(ref)

        for nombre in (vp.get("dataset") or []):
            nombre = nombre.strip()
            if not nombre or nombre in ds_map:
                continue
            entry = ds_map[nombre]
            if not any(a["id"] == ref["id"] for a in entry["articulos"]):
                entry["articulos"].append(ref)

    datasets = sorted([
        {
            "nombre":               nombre,
            "cantidad_articulos":   len(info["articulos"]),
            "porcentaje":           round(100 * len(info["articulos"]) / len(articulos), 1),
            "referencias_completas": info["referencias"],
            "urls":                 [u for u in info["urls"] if u],
            "articulos":            sorted(info["articulos"], key=lambda x: x["relevancia"], reverse=True),
        }
        for nombre, info in ds_map.items()
    ], key=lambda x: x["cantidad_articulos"], reverse=True)

    return {
        "tipo":             "datasets_referencias",
        "fuente":           "fase2_relevancia_alta.json",
        "fecha_generacion": FECHA,
        "total_datasets":   len(datasets),
        "total_articulos":  len(articulos),
        "datasets":         datasets,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Leyendo fase2_relevancia_alta.json...")
    data = load_data()
    n    = len(data["articulos"])
    print(f"  {n} artículos cargados")
    print(f"  {data['metadata']['descripcion']}")
    print()

    # Tablas con versión estándar + _h
    tablas_dobles = [
        ("01_distribuciones_agregadas",   tabla1_distribuciones),
        ("02_cruzada_metodo_intencion",   tabla2_cruzada),
        ("03_evolucion_temporal",         tabla3_temporal),
        ("05_detecciones_agregadas",      tabla5_detecciones_agregadas),
        ("06_clusters_metodo",            tabla6_clusters_metodo),
        ("07_clusters_intencion",         tabla7_clusters_intencion),
        ("08_indice_referencias",         tabla8_indice_referencias),
        ("09_caracteristicas_linguisticas", tabla9_caracteristicas),
        ("10_plataformas",                tabla10_plataformas),
    ]

    for nombre_base, func in tablas_dobles:
        print(f"  {nombre_base}.json ...", end="", flush=True)
        save_json(func(data, include_hallazgos=False),
                  os.path.join(OUTPUT_DIR, f"{nombre_base}.json"))
        print(" OK")

        print(f"  {nombre_base}_h.json ...", end="", flush=True)
        save_json(func(data, include_hallazgos=True),
                  os.path.join(OUTPUT_DIR, f"{nombre_base}_h.json"))
        print(" OK")

    # Tablas de versión única
    tablas_simples = [
        ("04_resumen_agregado.json",        tabla4_resumen_agregado),
        ("11_limitaciones_documentadas.json", tabla11_limitaciones),
        ("12_hallazgos_nuevos.json",         tabla12_hallazgos_nuevos),
        ("13_datasets_referencias.json",     tabla13_datasets_referencias),
    ]

    for filename, func in tablas_simples:
        print(f"  {filename} ...", end="", flush=True)
        save_json(func(data), os.path.join(OUTPUT_DIR, filename))
        print(" OK")

    total = len(tablas_dobles) * 2 + len(tablas_simples)
    print(f"\n[OK] {total} archivos generados en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
