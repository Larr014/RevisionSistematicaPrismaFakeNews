#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clasificacion semantica de articulos usando Claude API
Entrada: AllDeduplicated.ris
Salida: clasificacion_articulos.json
"""

import json
import os
import time
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import anthropic

RIS_PATH = r"C:\Users\Luis Rojas\OneDrive\Doc\Doctorado\tarea estado del arte\OSF\Registros\Etapa 3\AllDeduplicated.ris"
OUTPUT_PATH = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_articulos.json"
CHECKPOINT_PATH = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_checkpoint.json"

SYSTEM_PROMPT = """Eres un asistente especializado en analisis de literatura cientifica sobre procesamiento del lenguaje natural e intenciones comunicativas en medios digitales.

Tu tarea es clasificar articulos academicos segun las siguientes variables. Analiza el titulo y abstract y devuelve SOLO un JSON valido con esta estructura exacta:

{
  "metodos_especifico": [],
  "metodos_general": [],
  "metricas": [],
  "intenciones": [],
  "dataset": [],
  "temporal": null,
  "plataforma": [],
  "linguistica": [],
  "relevancia": 0.0
}

ETIQUETAS VALIDAS (usa solo estas):

metodos_especifico:
- M1_BERT: si usa BERT, RoBERTa, DistilBERT, ALBERT o variantes
- M2_GPT: si usa GPT, ChatGPT, LLM, large language model
- M3_Transformers: si usa transformers, attention mechanism, encoder-decoder (no BERT ni GPT especificamente)
- M4_CNN: si usa CNN, convolutional neural network
- M5_RNN_LSTM: si usa LSTM, RNN, GRU, recurrent
- M6_SVM: si usa SVM, support vector machine
- M7_NaiveBayes: si usa Naive Bayes, probabilistic classifier
- M8_RandomForest: si usa Random Forest, decision tree, ensemble
- M9_NLP_Traditional: si usa NLP clasico, tokenizacion, TF-IDF, word embeddings, Word2Vec, GloVe sin deep learning
- M10_ManualAnalysis: si usa anotacion manual, analisis humano, coding scheme, content analysis cualitativo

metodos_general (derivado automatico, no dejes vacio si hay metodos_especifico):
- "Deep Learning" para M1-M5
- "Machine Learning" para M6-M8
- "NLP" para M9
- "Manual/Hybrid" para M10

metricas:
- D1_Precision_Recall: menciona precision, recall, F1, F-measure
- D2_AUC_ROC: menciona AUC, ROC curve, area under the curve
- D3_Accuracy: menciona accuracy, exactitud
- D4_Confusion_Matrix: menciona confusion matrix, true/false positives

intenciones (elige las que apliquen semanticamente):
- I1_FakeNews: noticias falsas, desinformacion, misinformation, verificacion de hechos
- I2_Manipulation: manipulacion, engano, deception, clickbait
- I3_Persuasion: persuasion, propaganda, framing
- I4_Clickbait: clickbait, titulos sensacionalistas, engagement bait
- I5_Polarization: polarizacion politica, sesgo, partidismo
- I6_Emotion: analisis de sentimiento, emocion, opinion, stance
- I7_Conspiracy: teorias conspirativas, conspiracion

dataset:
- DS1_Available: dataset publico disponible, open source, github, zenodo
- DS2_Multilingual: dataset multilingue, varios idiomas
- DS3_Large: dataset grande, miles o millones de ejemplos
- DS4_Balanced: menciona balance/desbalance de clases

temporal:
- "T1_Recent" si el articulo menciona datos o contexto de 2020-2025, sino null

plataforma:
- P1_Twitter: Twitter, X, tweets
- P2_Facebook: Facebook, Meta
- P3_News: noticias, periodismo, articulos de prensa

linguistica:
- L1_English: corpus o datos en ingles
- L2_Spanish: corpus o datos en espanol
- L3_Multilingual: datos en multiples idiomas

relevancia (float 0.0-1.0):
- 1.0: articulo directamente sobre metodos para identificar intenciones comunicativas en textos digitales
- 0.7: sobre analisis de contenido digital o NLP aplicado a redes sociales
- 0.4: sobre NLP o ML en general, no especificamente intenciones
- 0.1: tema muy alejado o sin relacion clara

Responde SOLO con el JSON, sin explicaciones ni texto adicional."""


def parse_ris_file(filepath):
    articles = []
    current_article = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith("TY  -"):
                    if current_article:
                        articles.append(current_article)
                    current_article = {}
                elif " - " in line and not line.startswith(" "):
                    key, value = line.split(" - ", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "TI":
                        current_article['title'] = value
                    elif key == "AB":
                        current_article['abstract'] = current_article.get('abstract', '') + ' ' + value
                    elif key == "AU":
                        if 'authors' not in current_article:
                            current_article['authors'] = []
                        current_article['authors'].append(value)
                    elif key == "PY":
                        try:
                            current_article['year'] = int(value)
                        except:
                            pass
                    elif key == "DO":
                        current_article['doi'] = value
                    elif key == "JF":
                        current_article['journal'] = value
        if current_article:
            articles.append(current_article)
    except Exception as e:
        print(f"Error parsing RIS: {e}")
    return articles


def classify_with_claude(client, article):
    title = article.get('title', '')
    abstract = article.get('abstract', '').strip()

    if not title and not abstract:
        return empty_classification()

    user_msg = f"Titulo: {title}\n\nAbstract: {abstract}"

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}]
            )
            raw = response.content[0].text.strip()
            # Limpiar markdown si viene envuelto
            if raw.startswith("```"):
                raw = re.sub(r"```[a-z]*\n?", "", raw).strip("` \n")
            result = json.loads(raw)
            return result
        except json.JSONDecodeError as e:
            print(f"  JSON parse error articulo (intento {attempt+1}): {e}")
            time.sleep(1)
        except Exception as e:
            msg = str(e)
            if "overloaded" in msg or "529" in msg:
                wait = (attempt + 1) * 30
                print(f"  API sobrecargada, esperando {wait}s...")
                time.sleep(wait)
            elif "rate_limit" in msg or "429" in msg:
                wait = (attempt + 1) * 60
                print(f"  Rate limit, esperando {wait}s...")
                time.sleep(wait)
            else:
                print(f"  Error API (intento {attempt+1}): {msg[:80]}")
                time.sleep(5)

    return empty_classification()


def empty_classification():
    return {
        "metodos_especifico": [],
        "metodos_general": [],
        "metricas": [],
        "intenciones": [],
        "dataset": [],
        "temporal": None,
        "plataforma": [],
        "linguistica": [],
        "relevancia": 0.0
    }


def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"articulos": [], "ultimo_procesado": 0}


def save_checkpoint(data):
    with open(CHECKPOINT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no encontrada en variables de entorno")
        return

    client = anthropic.Anthropic(api_key=api_key)

    print("Leyendo archivo RIS...")
    articles = parse_ris_file(RIS_PATH)
    print(f"Cargados {len(articles)} articulos")

    # Cargar checkpoint si existe
    checkpoint = load_checkpoint()
    classified_articles = checkpoint["articulos"]
    start_idx = checkpoint["ultimo_procesado"]

    if start_idx > 0:
        print(f"Retomando desde articulo {start_idx + 1}...")

    total = len(articles)
    stats = defaultdict(int)

    for idx in range(start_idx, total):
        article = articles[idx]
        num = idx + 1

        result = classify_with_claude(client, article)

        record = {
            "id": f"articulo_{num:06d}",
            "titulo": article.get("title", "N/A"),
            "autores": article.get("authors", [])[:3],
            "year": article.get("year"),
            "doi": article.get("doi", "N/A"),
            "abstract": article.get("abstract", "")[:500],
            "clasificacion": {
                "variables_principales": {
                    "metodos_especifico": result.get("metodos_especifico", []),
                    "metodos_general": result.get("metodos_general", []),
                    "metricas": result.get("metricas", []),
                    "intenciones": result.get("intenciones", []),
                    "dataset": result.get("dataset", [])
                },
                "variables_adicionales": {
                    "temporal": result.get("temporal"),
                    "plataforma": result.get("plataforma", []),
                    "linguistica": result.get("linguistica", []),
                    "metodologica": []
                }
            },
            "relevancia_general": result.get("relevancia", 0.0)
        }

        classified_articles.append(record)

        # Estadisticas
        for m in result.get("metodos_especifico", []):
            stats[m] += 1
        for i in result.get("intenciones", []):
            stats[i] += 1

        # Progreso cada 50 articulos
        if num % 50 == 0 or num == total:
            print(f"  [{num}/{total}] {article.get('title', 'sin titulo')[:50]}...")

        # Checkpoint cada 100 articulos
        if num % 100 == 0:
            save_checkpoint({"articulos": classified_articles, "ultimo_procesado": num})
            print(f"  Checkpoint guardado ({num} articulos)")

        # Pausa pequeña para no saturar la API
        time.sleep(0.3)

    print(f"\nClasificacion completada: {total} articulos")

    output = {
        "metadata": {
            "titulo_revision": "Metodos para Identificar Intenciones Comunicativas en Publicaciones Digitales",
            "fecha_generacion": datetime.now().isoformat(),
            "total_articulos": total,
            "articulos_clasificados": len(classified_articles),
            "modelo_usado": "claude-haiku-4-5-20251001"
        },
        "articulos": classified_articles,
        "estadisticas": {
            "distribucion": dict(stats),
            "con_intencion": sum(1 for a in classified_articles if a["clasificacion"]["variables_principales"]["intenciones"]),
            "con_metodo": sum(1 for a in classified_articles if a["clasificacion"]["variables_principales"]["metodos_especifico"]),
            "alta_relevancia": sum(1 for a in classified_articles if a["relevancia_general"] >= 0.7)
        }
    }

    print(f"Guardando JSON en {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Borrar checkpoint al terminar
    if os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)

    print(f"Listo. JSON guardado.")
    print(f"  Con intencion clasificada: {output['estadisticas']['con_intencion']}")
    print(f"  Con metodo identificado:   {output['estadisticas']['con_metodo']}")
    print(f"  Alta relevancia (>=0.7):   {output['estadisticas']['alta_relevancia']}")


if __name__ == "__main__":
    main()
