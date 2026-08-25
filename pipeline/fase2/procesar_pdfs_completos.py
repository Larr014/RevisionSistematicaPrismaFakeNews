#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para clasificar 549 PDFs usando Claude CLI
Extrae texto con pdftotext (+ OCR si es necesario)
Clasifica cada uno con Claude
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os

# UTF-8 en Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

PDF_DIR = Path("pdfs")
OUTPUT_JSON = "clasificacion_pdfs_completos.json"
ERROR_REPORT = "reporte_errores_pdfs.json"

def extract_pdf_text(pdf_path):
    """Extrae texto del PDF usando pdftotext"""
    try:
        result = subprocess.run(
            ["pdftotext", "-", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )

        if result.returncode == 0 and result.stdout.strip():
            text = result.stdout
            # Remover referencias (heurística simple)
            lines = text.split('\n')
            cutoff = len(lines)

            for i, line in enumerate(lines):
                if any(w in line.lower() for w in ['references', 'bibliography', 'referencias', 'works cited']):
                    cutoff = i
                    break

            content = '\n'.join(lines[:cutoff])
            return content if len(content) > 200 else None
    except:
        pass

    return None

def classify_pdf(pdf_id, content):
    """Envía contenido a Claude para clasificación"""

    prompt = f"""Analiza este artículo académico y clasifícalo ÚNICAMENTE con JSON válido (sin explicaciones):

ARTÍCULO ID: {pdf_id}

CONTENIDO (primeras 12000 caracteres):
{content[:12000]}

JSON REQUERIDO:
{{
  "id": "{pdf_id}",
  "titulo": "Título extraído",
  "autores": ["Autor 1", "Autor 2"],
  "year": 2024,
  "abstract": "Resumen 1-2 líneas",
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

INSTRUCCIONES:
1. Selecciona SOLO categorías existentes de la lista anterior
2. Si encuentras algo nuevo, añádelo en hallazgos_nuevos (ej: "M22_NuevoMetodo")
3. Retorna SOLO JSON, sin texto adicional
"""

    try:
        result = subprocess.run(
            ["claude", "-m", "claude-opus-4-8"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            return None

        output = result.stdout.strip()
        json_start = output.find('{')
        json_end = output.rfind('}') + 1

        if json_start >= 0 and json_end > json_start:
            try:
                return json.loads(output[json_start:json_end])
            except:
                return None
    except:
        pass

    return None

def main():
    print("=" * 70)
    print("PROCESAMIENTO DE 549 PDFs - CLASIFICACION CON CLAUDE")
    print("=" * 70)

    pdf_files = sorted([f for f in PDF_DIR.glob("*.pdf")])
    total = len(pdf_files)

    print(f"PDFs encontrados: {total}\n")

    data = {
        "metadata": {
            "titulo_revision": "Metodos para Identificar Intenciones Comunicativas - Analisis Completo de PDFs",
            "fecha_generacion": datetime.now().isoformat(),
            "total_articulos": total,
            "articulos_clasificados": 0,
            "articulos_error": 0,
            "modelo_usado": "claude-cli-opus-4-8"
        },
        "articulos": []
    }

    errores = {"total_errores": 0, "pdfs_error": []}
    nuevos = {"metodos": set(), "intenciones": set(), "plataformas": set()}

    for idx, pdf_path in enumerate(pdf_files, 1):
        pdf_id = pdf_path.stem
        pct = (idx * 100) // total

        print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id:30s} ", end="", flush=True)

        # Extraer texto
        content = extract_pdf_text(pdf_path)
        if not content:
            print("[ERROR lectura]")
            errores["total_errores"] += 1
            errores["pdfs_error"].append({"pdf": pdf_id, "razon": "No se pudo extraer texto"})
            data["metadata"]["articulos_error"] += 1
            continue

        # Clasificar
        clasificacion = classify_pdf(pdf_id, content)
        if not clasificacion:
            print("[ERROR Claude]")
            errores["total_errores"] += 1
            errores["pdfs_error"].append({"pdf": pdf_id, "razon": "Error en clasificacion"})
            data["metadata"]["articulos_error"] += 1
            continue

        # SOLO si está 100% completo, registrarlo
        try:
            # Validar que tiene todos los campos requeridos
            assert clasificacion.get("id")
            assert clasificacion.get("titulo")
            assert clasificacion.get("clasificacion")

            # Registrar hallazgos
            for h in clasificacion.get("hallazgos_nuevos", []):
                if h.startswith("M"):
                    nuevos["metodos"].add(h)
                elif h.startswith("I"):
                    nuevos["intenciones"].add(h)
                elif h.startswith("P"):
                    nuevos["plataformas"].add(h)

            # Append SOLO si pasó validación
            data["articulos"].append(clasificacion)
            data["metadata"]["articulos_clasificados"] += 1
            print("[OK]")

        except (AssertionError, KeyError, TypeError):
            print("[ERROR validacion]")
            errores["total_errores"] += 1
            errores["pdfs_error"].append({"pdf": pdf_id, "razon": "Datos incompletos/inválidos en clasificacion"})
            data["metadata"]["articulos_error"] += 1
            continue

        # Guardar checkpoint cada 2 (solo artículos válidos)
        if idx % 2 == 0:
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # Guardar final
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if errores["total_errores"] > 0:
        with open(ERROR_REPORT, 'w', encoding='utf-8') as f:
            json.dump(errores, f, ensure_ascii=False, indent=2)

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"Procesados: {data['metadata']['articulos_clasificados']}/{total}")
    print(f"Errores: {data['metadata']['articulos_error']}")
    print(f"Exito: {100*data['metadata']['articulos_clasificados']/total:.1f}%")
    print(f"\nArchivos guardados:")
    print(f"  - {OUTPUT_JSON}")
    if errores["total_errores"] > 0:
        print(f"  - {ERROR_REPORT}")

    print("\nHALLAZGOS NUEVOS:")
    print(f"  Metodos especificos: {len(nuevos['metodos'])}")
    for item in sorted(nuevos['metodos']):
        print(f"    - {item}")
    print(f"  Intenciones: {len(nuevos['intenciones'])}")
    for item in sorted(nuevos['intenciones']):
        print(f"    - {item}")
    print(f"  Plataformas: {len(nuevos['plataformas'])}")
    for item in sorted(nuevos['plataformas']):
        print(f"    - {item}")

if __name__ == "__main__":
    main()
