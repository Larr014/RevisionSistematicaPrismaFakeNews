#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clasificacion semantica via Claude CLI (OAuth - sin API key adicional)
Entrada: AllDeduplicated.ris
Salida: clasificacion_claude.json
"""

import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from datetime import datetime

RIS_PATH = r"C:\Users\Luis Rojas\OneDrive\Doc\Doctorado\tarea estado del arte\OSF\Registros\Etapa 3\AllDeduplicated.ris"
OUTPUT_PATH = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_claude.json"
CHECKPOINT_PATH = r"C:\Users\Luis Rojas\.openclaw\workspace\checkpoint_claude.json"

# Apagar PC al terminar o al agotar cuota
APAGAR_AL_TERMINAR = "--apagar" in sys.argv
APAGAR_DELAY = 120  # segundos antes de apagar

QUOTA_ERRORS = [
    "rate limit", "quota", "overloaded", "too many requests",
    "usage limit", "exceeded", "capacity"
]


def apagar_pc(motivo):
    print(f"\nAPAGANDO en {APAGAR_DELAY}s: {motivo}")
    subprocess.run(
        f'shutdown /s /t {APAGAR_DELAY} /c "{motivo}"',
        shell=True
    )

SYSTEM_PROMPT = """Eres un asistente especializado en analisis de literatura cientifica sobre NLP e intenciones comunicativas digitales.

Clasifica el articulo academico y devuelve SOLO un JSON valido con esta estructura:

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

ETIQUETAS VALIDAS:
metodos_especifico: M1_BERT, M2_GPT, M3_Transformers, M4_CNN, M5_RNN_LSTM, M6_SVM, M7_NaiveBayes, M8_RandomForest, M9_NLP_Traditional, M10_ManualAnalysis
metodos_general (derivar de especifico): "Deep Learning" (M1-M5), "Machine Learning" (M6-M8), "NLP" (M9), "Manual/Hybrid" (M10)
metricas: D1_Precision_Recall, D2_AUC_ROC, D3_Accuracy, D4_Confusion_Matrix
intenciones: I1_FakeNews, I2_Manipulation, I3_Persuasion, I4_Clickbait, I5_Polarization, I6_Emotion, I7_Conspiracy
dataset: DS1_Available, DS2_Multilingual, DS3_Large, DS4_Balanced
temporal: "T1_Recent" si menciona contexto 2020-2025, sino null
plataforma: P1_Twitter, P2_Facebook, P3_News
linguistica: L1_English, L2_Spanish, L3_Multilingual
relevancia: 0.0-1.0 segun que tan directamente el articulo trata metodos para identificar intenciones comunicativas en textos digitales

Responde SOLO con el JSON."""


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


def classify_with_claude_cli(article):
    title = article.get('title', '')
    abstract = article.get('abstract', '').strip()

    if not title and not abstract:
        return empty_classification()

    prompt = f"{SYSTEM_PROMPT}\n\nTitulo: {title}\n\nAbstract: {abstract}"

    for attempt in range(3):
        process = None
        try:
            env = os.environ.copy()
            env['CLAUDECODE'] = ''

            process = subprocess.Popen(
                ['claude', '-p', prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            try:
                stdout, stderr = process.communicate(timeout=60)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                print(f"  Timeout (intento {attempt+1})")
                time.sleep(10)
                continue

            if process.returncode != 0:
                stderr_lower = stderr.lower()
                print(f"  CLI error (intento {attempt+1}): {stderr[:80]}")
                # Detectar cuota agotada
                if any(e in stderr_lower for e in QUOTA_ERRORS):
                    return None  # Señal especial: cuota agotada
                time.sleep(5)
                continue

            raw = stdout.strip()
            if raw.startswith("```"):
                raw = re.sub(r"```[a-z]*\n?", "", raw).strip("` \n")

            return json.loads(raw)

        except json.JSONDecodeError as e:
            print(f"  JSON parse error (intento {attempt+1}): {e}")
            time.sleep(2)
        except Exception as e:
            print(f"  Error (intento {attempt+1}): {str(e)[:80]}")
            time.sleep(5)
        finally:
            if process and process.poll() is None:
                process.kill()
                process.wait()

    return empty_classification()


def load_checkpoint(path):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"articulos": [], "ultimo_procesado": 0}


def save_checkpoint(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def main():
    print("Leyendo archivo RIS...")
    articles = parse_ris_file(RIS_PATH)
    print(f"Cargados {len(articles)} articulos")

    checkpoint = load_checkpoint(CHECKPOINT_PATH)
    classified_articles = checkpoint["articulos"]
    start_idx = checkpoint["ultimo_procesado"]

    if start_idx > 0:
        print(f"Retomando desde articulo {start_idx + 1}...")

    total = len(articles)
    stats = defaultdict(int)

    # Estadisticas de articulos ya procesados
    for a in classified_articles:
        for m in a["clasificacion"]["variables_principales"]["metodos_especifico"]:
            stats[m] += 1
        for i in a["clasificacion"]["variables_principales"]["intenciones"]:
            stats[i] += 1

    inicio = datetime.now()

    for idx in range(start_idx, total):
        article = articles[idx]
        num = idx + 1

        result = classify_with_claude_cli(article)

        # Cuota agotada — guardar checkpoint y apagar si corresponde
        if result is None:
            save_checkpoint(CHECKPOINT_PATH, {"articulos": classified_articles, "ultimo_procesado": idx})
            print(f"Cuota agotada en articulo {num}. Checkpoint guardado.")
            if APAGAR_AL_TERMINAR:
                apagar_pc(f"Cuota Claude agotada en art {num}/{total}")
            return

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

        for m in result.get("metodos_especifico", []):
            stats[m] += 1
        for i in result.get("intenciones", []):
            stats[i] += 1

        # Progreso cada 10 articulos con estimacion de tiempo
        if num % 10 == 0 or num == total:
            elapsed = (datetime.now() - inicio).total_seconds()
            procesados_sesion = num - start_idx
            if procesados_sesion > 0:
                seg_por_art = elapsed / procesados_sesion
                restantes = total - num
                eta_min = int((restantes * seg_por_art) / 60)
                print(f"  [{num}/{total}] ~{seg_por_art:.1f}s/art | ETA: {eta_min} min | {article.get('title', '')[:45]}...")

        # Checkpoint cada 100
        if num % 100 == 0:
            save_checkpoint(CHECKPOINT_PATH, {"articulos": classified_articles, "ultimo_procesado": num})
            print(f"  >> Checkpoint guardado ({num} articulos)")

    print(f"\nClasificacion completada: {total} articulos")

    output = {
        "metadata": {
            "titulo_revision": "Metodos para Identificar Intenciones Comunicativas en Publicaciones Digitales",
            "fecha_generacion": datetime.now().isoformat(),
            "total_articulos": total,
            "articulos_clasificados": len(classified_articles),
            "modelo_usado": "claude-via-cli"
        },
        "articulos": classified_articles,
        "estadisticas": {
            "distribucion": dict(stats),
            "con_intencion": sum(1 for a in classified_articles if a["clasificacion"]["variables_principales"]["intenciones"]),
            "con_metodo": sum(1 for a in classified_articles if a["clasificacion"]["variables_principales"]["metodos_especifico"]),
            "alta_relevancia": sum(1 for a in classified_articles if a["relevancia_general"] >= 0.7)
        }
    }

    print(f"Guardando JSON...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    if os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)

    print(f"Listo: {OUTPUT_PATH}")
    print(f"  Con intencion:    {output['estadisticas']['con_intencion']}")
    print(f"  Con metodo:       {output['estadisticas']['con_metodo']}")
    print(f"  Alta relevancia:  {output['estadisticas']['alta_relevancia']}")

    if APAGAR_AL_TERMINAR:
        apagar_pc(f"Clasificacion completada: {total} articulos procesados")


if __name__ == "__main__":
    main()
