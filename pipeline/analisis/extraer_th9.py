#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae hallazgos TH9 de clasificacion_pdfs_completos.json
y los subcategoriza en TH9a y TH9b segun sugerencia del director.

TH9a: Métricas de Desempeño Operativo / Tiempos de Cómputo
TH9b: Técnicas de Curación y Limpieza de Datos
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

INPUT = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_pdfs_completos.json"
OUTPUT = r"C:\Users\Luis Rojas\.openclaw\workspace\paper\th9_subcategorias.json"

# Keywords para identificar TH1-TH8 (basado en descripciones del paper)
TH_KEYWORDS = {
    "TH1": ["xgboost","adaboost","lightgbm","deberta","roberta","llama","gpt-4","gpt4",
             "multimodal","mistral","falcon","gemini","claude","electra","xlm","t5",
             "emergent method","nuevo metodo","new method","novel approach"],
    "TH2": ["taxonom","typolog","ontolog","classification scheme","annotation scheme",
             "hoax","propaganda","satire","satira","esquema","tipologia","framework",
             "categoria","category","label schema","labeling"],
    "TH3": ["mtld","yule","flesch","gunning","coleman","readability","legibilidad",
             "lexical diversity","diversidad lexica","hedging","stylometr","estilometr",
             "syntactic","sintactic","linguistic feature","caracteristica linguistica",
             "pos tag","n-gram","bigram","trigram"],
    "TH4": ["dataset","benchmark","corpus","evaluation protocol","protocolo de evaluacion",
             "train.*test split","cross.validation","ablation","confusion matrix",
             "ground truth","gold standard","annotation","etiquetad"],
    "TH5": ["limitation","limitacion","gap","brecha","future work","trabajo futuro",
             "challenge","desafio","unable","cannot","fail","problema abierto",
             "open problem","weakness","debilidad"],
    "TH6": ["meta.path","hetero","few.shot","zero.shot","transfer learn","cross.domain",
             "inductive","self.supervised","contrastive","knowledge graph","graph neural",
             "attention mechanism","transformer.*novel","arquitectura novedosa"],
    "TH7": ["multilin","arabic","chinese","mandarin","spanish.*model","model.*spanish",
             "cross.lingual","cross.cultural","low.resource","translation","idioma",
             "language transfer"],
    "TH8": ["propagation","propagacion","cascade","diffusion","difusion","retweet",
             "spreading","coordinat","spike","viral","red social.*patron",
             "network.*pattern","bot.*network","coordination"],
}

# Keywords para TH9a y TH9b
TH9A_KEYWORDS = [
    "training time","inference time","computation time","tiempo de entrenamiento",
    "tiempo de inferencia","tiempo de computo","computational cost","gpu","memory usage",
    "parameters","parametros del modelo","model size","throughput","latency","latencia",
    "flops","epoch.*time","speed","velocidad","resource","recurso","overhead",
    "efficiency","eficiencia computacional","hardware","cuda","vram","ram usage"
]

TH9B_KEYWORDS = [
    "preprocessing","preprocesamiento","data cleaning","limpieza de datos",
    "data augmentation","augmentation","noise removal","eliminacion de ruido",
    "imbalanced","desbalanceado","oversampling","undersampling","smote",
    "data quality","calidad de datos","duplicate","deduplication","normalization",
    "normalizacion","tokenization","tokenizacion","stopword","stemming",
    "lemmatization","lematizacion","curation","curacion","label noise",
    "mislabeled","pipeline.*preprocess","cleaning pipeline"
]

def match_any(text, keywords):
    t = text.lower()
    import re
    for kw in keywords:
        if re.search(kw.lower(), t):
            return True
    return False

with open(INPUT, encoding='utf-8') as f:
    data = json.load(f)

arts = data.get('articulos', [])
relevantes = [a for a in arts if a.get('relevancia_general', 0) >= 0.4]

total_hallazgos = 0
th_counts = {k: 0 for k in TH_KEYWORDS}
th9_hallazgos = []
th9a = []
th9b = []
th9_ninguna = []

for art in relevantes:
    for h in art.get('hallazgos_nuevos', []):
        total_hallazgos += 1
        # Ver si cae en TH1-TH8
        matched_th = False
        for th, kws in TH_KEYWORDS.items():
            if match_any(h, kws):
                th_counts[th] += 1
                matched_th = True
                break  # Solo el primer TH que matchea

        if not matched_th:
            # Es TH9 — subclasificar
            entry = {"articulo": art.get("id"), "hallazgo": h}
            th9_hallazgos.append(entry)
            is_a = match_any(h, TH9A_KEYWORDS)
            is_b = match_any(h, TH9B_KEYWORDS)
            if is_a and not is_b:
                entry["subcategoria"] = "TH9a"
                th9a.append(entry)
            elif is_b and not is_a:
                entry["subcategoria"] = "TH9b"
                th9b.append(entry)
            elif is_a and is_b:
                entry["subcategoria"] = "TH9a"  # Prioridad a desempeño
                th9a.append(entry)
            else:
                entry["subcategoria"] = "TH9_otro"
                th9_ninguna.append(entry)

print("=" * 60)
print("ANÁLISIS DE HALLAZGOS TH9")
print("=" * 60)
print(f"\nTotal hallazgos (relevancia >= 0.4): {total_hallazgos}")
print(f"\nDistribución TH1-TH8:")
for th, cnt in th_counts.items():
    print(f"  {th}: {cnt}")
print(f"  Subtotal TH1-TH8: {sum(th_counts.values())}")
print(f"\nTH9 total: {len(th9_hallazgos)}")
print(f"  TH9a (Desempeño/Tiempos): {len(th9a)}")
print(f"  TH9b (Curación/Limpieza): {len(th9b)}")
print(f"  TH9_otro (sin subcategoría clara): {len(th9_ninguna)}")

print(f"\n--- Muestra TH9a (primeros 5) ---")
for e in th9a[:5]:
    print(f"  [{e['articulo']}] {e['hallazgo'][:110]}")

print(f"\n--- Muestra TH9b (primeros 5) ---")
for e in th9b[:5]:
    print(f"  [{e['articulo']}] {e['hallazgo'][:110]}")

print(f"\n--- Muestra TH9_otro (primeros 5) ---")
for e in th9_ninguna[:5]:
    print(f"  [{e['articulo']}] {e['hallazgo'][:110]}")

# Guardar resultado
output_data = {
    "meta": {
        "total_hallazgos": total_hallazgos,
        "th1_th8": sum(th_counts.values()),
        "th9_total": len(th9_hallazgos),
        "th9a_desempeno": len(th9a),
        "th9b_curacion": len(th9b),
        "th9_otro": len(th9_ninguna)
    },
    "th_counts": th_counts,
    "th9a": th9a,
    "th9b": th9b,
    "th9_otro": th9_ninguna
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\nResultados guardados en: {OUTPUT}")
