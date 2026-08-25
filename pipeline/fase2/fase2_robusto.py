#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 2 ROBUSTO: Clasificacion con checkpoint por articulo + loop infinito
- Guarda resultado tras cada articulo exitoso
- Errores van a log; al terminar cada vuelta reintenta los fallidos
- Ctrl+C guarda estado y sale; al reiniciar retoma desde checkpoint
- Loop infinito hasta que todo este clasificado o el usuario detenga
"""

import subprocess
import json
import signal
import sys
from pathlib import Path
from datetime import datetime

EXTRACT_DIR    = Path("pdfs_extraido")
OUTPUT_JSON    = "clasificacion_pdfs_completos.json"
CHECKPOINT     = "fase2_checkpoint.json"
ERROR_LOG      = "fase2_errores_log.json"
MODEL          = "claude-sonnet-5"
CLAUDE_CMD     = r"C:\Users\Luis Rojas\AppData\Roaming\npm\claude.cmd"
MAX_CHARS      = 600_000  # Sonnet 5 tiene 200k tokens (~800k chars); cabe todo

# --- Control de parada limpia ---
_stop_requested = False

def _handle_signal(sig, frame):
    global _stop_requested
    print("\n\n[STOP] Parada solicitada. Terminando articulo actual y guardando...")
    _stop_requested = True

signal.signal(signal.SIGINT,  _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

# --- Checkpoint ---

def load_checkpoint():
    if Path(CHECKPOINT).exists():
        with open(CHECKPOINT, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"procesados": [], "vuelta": 1, "inicio": datetime.now().isoformat()}

def save_checkpoint(cp):
    with open(CHECKPOINT, 'w', encoding='utf-8') as f:
        json.dump(cp, f, ensure_ascii=False, indent=2)

# --- Output JSON (append por articulo) ---

def load_output():
    if Path(OUTPUT_JSON).exists():
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "metadata": {
            "titulo": "Clasificacion PDFs - Revision Sistematica",
            "modelo": MODEL,
            "inicio": datetime.now().isoformat(),
            "articulos_clasificados": 0,
            "articulos_error": 0
        },
        "articulos": []
    }

def append_article(clasificacion):
    data = load_output()
    data["articulos"].append(clasificacion)
    data["metadata"]["articulos_clasificados"] = len(data["articulos"])
    data["metadata"]["ultima_actualizacion"] = datetime.now().isoformat()
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Error log ---

def load_errors():
    if Path(ERROR_LOG).exists():
        with open(ERROR_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"total": 0, "entradas": []}

def log_error(pdf_id, vuelta, razon):
    errors = load_errors()
    errors["entradas"].append({
        "pdf": pdf_id,
        "vuelta": vuelta,
        "razon": razon[:200],
        "timestamp": datetime.now().isoformat()
    })
    errors["total"] = len(errors["entradas"])
    with open(ERROR_LOG, 'w', encoding='utf-8') as f:
        json.dump(errors, f, ensure_ascii=False, indent=2)

# --- Claude CLI ---

def send_to_claude(prompt):
    try:
        result = subprocess.run(
            [CLAUDE_CMD, "-p", "--model", MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        if result.returncode != 0:
            return None
        out = result.stdout.strip()
        return out if out else None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f" [EXC:{type(e).__name__}]", end="", flush=True)
        return None

def classify_article(pdf_id, content):
    # Sonnet 5 tiene 200k tokens (~800k chars): todo cabe en una sola llamada
    # Si excede MAX_CHARS (casos extremos), truncar preservando inicio y fin
    if len(content) > MAX_CHARS:
        mitad = MAX_CHARS // 2
        content = content[:mitad] + "\n\n[...contenido truncado...]\n\n" + content[-mitad:]

    mensaje = f"""Analiza el siguiente articulo academico completo y retorna SOLO un JSON de clasificacion.

ARTICULO ID: {pdf_id}

---CONTENIDO COMPLETO---
{content}
---FIN DEL ARTICULO---

Retorna UNICAMENTE el siguiente JSON (sin markdown, sin texto adicional, sin ```json):

{{
  "id": "{pdf_id}",
  "titulo": "titulo del articulo",
  "autores": ["Autor1", "Autor2"],
  "year": 2024,
  "abstract": "resumen de 2-3 oraciones",
  "clasificacion": {{
    "variables_principales": {{
      "metodos_especifico": [],
      "metodos_general": [],
      "metricas": [],
      "intenciones": [],
      "dataset": [],
      "dataset_info": []
    }},
    "variables_adicionales": {{
      "temporal": null,
      "plataforma": [],
      "linguistica": [],
      "metodologica": []
    }}
  }},
  "relevancia_general": 0.75,
  "hallazgos_nuevos": []
}}

Valores validos para cada campo:
- metodos_especifico: M1_LogisticRegression M2_NaiveBayes M3_DecisionTree M4_GradientBoosting M5_KNN M6_SVM M7_NeuralNetwork M8_RandomForest M9_NLP_Traditional M10_DeepLearning M11_LSTM M12_Transformer M13_BERT M14_GraphNetwork M15_Ensemble M16_Clustering M17_TopicModeling M18_SemanticAnalysis M19_SentimentAnalysis M20_StylometryAnalysis M21_HybridMethod
- metodos_general: Machine Learning Deep Learning NLP Computer Vision Graph Analysis Statistical Analysis Linguistic Analysis Network Analysis Knowledge Graphs Ontologies Rule-Based Systems Hybrid Methods Transfer Learning
- metricas: D1_Precision_Recall D2_F1Score D3_Accuracy D4_AUC D5_Confusion_Matrix D6_Matthews_Correlation D7_Cohen_Kappa D8_Mean_Absolute_Error D9_RMSE D10_Silhouette_Score D11_Davies_Bouldin_Index D12_Execution_Time D13_Memory_Usage
- intenciones: I1_FakeNews I2_Manipulation I3_Misinformation I4_Satire I5_Rumors I6_BotActivity I7_EmotionAnalysis I8_PolarityAnalysis I9_ToxicContent I10_Deepfakes I11_Coordinated_Behavior I12_SuspiciousActivity I13_Credibility_Assessment
- plataforma: P1_Twitter P2_Facebook P3_News P4_Reddit P5_Instagram P6_YouTube P7_TikTok P8_Telegram P9_WhatsApp P10_Multiple P11_General
- linguistica: L1_English L2_Spanish L3_Chinese L4_Arabic L5_French L6_German L7_Multilingual L8_NotSpecified
- dataset: lista de nombres de datasets usados (ej: ["FakeNewsNet", "LIAR", "BuzzFeed"])
- dataset_info: para cada dataset encontrado, incluye un objeto con nombre y cualquier referencia util para encontrarlo (URL, DOI, repositorio GitHub, paper de referencia, etc.). Ejemplo:
  [
    {{"nombre": "FakeNewsNet", "url": "https://github.com/KaiDMML/FakeNewsNet", "referencia": "Shu et al. 2020"}},
    {{"nombre": "LIAR", "url": "https://www.cs.ucsb.edu/~william/data/liar_dataset.zip", "referencia": "Wang 2017"}},
    {{"nombre": "dataset propio", "url": null, "referencia": "creado por los autores, disponible bajo solicitud"}}
  ]
  Si no hay URL conocida, pon null en url pero igual describe como encontrarlo en referencia.
- relevancia_general: float 0.0-1.0 (que tan relevante es para deteccion de intenciones comunicativas en redes sociales)
- hallazgos_nuevos: metodos o intenciones NO listados arriba que encontraste en el articulo
"""

    respuesta = send_to_claude(mensaje)
    if not respuesta:
        return None, "Claude no respondio"

    try:
        j_start = respuesta.find('{')
        j_end   = respuesta.rfind('}') + 1
        if j_start >= 0 and j_end > j_start:
            return json.loads(respuesta[j_start:j_end]), None
    except json.JSONDecodeError as e:
        return None, f"JSON invalido: {str(e)[:100]}"

    return None, "No se encontro JSON en respuesta"

# --- Main ---

def main():
    global _stop_requested

    print("=" * 70)
    print("FASE 2 ROBUSTO: Clasificacion con loop infinito + checkpoint")
    print("=" * 70)
    print(f"Modelo: {MODEL}")
    print(f"Output: {OUTPUT_JSON}")
    print(f"Ctrl+C para parar limpiamente\n")

    cp = load_checkpoint()
    procesados = set(cp.get("procesados", []))
    vuelta     = cp.get("vuelta", 1)

    print(f"Checkpoint: {len(procesados)} articulos ya procesados")
    if procesados:
        print(f"Reanudando desde vuelta {vuelta}...")

    all_dirs = sorted([d for d in EXTRACT_DIR.iterdir() if d.is_dir()])
    total    = len(all_dirs)

    while not _stop_requested:
        pendientes = [d for d in all_dirs if d.name not in procesados]

        if not pendientes:
            print("\n" + "=" * 70)
            print("✅ FASE 2 COMPLETADA — Todos los articulos clasificados")
            print("=" * 70)
            break

        errores_vuelta = []
        print(f"\n{'='*70}")
        print(f"VUELTA {vuelta} | {len(pendientes)} pendientes de {total} total")
        print(f"{'='*70}\n")

        for idx, pdf_dir in enumerate(pendientes, 1):
            if _stop_requested:
                break

            pdf_id = pdf_dir.name
            pct    = int((len(procesados) + idx - 1) * 100 / total)
            print(f"[{len(procesados)+idx:3d}/{total}] [{pct:3d}%] V{vuelta} {pdf_id[:45]:45s} ", end="", flush=True)

            content_file = pdf_dir / "content.txt"
            if not content_file.exists():
                print("[SIN CONTENIDO]")
                errores_vuelta.append(pdf_id)
                log_error(pdf_id, vuelta, "No existe content.txt")
                continue

            try:
                content = content_file.read_text(encoding='utf-8', errors='replace')
            except Exception as e:
                print("[ERROR LECTURA]")
                errores_vuelta.append(pdf_id)
                log_error(pdf_id, vuelta, f"Error lectura: {e}")
                continue

            if len(content) < 100:
                print("[CONTENIDO VACIO]")
                errores_vuelta.append(pdf_id)
                log_error(pdf_id, vuelta, "Contenido muy corto")
                continue

            try:
                clasificacion, error = classify_article(pdf_id, content)
            except Exception as e:
                clasificacion, error = None, f"Excepcion: {type(e).__name__}: {e}"

            if clasificacion:
                try:
                    append_article(clasificacion)
                    procesados.add(pdf_id)
                    cp["procesados"] = list(procesados)
                    cp["vuelta"]     = vuelta
                    cp["ultimo"]     = pdf_id
                    cp["ultima_actualizacion"] = datetime.now().isoformat()
                    save_checkpoint(cp)
                    print("[OK]")
                except Exception as e:
                    print(f"[ERROR GUARDADO: {e}]")
                    errores_vuelta.append(pdf_id)
            else:
                print(f"[ERROR]")
                errores_vuelta.append(pdf_id)
                try:
                    log_error(pdf_id, vuelta, error or "desconocido")
                except Exception:
                    pass

        # Resumen de vuelta
        print(f"\n--- Vuelta {vuelta} finalizada ---")
        print(f"Procesados acumulados : {len(procesados)}/{total}")
        print(f"Errores esta vuelta   : {len(errores_vuelta)}")

        if _stop_requested:
            print("\n[STOP] Script detenido por usuario.")
            print(f"Al reiniciar continuara desde articulo #{len(procesados)+1}")
            break

        if not errores_vuelta:
            print("\n✅ Sin errores. Clasificacion completada.")
            break

        print(f"\nReintentando {len(errores_vuelta)} articulos en vuelta {vuelta+1}...")
        vuelta += 1
        cp["vuelta"] = vuelta
        save_checkpoint(cp)

    # Resumen final
    data = load_output()
    errors = load_errors()
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"Total articulos     : {total}")
    print(f"Clasificados OK     : {data['metadata']['articulos_clasificados']}")
    print(f"Errores en log      : {errors['total']}")
    print(f"Archivo resultado   : {OUTPUT_JSON}")
    print(f"Log de errores      : {ERROR_LOG}")

if __name__ == "__main__":
    main()
