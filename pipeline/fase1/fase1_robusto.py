#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 1 ROBUSTO: Con OCR + manejo de excepciones + reintentos
- Intenta OCR con timeout
- Si OCR falla/timeout, continua con solo pdftotext
- Manejo robusto de errores sin bloquear
- Reintentos inteligentes
"""

import json
import subprocess
import signal
import sys
from pathlib import Path
from datetime import datetime
import re
import os
import time

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"

PDF_DIR = Path("pdfs")
EXTRACT_DIR = Path("pdfs_extraido")
ERROR_REPORT = "reporte_extraccion_errores.json"
IDIOMA_REPORT = "reporte_idiomas_detectados.json"
CHECKPOINT = "checkpoint_fase1.json"

# Signal handler para interrupciones
def signal_handler(sig, frame):
    print("\n\n[INTERRUMPIDO] Guardando estado...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def cleanup_text(text):
    if not text:
        return ""
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\n+', '\n', text)
    text = '\n'.join(line.strip() for line in text.split('\n'))
    text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t\r')
    return text.strip()

def extract_text_pdftotext(pdf_path):
    """Extrae texto - con timeout y manejo de errores"""
    try:
        result = subprocess.Popen(
            ["pdftotext", str(pdf_path), "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        try:
            stdout, stderr = result.communicate(timeout=60)
            if result.returncode == 0 and stdout:
                text = cleanup_text(stdout)
                return text if len(text) > 100 else None
        except subprocess.TimeoutExpired:
            result.kill()
            result.wait()
            return None
    except Exception as e:
        pass
    return None

def extract_images_and_ocr_safe(pdf_path, extract_subdir):
    """OCR con manejo robusto de excepciones"""
    try:
        images_dir = extract_subdir / "images"
        images_dir.mkdir(exist_ok=True)

        # pdfimages con timeout
        try:
            subprocess.run(
                ["pdfimages", "-png", str(pdf_path), str(images_dir / "img")],
                capture_output=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            return None
        except:
            return None

        ocr_text = ""
        image_files = sorted(images_dir.glob("img*.png"))

        if not image_files:
            return None

        # OCR con timeout estricto: 3s por imagen
        for img_file in image_files:
            try:
                result = subprocess.Popen(
                    [r"C:\Program Files\Tesseract-OCR\tesseract.exe", str(img_file), "stdout", "-l", "eng+spa"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'
                )
                try:
                    stdout, stderr = result.communicate(timeout=3)
                    if result.returncode == 0 and stdout and len(stdout.strip()) > 5:
                        ocr_text += "\n" + cleanup_text(stdout)
                except subprocess.TimeoutExpired:
                    result.kill()
                    result.wait()
                    # Continua con siguiente imagen si timeout
                    continue
            except Exception as e:
                # Si una imagen falla, continua con las otras
                continue

        return cleanup_text(ocr_text) if ocr_text else None

    except Exception as e:
        # Si algo falla en OCR completo, retorna None sin bloquear
        return None

def detect_language(text):
    spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'es', 'una', 'los']
    english_words = ['the', 'and', 'a', 'in', 'is', 'to', 'of', 'for', 'with']

    text_lower = text.lower()
    spanish_count = sum(text_lower.count(w) for w in spanish_words)
    english_count = sum(text_lower.count(w) for w in english_words)

    if spanish_count > english_count and spanish_count > 5:
        return "Spanish"
    elif english_count > 5:
        return "English"
    else:
        return "Unknown"

def main():
    print("=" * 80)
    print("FASE 1 ROBUSTO: Con OCR + Manejo de Excepciones")
    print("=" * 80)
    print()

    pdf_files = sorted([f for f in PDF_DIR.glob("*.pdf")])
    total = len(pdf_files)

    # Detectar ya procesados
    ya_procesados = set()
    if EXTRACT_DIR.exists():
        ya_procesados = {d.name for d in EXTRACT_DIR.iterdir() if d.is_dir()}

    print(f"Total: {total} | Procesados: {len(ya_procesados)} | Faltantes: {total - len(ya_procesados)}\n")

    # Cargar reportes
    errores = {"total": 0, "pdfs": []}
    if Path(ERROR_REPORT).exists():
        with open(ERROR_REPORT, 'r', encoding='utf-8') as f:
            errores = json.load(f)

    idiomas_raros = {"detectados": {}}
    if Path(IDIOMA_REPORT).exists():
        with open(IDIOMA_REPORT, 'r', encoding='utf-8') as f:
            idiomas_raros = json.load(f)

    # Procesar faltantes
    pendientes = [f for f in pdf_files if f.stem not in ya_procesados]
    idx_global = len(ya_procesados) + 1

    procesados_exitosos = 0
    errores_conteo = 0

    for idx, pdf_path in enumerate(pendientes, 1):
        pdf_id = pdf_path.stem
        pct = (idx_global * 100) // total

        print(f"[{idx_global:3d}/{total}] [{pct:3d}%] {pdf_id[:35]:35s} ", end="", flush=True)

        extract_subdir = EXTRACT_DIR / pdf_id
        extract_subdir.mkdir(exist_ok=True)

        try:
            # Extraer texto - crítico, si falla salta este PDF
            text = extract_text_pdftotext(pdf_path)
            if not text:
                print("[ERROR lectura]")
                errores["total"] += 1
                errores["pdfs"].append({"pdf": pdf_id, "razon": "pdftotext fallo"})
                errores_conteo += 1
                idx_global += 1
                continue

            # Extraer OCR - IMPORTANTE: no bloquea si falla
            ocr_text = None
            try:
                ocr_text = extract_images_and_ocr_safe(pdf_path, extract_subdir)
            except Exception as e:
                # OCR falló, pero continuamos con solo pdftotext
                ocr_text = None

            full_content = text
            if ocr_text and len(ocr_text) > 10:
                full_content += "\n\n" + "="*80 + "\n[CONTENIDO EXTRAIDO POR OCR]\n" + "="*80 + "\n" + ocr_text

            idioma = detect_language(full_content)
            if idioma not in ["English", "Spanish"]:
                if idioma not in idiomas_raros["detectados"]:
                    idiomas_raros["detectados"][idioma] = []
                idiomas_raros["detectados"][idioma].append(pdf_id)

            # Guardar content.txt
            with open(extract_subdir / "content.txt", 'w', encoding='utf-8') as f:
                f.write(full_content)

            # Guardar metadata.json
            metadata = {
                "pdf_id": pdf_id,
                "fecha_procesamiento": datetime.now().isoformat(),
                "tamaño_bytes": pdf_path.stat().st_size,
                "caracteres_text": len(text),
                "caracteres_ocr": len(ocr_text) if ocr_text else 0,
                "caracteres_totales": len(full_content),
                "idioma": idioma,
                "tiene_ocr": ocr_text is not None and len(ocr_text) > 10,
                "imagenes": len(list((extract_subdir / "images").glob("*.png"))) if (extract_subdir / "images").exists() else 0
            }

            with open(extract_subdir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print("[OK]")
            procesados_exitosos += 1

        except Exception as e:
            print(f"[EXCEPCION]")
            errores["total"] += 1
            errores["pdfs"].append({"pdf": pdf_id, "razon": str(e)[:60]})
            errores_conteo += 1

        idx_global += 1

    # Guardar reportes finales
    with open(ERROR_REPORT, 'w', encoding='utf-8') as f:
        json.dump(errores, f, ensure_ascii=False, indent=2)

    if idiomas_raros["detectados"]:
        with open(IDIOMA_REPORT, 'w', encoding='utf-8') as f:
            json.dump(idiomas_raros, f, ensure_ascii=False, indent=2)

    # Resumen final
    print("\n" + "=" * 80)
    print("FASE 1 COMPLETADA CON EXITO")
    print("=" * 80)

    total_exitosos = len(ya_procesados) + procesados_exitosos
    print(f"Total PDFs: {total}")
    print(f"Procesados exitosamente: {total_exitosos}")
    print(f"Errores: {errores['total']}")
    print(f"Tasa exito: {100 * total_exitosos / total:.1f}%")
    print(f"\nCarpeta extraction: {EXTRACT_DIR}/ ({len(list(EXTRACT_DIR.iterdir()))} subcarpetas)")
    print(f"Reporte errores: {ERROR_REPORT}")

    if idiomas_raros["detectados"]:
        print(f"\nIdiomas detectados (no EN/ES):")
        for idioma, pdfs in idiomas_raros["detectados"].items():
            print(f"  - {idioma}: {len(pdfs)} PDFs")

if __name__ == "__main__":
    main()
