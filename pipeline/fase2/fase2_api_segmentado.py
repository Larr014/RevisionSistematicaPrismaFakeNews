#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 2: CLASIFICACION CON API ANTHROPIC + SEGMENTACION
- Lee cada PDF extraído
- Segmenta en partes de 4000 caracteres
- Envía partes a Claude con razonamiento
- Pide análisis completo al final
- Genera JSON clasificación
"""

import json
import math
import os
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic

EXTRACT_DIR = Path("pdfs_extraido")
OUTPUT_JSON = "clasificacion_pdfs_completos.json"
ERROR_REPORT = "reporte_clasificacion_errores.json"

# Verificar API key - incluir la key directamente si es necesario
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    # Intentar configurar la key desde variable de entorno del sistema
    import subprocess
    try:
        result = subprocess.run(
            ['powershell', '-Command', '$env:ANTHROPIC_API_KEY'],
            capture_output=True,
            text=True,
            timeout=5
        )
        API_KEY = result.stdout.strip()
    except:
        pass

if not API_KEY:
    print("ERROR: ANTHROPIC_API_KEY no configurada")
    print("Asegúrate de que ANTHROPIC_API_KEY esté en variables de entorno")
    exit(1)

client = Anthropic(api_key=API_KEY)

def classify_with_segmentation(pdf_id, content):
    """Clasifica PDF con segmentación y razonamiento"""

    TAMAÑO_PARTE = 4000
    num_partes = math.ceil(len(content) / TAMAÑO_PARTE)

    conversation_history = []

    # Enviar cada parte a Claude
    for i in range(num_partes):
        inicio = i * TAMAÑO_PARTE
        fin = min((i + 1) * TAMAÑO_PARTE, len(content))
        parte = content[inicio:fin]

        if i < num_partes - 1:
            # Partes intermedias: solo recibir
            mensaje = f"""Eres un asistente que analiza un artículo académico POR PARTES.

Esta es PARTE {i+1} de {num_partes}. Lee y recuerda el contenido.

---PARTE {i+1}---
{parte}
---FIN PARTE {i+1}---

Responde solo: "Parte {i+1} recibida ({len(parte)} caracteres)"
"""
        else:
            # Última parte: pedir análisis
            mensaje = f"""Esta es la ÚLTIMA PARTE {i+1} de {num_partes}:

---PARTE {i+1}---
{parte}
---FIN PARTE {i+1}---

Ya has leído TODAS las partes del artículo {pdf_id}.

Ahora analiza TODO el contenido que leíste y RETORNA ÚNICAMENTE este JSON (sin explicaciones, sin markdown, solo JSON puro):

{{
  "id": "{pdf_id}",
  "titulo": "Título del artículo",
  "autores": ["Autor1", "Autor2"],
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
"""

        try:
            conversation_history.append({
                "role": "user",
                "content": mensaje
            })

            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=4096,
                messages=conversation_history
            )

            assistant_message = response.content[0].text
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            if i < num_partes - 1:
                print(f"  Parte {i+1}/{num_partes}: OK")
            else:
                # Parte final: parsear JSON
                print(f"  Parte {i+1}/{num_partes}: Analizando...")

                # Intentar extraer JSON
                json_start = assistant_message.find('{')
                json_end = assistant_message.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    try:
                        json_str = assistant_message[json_start:json_end]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        return None
                else:
                    return None

        except Exception as e:
            print(f"  ERROR: {e}")
            return None

    return None

def main():
    print("=" * 80)
    print("FASE 2: CLASIFICACION CON API ANTHROPIC + SEGMENTACION")
    print("=" * 80)
    print()

    # Obtener PDFs extraídos
    pdf_dirs = sorted([d for d in EXTRACT_DIR.iterdir() if d.is_dir()])
    total = len(pdf_dirs)

    print(f"PDFs a clasificar: {total}\n")

    data = {
        "metadata": {
            "titulo_revision": "Metodos para Identificar Intenciones Comunicativas - Clasificacion con API",
            "fecha_generacion": datetime.now().isoformat(),
            "total_articulos": total,
            "articulos_clasificados": 0,
            "articulos_error": 0,
            "modelo_usado": "claude-opus-4-8-api"
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

            # Clasificar con segmentación
            print("\n", end="")
            clasificacion = classify_with_segmentation(pdf_id, content)

            if not clasificacion:
                print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id:40s} [ERROR JSON]")
                errores["total_errores"] += 1
                errores["pdfs"].append({"pdf": pdf_id, "razon": "JSON inválido"})
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

            print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id:40s} [OK]")

            # Guardar checkpoint cada 10
            if idx % 10 == 0:
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id:40s} [ERROR]")
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
