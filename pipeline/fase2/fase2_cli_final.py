#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 2 FINAL: Clasificar 554 PDFs con Claude CLI + Segmentacion
- Claude CLI con -p (print mode)
- Segmentacion en partes de 4000 chars
- Encoding UTF-8 robusto
- JSON limpio como resultado
"""

import subprocess
import math
import json
from pathlib import Path
from datetime import datetime

EXTRACT_DIR = Path("pdfs_extraido")
OUTPUT_JSON = "clasificacion_pdfs_completos.json"
ERROR_REPORT = "reporte_clasificacion_errores.json"

def send_to_claude(prompt):
    """Envia prompt a Claude CLI con Sonnet"""
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "claude-sonnet-5"],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120
        )

        if result.returncode != 0:
            return None

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

def classify_with_segmentation(pdf_id, content):
    """Clasifica PDF con segmentacion"""

    TAMAÑO_PARTE = 4000
    num_partes = math.ceil(len(content) / TAMAÑO_PARTE)

    # Enviar cada parte
    for i in range(num_partes):
        inicio = i * TAMAÑO_PARTE
        fin = min((i + 1) * TAMAÑO_PARTE, len(content))
        parte = content[inicio:fin]

        if i < num_partes - 1:
            # Partes intermedias
            mensaje = f"""ARTICULO: {pdf_id}
Parte {i+1} de {num_partes}. Lee y recuerda.

---PARTE {i+1}---
{parte}
---FIN PARTE {i+1}---

Responde: "Parte {i+1} recibida"
"""
        else:
            # Ultima parte + analisis
            mensaje = f"""ARTICULO: {pdf_id}
Ultima parte {i+1} de {num_partes}:

---PARTE {i+1}---
{parte}
---FIN PARTE {i+1}---

Ya leiste TODO. Retorna SOLO JSON:

{{
  "id": "{pdf_id}",
  "titulo": "Titulo",
  "autores": ["Autor1"],
  "year": 2024,
  "abstract": "Resumen",
  "clasificacion": {{
    "variables_principales": {{
      "metodos_especifico": ["M1_LogisticRegression", "M2_NaiveBayes", "M3_DecisionTree", "M4_GradientBoosting", "M5_KNN", "M6_SVM", "M7_NeuralNetwork", "M8_RandomForest", "M9_NLP_Traditional", "M10_DeepLearning", "M11_LSTM", "M12_Transformer", "M13_BERT", "M14_GraphNetwork", "M15_Ensemble", "M16_Clustering", "M17_TopicModeling", "M18_SemanticAnalysis", "M19_SentimentAnalysis", "M20_StylometryAnalysis", "M21_HybridMethod"],
      "metodos_general": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Graph Analysis", "Statistical Analysis", "Linguistic Analysis", "Network Analysis", "Knowledge Graphs", "Ontologies", "Rule-Based Systems", "Hybrid Methods", "Transfer Learning"],
      "metricas": ["D1_Precision_Recall", "D2_F1Score", "D3_Accuracy", "D4_AUC", "D5_Confusion_Matrix", "D6_Matthews_Correlation", "D7_Cohen_Kappa", "D8_Mean_Absolute_Error", "D9_RMSE", "D10_Silhouette_Score", "D11_Davies_Bouldin_Index", "D12_Execution_Time", "D13_Memory_Usage"],
      "intenciones": ["I1_FakeNews", "I2_Manipulation", "I3_Misinformation", "I4_Satire", "I5_Rumors", "I6_BotActivity", "I7_EmotionAnalysis", "I8_PolarityAnalysis", "I9_ToxicContent", "I10_Deepfakes", "I11_Coordinated_Behavior", "I12_SuspiciousActivity", "I13_Credibility_Assessment"],
      "dataset": []
    }},
    "variables_adicionales": {{
      "temporal": null,
      "plataforma": ["P1_Twitter", "P2_Facebook", "P3_News", "P4_Reddit", "P5_Instagram", "P6_YouTube", "P7_TikTok", "P8_Telegram", "P9_WhatsApp", "P10_Multiple", "P11_General"],
      "linguistica": ["L1_English", "L2_Spanish", "L3_Chinese", "L4_Arabic", "L5_French", "L6_German", "L7_Multilingual", "L8_NotSpecified"],
      "metodologica": []
    }}
  }},
  "relevancia_general": 0.75,
  "hallazgos_nuevos": []
}}
"""

        respuesta = send_to_claude(mensaje)
        if not respuesta:
            return None

    # Parsear JSON de la ultima respuesta
    try:
        json_start = respuesta.find('{')
        json_end = respuesta.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = respuesta[json_start:json_end]
            return json.loads(json_str)
    except:
        pass

    return None

def main():
    print("=" * 80)
    print("FASE 2: CLASIFICACION DE 554 PDFs CON CLAUDE CLI")
    print("=" * 80)
    print()

    pdf_dirs = sorted([d for d in EXTRACT_DIR.iterdir() if d.is_dir()])
    total = len(pdf_dirs)

    print(f"PDFs a clasificar: {total}\n")

    data = {
        "metadata": {
            "titulo_revision": "Metodos para Identificar Intenciones Comunicativas - Clasificacion de PDFs",
            "fecha_generacion": datetime.now().isoformat(),
            "total_articulos": total,
            "articulos_clasificados": 0,
            "articulos_error": 0,
            "modelo_usado": "claude-sonnet-5-via-cli"
        },
        "articulos": []
    }

    errores = {"total_errores": 0, "pdfs": []}
    hallazgos_nuevos = {"metodos": set(), "intenciones": set()}

    for idx, pdf_dir in enumerate(pdf_dirs, 1):
        pdf_id = pdf_dir.name
        pct = (idx * 100) // total

        print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id:40s} ", end="", flush=True)

        content_file = pdf_dir / "content.txt"
        if not content_file.exists():
            print("[ERROR lectura]")
            errores["total_errores"] += 1
            errores["pdfs"].append({"pdf": pdf_id, "razon": "No existe content.txt"})
            data["metadata"]["articulos_error"] += 1
            continue

        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content or len(content) < 100:
                print("[ERROR contenido vacio]")
                errores["total_errores"] += 1
                errores["pdfs"].append({"pdf": pdf_id, "razon": "Contenido muy corto"})
                data["metadata"]["articulos_error"] += 1
                continue

            clasificacion = classify_with_segmentation(pdf_id, content)

            if not clasificacion:
                print("[ERROR clasificacion]")
                errores["total_errores"] += 1
                errores["pdfs"].append({"pdf": pdf_id, "razon": "Error Claude"})
                data["metadata"]["articulos_error"] += 1
                continue

            for hallazgo in clasificacion.get("hallazgos_nuevos", []):
                if hallazgo.startswith("M"):
                    hallazgos_nuevos["metodos"].add(hallazgo)
                elif hallazgo.startswith("I"):
                    hallazgos_nuevos["intenciones"].add(hallazgo)

            data["articulos"].append(clasificacion)
            data["metadata"]["articulos_clasificados"] += 1

            print("[OK]")

            if idx % 10 == 0:
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print("[ERROR]")
            errores["total_errores"] += 1
            errores["pdfs"].append({"pdf": pdf_id, "razon": str(e)[:50]})
            data["metadata"]["articulos_error"] += 1

    # Guardar final
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if errores["total_errores"] > 0:
        with open(ERROR_REPORT, 'w', encoding='utf-8') as f:
            json.dump(errores, f, ensure_ascii=False, indent=2)

    # Resumen
    print("\n" + "=" * 80)
    print("FASE 2 COMPLETADA")
    print("=" * 80)
    print(f"Total: {total}")
    print(f"Clasificados: {data['metadata']['articulos_clasificados']}")
    print(f"Errores: {data['metadata']['articulos_error']}")
    print(f"Tasa exito: {100 * data['metadata']['articulos_clasificados'] / total:.1f}%")
    print(f"\nArchivo: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
