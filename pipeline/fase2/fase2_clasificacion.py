#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 2: CLASIFICACION DE 554 PDFs CON CLAUDE
- Lee content.txt de cada PDF ya extraído
- Clasifica con Claude CLI
- Genera JSON con mismo esquema que antes
- Detecta hallazgos nuevos
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

EXTRACT_DIR = Path("pdfs_extraido")
OUTPUT_JSON = "clasificacion_pdfs_completos.json"
ERROR_REPORT = "reporte_clasificacion_errores.json"

def classify_with_claude(pdf_id, content):
    """Clasifica PDF con Claude CLI"""

    prompt = f"""Analiza el siguiente contenido de artículo académico y clasifícalo:

ARTÍCULO ID: {pdf_id}

---CONTENIDO---
{content[:12000]}
---FIN CONTENIDO---

TAREA: Retorna ÚNICAMENTE este JSON (sin texto adicional):

{{
  "id": "{pdf_id}",
  "titulo": "Título extraído del contenido",
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

Si encuentras categorías no listadas, usa prefijos similares en hallazgos_nuevos (M22_NuevoMetodo, I14_NuevaIntencion, etc.)
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

    except Exception as e:
        pass

    return None

def main():
    print("=" * 80)
    print("FASE 2: CLASIFICACION DE 554 PDFs CON CLAUDE")
    print("=" * 80)
    print()

    # Obtener PDFs extraídos
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
            "modelo_usado": "claude-cli-opus-4-8"
        },
        "articulos": []
    }

    errores = {"total_errores": 0, "pdfs": []}
    hallazgos_nuevos = {"metodos": set(), "intenciones": set()}

    for idx, pdf_dir in enumerate(pdf_dirs, 1):
        pdf_id = pdf_dir.name
        pct = (idx * 100) // total

        print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id:40s} ", end="", flush=True)

        # Leer content.txt
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

            # Clasificar con Claude
            clasificacion = classify_with_claude(pdf_id, content)

            if not clasificacion:
                print("[ERROR Claude]")
                errores["total_errores"] += 1
                errores["pdfs"].append({"pdf": pdf_id, "razon": "Error clasificacion Claude"})
                data["metadata"]["articulos_error"] += 1
                continue

            # Registrar hallazgos nuevos
            for hallazgo in clasificacion.get("hallazgos_nuevos", []):
                if hallazgo.startswith("M"):
                    hallazgos_nuevos["metodos"].add(hallazgo)
                elif hallazgo.startswith("I"):
                    hallazgos_nuevos["intenciones"].add(hallazgo)

            data["articulos"].append(clasificacion)
            data["metadata"]["articulos_clasificados"] += 1

            print("[OK]")

            # Guardar checkpoint cada 10
            if idx % 10 == 0:
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[ERROR]")
            errores["total_errores"] += 1
            errores["pdfs"].append({"pdf": pdf_id, "razon": str(e)[:50]})
            data["metadata"]["articulos_error"] += 1

    # Guardar JSON final
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Guardar reporte de errores
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

    if errores["total_errores"] > 0:
        print(f"Errores: {ERROR_REPORT}")

    print("\nHallazgos nuevos:")
    print(f"  Metodos: {len(hallazgos_nuevos['metodos'])}")
    for m in sorted(hallazgos_nuevos['metodos']):
        print(f"    - {m}")
    print(f"  Intenciones: {len(hallazgos_nuevos['intenciones'])}")
    for i in sorted(hallazgos_nuevos['intenciones']):
        print(f"    - {i}")

if __name__ == "__main__":
    main()
