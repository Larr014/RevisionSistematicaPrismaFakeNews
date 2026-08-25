#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae hallazgos TH9 usando la lógica ORIGINAL de generar_tablas_fase2.py
y subcategoriza en:
  TH9a: Variantes algorítmicas y métricas de rendimiento
  TH9b: Hallazgos de contexto disciplinar no computacional
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

INPUT   = r"C:\Users\Luis Rojas\.openclaw\workspace\fase2_relevancia_alta.json"
OUTPUT  = r"C:\Users\Luis Rojas\.openclaw\workspace\paper\th9_subcategorias.json"

# ── Keywords ORIGINALES de generar_tablas_fase2.py (sin modificar) ─────────
TEMAS_HALLAZGOS = [
    {
        "id": "TH1",
        "keywords": ["clasificador", "algoritmo", "xgboost", "adaboost", "lightgbm", "catboost",
                     "deberta", "roberta", "llama", "gpt-4", "mistral", "chatgpt",
                     "modelo", "arquitectura", "red neur"],
    },
    {
        "id": "TH2",
        "keywords": ["intencion", "intenci", "categoria", "tipo de", "hoax", "propaganda",
                     "satira", "satire", "engano", "esquema", "taxonom"],
    },
    {
        "id": "TH3",
        "keywords": ["lexic", "sintact", "estilometr", "stylom", "readability", "flesch",
                     "gunning", "yule", "mtld", "n-gram", "tf-idf", "tfidf",
                     "embedding", "feature", "caracteristic", "legibilid"],
    },
    {
        "id": "TH4",
        "keywords": ["dataset", "corpus", "benchmark", "evaluacion", "evalua",
                     "metrica", "medida", "conjunto de dato", "datos etiquetados"],
    },
    {
        "id": "TH5",
        "keywords": ["limitacion", "limitaci", "no puede", "no detecta", "dificultad",
                     "sesgo", "bias", "gap", "carencia", "no resuelto"],
    },
    {
        "id": "TH6",
        "keywords": ["grafo", "graph", "multimodal", "cross-lingual", "transfer",
                     "few-shot", "zero-shot", "inductiv", "heterog", "meta-path",
                     "knowledge graph", "propagacion", "propagaci", "cascada"],
    },
    {
        "id": "TH7",
        "keywords": ["multilingu", "multilingue", "cross-lingual", "idioma", "arabic",
                     "chinese", "spanish", "hindi", "urdu", "portuguese", "lengua"],
    },
    {
        "id": "TH8",
        "keywords": ["propagacion", "propagaci", "difusion", "difusi", "temporal",
                     "timeline", "patron", "comportamiento", "bot", "coordinado",
                     "red social", "usuario"],
    },
]

# ── TH9a: Variantes metodológicas con terminología inglesa ───────────────────
# Métodos, arquitecturas y métricas capturados en texto completo pero fuera
# del vocabulario léxico español de TH1-TH8.
TH9A_KEYWORDS = [
    # Arquitecturas DL / ML en inglés no cubiertas por TH1
    "cnn", "convolutional neural", "gru", "lstm", "bilstm", "rnn", "recurrent",
    "bert", "albert", "electra", "xlnet", "t5", "gpt-2", "gpt-3",
    "svm", "support vector", "random forest", "logistic regression",
    "naive bayes", "decision tree", "knn", "k-nearest",
    "mlp", "multi-layer perceptron", "lasso", "ridge regression",
    "elastic net", "gradient boosting", "xgboost", "catboost",
    "attention mechanism", "self-attention", "fine-tuning", "fine-tune",
    "transformer", "encoder", "decoder", "autoencoder",
    "dual-bert", "co-attention", "capsule network",
    # Topic models y clustering
    "lda", "lsi", "latent dirichlet", "topic model",
    "cluster", "k-means", "dbscan", "hierarchical clustering",
    # Fusión y ensamblado
    "score fusion", "ensemble", "stacking", "weighted fusion",
    "mean-pooling", "max-pooling", "sliding window", "ventana deslizante",
    # Causalidad y estadística avanzada
    "causal", "structural causal", "front-door", "back-door",
    "binomial", "negative binomial", "zero-inflated", "poisson",
    "odds ratio", "homofilia", "homophily",
    "chi-square", "t-test", "anova", "pearson", "spearman",
    "regresion lineal", "regresion logistica", "linear regression",
    "bootstrapping", "cross-validation", "k-fold", "ablation",
    # XAI / Interpretabilidad
    "shap", "lime", "xai", "explainab", "interpretab", "explicab",
    "gradcam", "grad-cam", "feature importance", "saliency map",
    "attention visualization",
    # Adversarial y robustez
    "adversarial", "adversario", "ataque adversarial", "perturbacion",
    "robustez", "robustness", "noisy tuning",
    # Modelos generativos y multimodales avanzados
    "vae", "variational autoencoder", "autoencoder", "variational",
    "generative adversarial", "gan", "diffusion model",
    "contrastive learning", "contrastive loss",
    "vision transformer", "vit ", "clip model", "contrastive language-image",
    "codificador dual", "dual encoder",
    "knowledge distillation", "destilacion de conocimiento",
    "fusion de caracteristicas", "feature fusion",
    "representacion multimodal", "multimodal representation",
    # Métricas de rendimiento
    "accuracy", "f1-score", "f1 score", "recall", "auc", "roc curve",
    "binary classification", "multi-label", "overfit", "underfit",
    "regularizacion", "regularization", "hiperparametro", "hyperparameter",
    "loss function", "perdida", "cross-entropy", "bce",
    "dropout", "batch normalization", "learning rate", "epoch",
    "prototype vector", "role prototype", "cosine similarity",
    # Técnicas de representación y recuperación
    "sentence embedding", "word embedding", "vector representation",
    "dense retrieval", "sparse retrieval", "bm25",
    "reranking", "reranker", "semantic search",
    "pooling", "layer normalization", "residual connection",
    # Implementaciones y optimización
    "chrome extension", "browser extension", "api integration",
    "pipeline de clasificacion", "inference pipeline",
    "throughput", "latency", "computational efficiency",
    "gradient", "backpropagation", "optimizer", "adam", "sgd"
]

# ── TH9b: Hallazgos de contexto disciplinar no computacional ─────────────────
TH9B_KEYWORDS = [
    # Psicología, cognición y teorías conductuales
    "psicolog", "psychology", "cognitive", "cognitiv",
    "creencia", "belief", "actitud", "attitude",
    "teoria de la persuasion", "persuasion theory", "yale attitude",
    "theory of planned behavior", "cognitive reflection test",
    "abc model", "agency-belief", "social cognitive",
    "motivacion para compartir", "sharing motivation",
    # Metodología cualitativa y encuestas
    "cualitativ", "qualitative", "entrevista", "interview",
    "encuesta", "survey", "cuestionario", "questionnaire",
    "focus group", "etnograf", "ethnograph",
    "stepwise regression", "regresion stepwise",
    # Confianza, percepción y comportamiento social
    "confianza en", "trust in", "distrust", "desconfianza",
    "percepcion de", "percepcion publica", "public perception",
    "vulnerabilidad a", "susceptibilidad",
    "intencion de compartir", "sharing intention",
    "confianza en gobiernos", "trust in government",
    # Bibliometría y revisiones
    "bibliometr", "meta-analis", "meta-analysis",
    "scoping review", "mapping review",
    # Comunicación, salud, educación
    "media literar", "alfabetizacion mediatica", "pensamiento critico",
    "critical thinking", "educacion mediatica",
    "fact-checker humano", "verificador", "periodismo", "journalism",
    "salud publica", "public health", "health communication",
    "politica publica", "public policy",
    # Optimización de despliegue (no ML)
    "despliegue estocastico", "stochastic deployment",
    "transicion de fase", "phase transition",
    "fact-checker deployment", "timing de despliegue"
]

# ── Cargar datos ─────────────────────────────────────────────────────────────
with open(INPUT, encoding='utf-8') as f:
    data = json.load(f)

arts = data.get('articulos', [])

# ── Reproducir lógica ORIGINAL de tabla12_hallazgos_nuevos ───────────────────
todos = []
for art in arts:
    for h in (art.get("hallazgos_nuevos") or []):
        todos.append({"hallazgo": h, "articulo_id": art["id"], "titulo": art.get("titulo","")})

usados = set()
th_counts = {}

for tema in TEMAS_HALLAZGOS:
    kws = tema["keywords"]
    matching = []
    for idx, entry in enumerate(todos):
        if idx in usados:
            continue
        if any(kw in entry["hallazgo"].lower() for kw in kws):
            matching.append(entry)
            usados.add(idx)
    th_counts[tema["id"]] = len(matching)

# TH9 = los no clasificados por TH1-TH8
th9_todos = [e for idx, e in enumerate(todos) if idx not in usados]

# ── Subcategorizar TH9 ───────────────────────────────────────────────────────
# TH9a: métodos/técnicas computacionales con terminología inglesa
# TH9b: contexto disciplinar no computacional
# TH9c: residual genuino (observaciones, datos sin categoría clara)
th9a, th9b, th9c = [], [], []

for entry in th9_todos:
    h_low = entry["hallazgo"].lower()
    es_a = any(kw in h_low for kw in TH9A_KEYWORDS)
    es_b = any(kw in h_low for kw in TH9B_KEYWORDS)

    if es_a and not es_b:
        entry["subcategoria"] = "TH9a"
        th9a.append(entry)
    elif es_b and not es_a:
        entry["subcategoria"] = "TH9b"
        th9b.append(entry)
    elif es_a and es_b:
        # Prioridad a metodológico sobre disciplinar
        entry["subcategoria"] = "TH9a"
        th9a.append(entry)
    else:
        entry["subcategoria"] = "TH9c"
        th9c.append(entry)

# ── Reporte ──────────────────────────────────────────────────────────────────
print("=" * 65)
print("REPRODUCCIÓN EXACTA DE CLASIFICACIÓN TH (lógica generar_tablas_fase2)")
print("=" * 65)
print(f"\nTotal hallazgos: {len(todos)}")
print(f"\nDistribución TH1-TH8 (keywords originales):")
for th, cnt in th_counts.items():
    print(f"  {th}: {cnt:4d}")
print(f"  Subtotal TH1-TH8: {sum(th_counts.values())}")
print(f"\nTH9 total:                                  {len(th9_todos)}")
print(f"  TH9a (Métodos/técnicas en inglés):       {len(th9a)}")
print(f"  TH9b (Contexto disciplinar):              {len(th9b)}")
print(f"  TH9c (Residual genuino):                  {len(th9c)}")

print(f"\n--- Muestra TH9a (primeros 8) ---")
for e in th9a[:8]:
    print(f"  [{e['articulo_id']}] {e['hallazgo'][:110]}")

print(f"\n--- Muestra TH9b (primeros 8) ---")
for e in th9b[:8]:
    print(f"  [{e['articulo_id']}] {e['hallazgo'][:110]}")

print(f"\n--- Muestra TH9c (primeros 8) ---")
for e in th9c[:8]:
    print(f"  [{e['articulo_id']}] {e['hallazgo'][:110]}")


# ── Guardar ──────────────────────────────────────────────────────────────────
output_data = {
    "meta": {
        "descripcion": "Clasificación TH reproducida con lógica original. TH9 subcategorizado inductivamente.",
        "total_hallazgos": len(todos),
        "th1_th8_total": sum(th_counts.values()),
        "th_counts": th_counts,
        "th9_total": len(th9_todos),
        "th9a_metodos_terminologia_inglesa": len(th9a),
        "th9b_contexto_disciplinar": len(th9b),
        "th9c_residual": len(th9c)
    },
    "th9a": th9a,
    "th9b": th9b,
    "th9c": th9c
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\nResultados guardados en: {OUTPUT}")
