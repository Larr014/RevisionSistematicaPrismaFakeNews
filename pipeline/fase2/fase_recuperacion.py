#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE RECUPERACION: Extraccion + Clasificacion para los 10 articulos no procesados.

Para cada articulo:
  1. Extraccion de texto:
     - PDFs con texto digital -> pdftotext
     - PDFs escaneados        -> pdftoppm + Tesseract OCR (todas las paginas)
  2. Clasificacion via Claude CLI (igual que fase2_robusto)

Si un paso falla, se registra en el log y continua con el siguiente.
Al terminar, imprime resumen completo.
"""

import json
import subprocess
import sys
import shutil
import time
import re
import tempfile
from pathlib import Path
from datetime import datetime

# ── Rutas ──────────────────────────────────────────────────────────────────────
PDF_DIR      = Path("pdfs")
EXTRACT_DIR  = Path("pdfs_extraido")
OUTPUT_JSON  = "clasificacion_pdfs_completos.json"
CHECKPOINT   = "fase2_checkpoint.json"
LOG_FILE     = "fase_recuperacion_log.json"
SUMMARY_FILE = "fase_recuperacion_resumen.txt"

TESSERACT    = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
PDFTOTEXT    = r"C:\poppler\Library\bin\pdftotext.exe"
PDFTOPPM     = r"C:\poppler\Library\bin\pdftoppm.exe"
CLAUDE_CMD   = r"C:\Users\Luis Rojas\AppData\Roaming\npm\claude.cmd"
MODEL        = "claude-sonnet-5"
MAX_CHARS    = 600_000

os_env = {"TESSDATA_PREFIX": r"C:\Program Files\Tesseract-OCR\tessdata"}

# ── Los 10 articulos objetivo ──────────────────────────────────────────────────
# Formato: (id_corto, nombre_carpeta_en_pdfs_extraido, tipo)
TARGETS = [
    # PDFs escaneados — requieren OCR
    # NOTA: 000159, 000845, 001930, 001961 ya estan procesados bajo nombre corto en checkpoint
    # Solo quedan 3 escaneados sin procesar + 001887 (texto)
    ("articulo_001755", "articulo_001755",   "ocr"),   # 15MB escaneado
    ("articulo_003285", "articulo_003285",   "ocr"),   # 6.7MB escaneado
    ("articulo_003326", "articulo_003326",   "ocr"),   # 4.3MB escaneado
    # PDF con texto digital — fallo extraccion previa
    ("articulo_001887", "articulo_001887",   "text"),  # 1.4MB, tiene texto digital
]

# ── Log ────────────────────────────────────────────────────────────────────────
log_entries = []

def log(art_id, fase, estado, detalle=""):
    entry = {
        "id":        art_id,
        "fase":      fase,
        "estado":    estado,
        "detalle":   detalle[:300],
        "timestamp": datetime.now().isoformat(),
    }
    log_entries.append(entry)
    icon = "OK" if estado == "ok" else "FAIL"
    print(f"  [{icon}] {fase}: {detalle[:80]}" if detalle else f"  [{icon}] {fase}")
    _save_log()

def _save_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({"total": len(log_entries), "entradas": log_entries}, f,
                  ensure_ascii=False, indent=2)

# ── Utilidades ────────────────────────────────────────────────────────────────
def cleanup_text(text):
    if not text:
        return ""
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = "".join(c for c in text if ord(c) >= 32 or c in "\n\t")
    return text.strip()

def find_pdf(art_id_short):
    matches = list(PDF_DIR.glob(f"{art_id_short}*.pdf"))
    return matches[0] if matches else None

# ── Extraccion ────────────────────────────────────────────────────────────────
def extract_text_pdftotext(pdf_path):
    """Extrae texto de PDF digital con pdftotext."""
    try:
        r = subprocess.run(
            [PDFTOTEXT, str(pdf_path), "-"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return cleanup_text(r.stdout)
    except Exception as e:
        return None
    return None

def extract_text_ocr(pdf_path, extract_subdir, max_pages=None):
    """Convierte paginas a imagen con pdftoppm y aplica Tesseract OCR."""
    images_dir = extract_subdir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Detectar numero de paginas
    try:
        r = subprocess.run(
            [PDFTOTEXT, str(pdf_path), "-"],
            capture_output=True, timeout=10
        )
    except Exception:
        pass

    # Renderizar paginas como PNG a 150 DPI (balance calidad/velocidad)
    try:
        cmd = [PDFTOPPM, "-r", "150", "-png", str(pdf_path), str(images_dir / "page")]
        subprocess.run(cmd, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None, "pdftoppm timeout (>5min)"
    except Exception as e:
        return None, f"pdftoppm error: {e}"

    page_images = sorted(images_dir.glob("page*.png"))
    if not page_images:
        return None, "pdftoppm no genero imagenes"

    if max_pages:
        page_images = page_images[:max_pages]

    ocr_parts = []
    failed_pages = 0

    for i, img_path in enumerate(page_images, 1):
        try:
            r = subprocess.run(
                [TESSERACT, str(img_path), "stdout", "-l", "eng+spa"],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=60, env={**__import__("os").environ, **os_env},
            )
            if r.returncode == 0 and r.stdout.strip():
                ocr_parts.append(f"[Pagina {i}]\n{cleanup_text(r.stdout)}")
            else:
                failed_pages += 1
        except subprocess.TimeoutExpired:
            failed_pages += 1
        except Exception:
            failed_pages += 1

    if not ocr_parts:
        return None, f"OCR no extrajo texto de ninguna de {len(page_images)} paginas"

    full_text = "\n\n".join(ocr_parts)
    note = f"\n\n[OCR: {len(ocr_parts)} paginas procesadas, {failed_pages} fallidas, {len(page_images)} total]"
    return cleanup_text(full_text + note), None

# ── Clasificacion ─────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """Analiza el siguiente articulo academico completo y retorna SOLO un JSON de clasificacion.

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

Valores validos:
- metodos_especifico: M1_LogisticRegression M2_NaiveBayes M3_DecisionTree M4_GradientBoosting M5_KNN M6_SVM M7_NeuralNetwork M8_RandomForest M9_NLP_Traditional M10_DeepLearning M11_LSTM M12_Transformer M13_BERT M14_GraphNetwork M15_Ensemble M16_Clustering M17_TopicModeling M18_SemanticAnalysis M19_SentimentAnalysis M20_StylometryAnalysis M21_HybridMethod
- metodos_general: Machine Learning Deep Learning NLP Computer Vision Graph Analysis Statistical Analysis Linguistic Analysis Network Analysis Knowledge Graphs Ontologies Rule-Based Systems Hybrid Methods Transfer Learning
- metricas: D1_Precision_Recall D2_F1Score D3_Accuracy D4_AUC D5_Confusion_Matrix D6_Matthews_Correlation D7_Cohen_Kappa D8_Mean_Absolute_Error D9_RMSE D10_Silhouette_Score D11_Davies_Bouldin_Index D12_Execution_Time D13_Memory_Usage
- intenciones: I1_FakeNews I2_Manipulation I3_Misinformation I4_Satire I5_Rumors I6_BotActivity I7_EmotionAnalysis I8_PolarityAnalysis I9_ToxicContent I10_Deepfakes I11_Coordinated_Behavior I12_SuspiciousActivity I13_Credibility_Assessment
- plataforma: P1_Twitter P2_Facebook P3_News P4_Reddit P5_Instagram P6_YouTube P7_TikTok P8_Telegram P9_WhatsApp P10_Multiple P11_General
- linguistica: L1_English L2_Spanish L3_Chinese L4_Arabic L5_French L6_German L7_Multilingual L8_NotSpecified
- dataset: lista de nombres de datasets usados
- dataset_info: [{{"nombre": "...", "url": "...", "referencia": "..."}}]
- relevancia_general: float 0.0-1.0
- hallazgos_nuevos: metodos o intenciones NO listados arriba
"""

def classify_article(pdf_id, content):
    if len(content) > MAX_CHARS:
        half = MAX_CHARS // 2
        content = content[:half] + "\n\n[...contenido truncado...]\n\n" + content[-half:]

    prompt = PROMPT_TEMPLATE.format(pdf_id=pdf_id, content=content)

    for intento in range(3):
        try:
            r = subprocess.run(
                [CLAUDE_CMD, "-p", "--model", MODEL],
                input=prompt, capture_output=True,
                text=True, encoding="utf-8", errors="replace",
                timeout=300,
            )
            if r.returncode != 0:
                continue
            out = r.stdout.strip()
            if not out:
                continue
            j_start = out.find("{")
            j_end   = out.rfind("}") + 1
            if j_start >= 0 and j_end > j_start:
                return json.loads(out[j_start:j_end]), None
        except subprocess.TimeoutExpired:
            if intento < 2:
                time.sleep(5)
            continue
        except json.JSONDecodeError as e:
            if intento < 2:
                time.sleep(5)
            continue
        except Exception as e:
            return None, f"Excepcion: {type(e).__name__}: {e}"

    return None, "Claude no respondio tras 3 intentos"

# ── Output JSON (append) ───────────────────────────────────────────────────────
def append_article(clasificacion):
    if Path(OUTPUT_JSON).exists():
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"metadata": {"articulos_clasificados": 0}, "articulos": []}

    data["articulos"].append(clasificacion)
    data["metadata"]["articulos_clasificados"] = len(data["articulos"])
    data["metadata"]["ultima_actualizacion"]   = datetime.now().isoformat()

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_checkpoint(folder_name):
    cp = {}
    if Path(CHECKPOINT).exists():
        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            cp = json.load(f)
    procesados = set(cp.get("procesados", []))
    procesados.add(folder_name)
    cp["procesados"] = list(procesados)
    cp["ultima_actualizacion"] = datetime.now().isoformat()
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(cp, f, ensure_ascii=False, indent=2)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("FASE RECUPERACION: 10 articulos pendientes")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Cargar checkpoint para no reprocesar los que ya esten listos
    cp_procesados = set()
    if Path(CHECKPOINT).exists():
        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            cp_procesados = set(json.load(f).get("procesados", []))

    resultados = []

    for i, (art_id, folder_name, tipo) in enumerate(TARGETS, 1):
        print(f"\n[{i:2d}/10] {art_id} ({tipo.upper()})")

        res = {"id": art_id, "folder": folder_name, "tipo": tipo,
               "extraccion": None, "clasificacion": None, "razon_fallo": None}

        # Saltar si ya esta en el checkpoint
        if folder_name in cp_procesados:
            print(f"  [SKIP] Ya procesado en checkpoint")
            res["extraccion"] = "skip"
            res["clasificacion"] = "skip"
            resultados.append(res)
            continue

        # ── PASO 1: Extraccion ───────────────────────────────────────────────
        extract_subdir = EXTRACT_DIR / folder_name
        extract_subdir.mkdir(parents=True, exist_ok=True)
        content_file = extract_subdir / "content.txt"

        content = None

        if content_file.exists() and content_file.stat().st_size > 100:
            content = content_file.read_text(encoding="utf-8", errors="replace")
            log(art_id, "extraccion", "ok", f"content.txt ya existia ({len(content)} chars)")
            res["extraccion"] = "cached"
        else:
            pdf_path = find_pdf(art_id)
            if not pdf_path:
                msg = f"PDF no encontrado en {PDF_DIR}"
                log(art_id, "extraccion", "fail", msg)
                res["razon_fallo"] = msg
                resultados.append(res)
                continue

            if tipo == "text":
                text = extract_text_pdftotext(pdf_path)
                if text and len(text) > 100:
                    content = text
                    log(art_id, "extraccion", "ok", f"pdftotext: {len(content)} chars")
                    res["extraccion"] = "pdftotext"
                else:
                    # Fallback a OCR si pdftotext no produce nada
                    log(art_id, "extraccion", "fail", "pdftotext no extrajo texto, intentando OCR")
                    content, err = extract_text_ocr(pdf_path, extract_subdir)
                    if content and len(content) > 100:
                        log(art_id, "extraccion", "ok", f"OCR fallback: {len(content)} chars")
                        res["extraccion"] = "ocr_fallback"
                    else:
                        msg = f"pdftotext y OCR fallaron: {err}"
                        log(art_id, "extraccion", "fail", msg)
                        res["razon_fallo"] = msg
                        resultados.append(res)
                        continue

            elif tipo == "ocr":
                pdf_size_mb = pdf_path.stat().st_size / 1024 / 1024
                max_pages = 40 if pdf_size_mb > 10 else None
                if max_pages:
                    print(f"  PDF grande ({pdf_size_mb:.1f}MB), limitando a {max_pages} paginas")

                t0 = time.time()
                content, err = extract_text_ocr(pdf_path, extract_subdir, max_pages=max_pages)
                elapsed = time.time() - t0

                if content and len(content) > 100:
                    log(art_id, "extraccion", "ok",
                        f"OCR: {len(content)} chars en {elapsed:.0f}s")
                    res["extraccion"] = "ocr"
                else:
                    msg = f"OCR no extrajo texto: {err}"
                    log(art_id, "extraccion", "fail", msg)
                    res["razon_fallo"] = msg
                    resultados.append(res)
                    continue

            # Guardar content.txt
            content_file.write_text(content, encoding="utf-8")

        # ── PASO 2: Clasificacion ────────────────────────────────────────────
        print(f"  Clasificando con Claude ({len(content):,} chars)...")
        clasificacion, err = classify_article(folder_name, content)

        if clasificacion:
            try:
                append_article(clasificacion)
                update_checkpoint(folder_name)
                log(art_id, "clasificacion", "ok",
                    f"titulo: {clasificacion.get('titulo','?')[:60]}")
                res["clasificacion"] = "ok"
            except Exception as e:
                msg = f"Error guardando: {e}"
                log(art_id, "clasificacion", "fail", msg)
                res["razon_fallo"] = msg
        else:
            log(art_id, "clasificacion", "fail", err or "sin respuesta")
            res["razon_fallo"] = err

        resultados.append(res)

    # ── Resumen ───────────────────────────────────────────────────────────────
    ok_ext  = [r for r in resultados if r["extraccion"] in ("ok","pdftotext","ocr","ocr_fallback","cached")]
    ok_cls  = [r for r in resultados if r["clasificacion"] == "ok"]
    failed  = [r for r in resultados if r["razon_fallo"]]

    summary = [
        "=" * 70,
        "RESUMEN FASE RECUPERACION",
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        f"Total articulos: {len(TARGETS)}",
        f"Extraccion OK  : {len(ok_ext)}",
        f"Clasificados   : {len(ok_cls)}",
        f"Fallidos       : {len(failed)}",
        "",
    ]

    if ok_cls:
        summary.append("CLASIFICADOS EXITOSAMENTE:")
        for r in ok_cls:
            summary.append(f"  + {r['id']}")
        summary.append("")

    if failed:
        summary.append("FALLIDOS (ver fase_recuperacion_log.json para detalle):")
        for r in failed:
            summary.append(f"  - {r['id']}: {r['razon_fallo'][:80]}")
        summary.append("")

    summary.append("=" * 70)
    summary_text = "\n".join(summary)

    print("\n" + summary_text)
    Path(SUMMARY_FILE).write_text(summary_text, encoding="utf-8")
    print(f"\nResumen guardado en: {SUMMARY_FILE}")
    print(f"Log detallado en  : {LOG_FILE}")

if __name__ == "__main__":
    main()
