#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para clasificar PDFs usando Claude CLI
Versión sin dependencias externas, solo subprocess
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import locale

# Forzar UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

PDF_DIR = Path("pdfs")
OUTPUT_JSON = "clasificacion_pdfs_completos.json"
ERROR_REPORT = "reporte_errores_pdfs.json"

def classify_with_claude_simple(pdf_id, pdf_name):
    """
    Envía solicitud simple a Claude CLI para analizar un PDF
    Claude leerá el PDF directamente desde el archivo
    """

    prompt = f"""Por favor, analiza el archivo PDF: {pdf_path_str}

Extrae:
1. Título del artículo
2. Autores (lista)
3. Año
4. Abstract/resumen
5. Métodos usados (clasifica según: M1_Logistic, M2_NaiveBayes, M3_DecisionTree, M4_GradientBoosting, M5_KNN, M6_SVM, M7_NeuralNetwork, M8_RandomForest, M9_NLP_Trad, M10_DeepLearning, M11_LSTM, M12_Transformer, M13_BERT, M14_GraphNetwork, M15_Ensemble, M16_Clustering, M17_TopicModeling, M18_SemanticAnalysis, M19_SentimentAnalysis, M20_Stylometry, M21_HybridMethod)
6. Métodos generales: Machine Learning, Deep Learning, NLP, Computer Vision, Graph Analysis, etc.
7. Qué intenta detectar (I1_FakeNews, I2_Manipulation, I3_Misinformation, I4_Satire, I5_Rumors, I6_BotActivity, I7_EmotionAnalysis, I8_PolarityAnalysis, I9_ToxicContent, I10_Deepfakes, I11_Coordinated_Behavior, I12_SuspiciousActivity, I13_Credibility_Assessment)
8. Plataformas (P1_Twitter, P2_Facebook, P3_News, P4_Reddit, P5_Instagram, P6_YouTube, P7_TikTok, P8_Telegram, P9_WhatsApp, P10_Multiple, P11_General)
9. Idioma (L1_English, L2_Spanish, L3_Chinese, L4_Arabic, L5_French, L6_German, L7_Multilingual, L8_NotSpecified)
10. Relevancia general (0-1)
11. Cualquier nuevo método/intención/categoría no listada

Retorna SOLO JSON válido (nada más):
{{
  "id": "{pdf_id}",
  "titulo": "Título",
  "autores": ["Autor1", "Autor2"],
  "year": 2024,
  "abstract": "Resumen",
  "clasificacion": {{
    "variables_principales": {{
      "metodos_especifico": ["M1", "M2"],
      "metodos_general": ["Machine Learning"],
      "metricas": [],
      "intenciones": ["I1_FakeNews"],
      "dataset": []
    }},
    "variables_adicionales": {{
      "temporal": null,
      "plataforma": ["P1_Twitter"],
      "linguistica": ["L1_English"],
      "metodologica": []
    }}
  }},
  "relevancia_general": 0.75,
  "hallazgos_nuevos": []
}}
"""

    try:
        result = subprocess.run(
            ["claude", "-m", "claude-opus-4-8", pdf_path_str],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8'
        )

        if result.returncode != 0:
            return None

        output = result.stdout.strip()
        json_start = output.find('{')
        json_end = output.rfind('}') + 1

        if json_start >= 0 and json_end > json_start:
            json_str = output[json_start:json_end]
            try:
                return json.loads(json_str)
            except:
                return None

    except Exception as e:
        pass

    return None

def main():
    print("[INICIO] Procesamiento de PDFs para clasificacion")
    print(f"Directorio: {PDF_DIR}")
    print()

    pdf_files = sorted([f for f in PDF_DIR.glob("*.pdf")])
    total = len(pdf_files)

    print(f"Total PDFs: {total}")
    print("-" * 70)

    clasificacion_data = {
        "metadata": {
            "titulo_revision": "Analisis Completo de PDFs Recolectados",
            "fecha_generacion": datetime.now().isoformat(),
            "total_articulos": total,
            "articulos_clasificados": 0,
            "articulos_error": 0,
            "modelo_usado": "claude-cli-opus-4-8"
        },
        "articulos": []
    }

    errores = {
        "total_errores": 0,
        "pdfs_error": []
    }

    hallazgos_nuevos = {
        "metodos_especificos": [],
        "intenciones": [],
        "plataformas": []
    }

    for idx, pdf_path in enumerate(pdf_files, 1):
        pdf_id = pdf_path.stem
        global pdf_path_str
        pdf_path_str = str(pdf_path)

        pct = (idx * 100) // total
        print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id:30s} ", end="", flush=True)

        clasificacion = classify_with_claude_simple(pdf_id, pdf_path.name)

        if not clasificacion:
            print("[ERROR]")
            errores["total_errores"] += 1
            errores["pdfs_error"].append({
                "pdf": pdf_id,
                "razon": "Error clasificacion con Claude"
            })
            clasificacion_data["metadata"]["articulos_error"] += 1
            continue

        # Registrar hallazgos nuevos
        for hallazgo in clasificacion.get("hallazgos_nuevos", []):
            if hallazgo not in hallazgos_nuevos["metodos_especificos"] + \
                             hallazgos_nuevos["intenciones"] + \
                             hallazgos_nuevos["plataformas"]:
                if hallazgo.startswith("M"):
                    hallazgos_nuevos["metodos_especificos"].append(hallazgo)
                elif hallazgo.startswith("I"):
                    hallazgos_nuevos["intenciones"].append(hallazgo)
                elif hallazgo.startswith("P"):
                    hallazgos_nuevos["plataformas"].append(hallazgo)

        clasificacion_data["articulos"].append(clasificacion)
        clasificacion_data["metadata"]["articulos_clasificados"] += 1

        print("[OK]")

        # Guardar progreso cada 10 artículos
        if idx % 10 == 0:
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(clasificacion_data, f, ensure_ascii=False, indent=2)

    # Guardar JSON final
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(clasificacion_data, f, ensure_ascii=False, indent=2)

    # Guardar reporte de errores
    if errores["total_errores"] > 0:
        with open(ERROR_REPORT, 'w', encoding='utf-8') as f:
            json.dump(errores, f, ensure_ascii=False, indent=2)

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"Procesados: {clasificacion_data['metadata']['articulos_clasificados']}/{total}")
    print(f"Errores: {clasificacion_data['metadata']['articulos_error']}")
    print(f"Exito: {100*clasificacion_data['metadata']['articulos_clasificados']/total:.1f}%")
    print(f"\nArchivos:")
    print(f"  {OUTPUT_JSON}")
    if errores["total_errores"] > 0:
        print(f"  {ERROR_REPORT}")

    print("\nHALLAZGOS NUEVOS:")
    print(f"  Metodos: {len(hallazgos_nuevos['metodos_especificos'])}")
    for item in sorted(set(hallazgos_nuevos['metodos_especificos'])):
        print(f"    - {item}")
    print(f"  Intenciones: {len(hallazgos_nuevos['intenciones'])}")
    for item in sorted(set(hallazgos_nuevos['intenciones'])):
        print(f"    - {item}")

if __name__ == "__main__":
    main()
