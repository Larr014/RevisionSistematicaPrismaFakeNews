#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 1: EXTRACCION DE CONTENIDO DE 549 PDFs
Basado en código que funciona del test
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil
import re
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"

PDF_DIR = Path("pdfs")
EXTRACT_DIR = Path("pdfs_extraido")
ERROR_REPORT = "reporte_extraccion_errores.json"
IDIOMA_REPORT = "reporte_idiomas_detectados.json"

def cleanup_text(text):
    """Limpia y normaliza"""
    if not text:
        return ""
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\n+', '\n', text)
    text = '\n'.join(line.strip() for line in text.split('\n'))
    text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t\r')
    return text.strip()

def extract_text_pdftotext(pdf_path):
    """Extrae TODO el texto - COPIA DE TEST QUE FUNCIONA"""
    try:
        result = subprocess.Popen(
            ["pdftotext", str(pdf_path), "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        stdout, stderr = result.communicate(timeout=60)

        if result.returncode == 0 and stdout:
            text = cleanup_text(stdout)
            return text if len(text) > 100 else None
    except:
        pass

    return None

def extract_images_and_ocr(pdf_path, extract_subdir):
    """Extrae imágenes y OCR - COPIA DE TEST QUE FUNCIONA"""
    try:
        images_dir = extract_subdir / "images"
        images_dir.mkdir(exist_ok=True)

        # pdfimages
        subprocess.run(
            ["pdfimages", "-png", str(pdf_path), str(images_dir / "img")],
            capture_output=True,
            timeout=60
        )

        # OCR
        ocr_text = ""
        image_files = sorted(images_dir.glob("img*.png"))

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
                stdout, stderr = result.communicate(timeout=30)

                if result.returncode == 0 and stdout:
                    ocr_text += "\n" + cleanup_text(stdout)
            except:
                pass

        return cleanup_text(ocr_text) if ocr_text else None

    except:
        pass

    return None

def detect_language(text):
    """Detecta idioma"""
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
    print("FASE 1: EXTRACCION DE CONTENIDO DE 549 PDFs")
    print("=" * 80)
    print()

    # Limpiar carpeta
    if EXTRACT_DIR.exists():
        print(f"Eliminando carpeta: {EXTRACT_DIR}")
        shutil.rmtree(EXTRACT_DIR)

    EXTRACT_DIR.mkdir()
    print(f"Carpeta creada: {EXTRACT_DIR}\n")

    pdf_files = sorted([f for f in PDF_DIR.glob("*.pdf")])
    total = len(pdf_files)

    errores = {"total": 0, "pdfs": []}
    idiomas_raros = {"detectados": {}}

    for idx, pdf_path in enumerate(pdf_files, 1):
        pdf_id = pdf_path.stem
        pct = (idx * 100) // total

        print(f"[{idx:3d}/{total}] [{pct:3d}%] {pdf_id[:35]:35s} ", end="", flush=True)

        extract_subdir = EXTRACT_DIR / pdf_id
        extract_subdir.mkdir(exist_ok=True)

        try:
            # Extraer texto
            text = extract_text_pdftotext(pdf_path)
            if not text:
                print("[ERROR lectura]")
                errores["total"] += 1
                errores["pdfs"].append({
                    "pdf": pdf_id,
                    "razon": "pdftotext fallo o sin contenido"
                })
                continue

            # Extraer OCR
            ocr_text = extract_images_and_ocr(pdf_path, extract_subdir)

            # Combinar
            full_content = text
            if ocr_text:
                full_content += "\n\n" + "="*80 + "\n[OCR]\n" + "="*80 + "\n" + ocr_text

            # Idioma
            idioma = detect_language(full_content)
            if idioma not in ["English", "Spanish"]:
                if idioma not in idiomas_raros["detectados"]:
                    idiomas_raros["detectados"][idioma] = []
                idiomas_raros["detectados"][idioma].append(pdf_id)

            # Guardar content.txt
            content_file = extract_subdir / "content.txt"
            with open(content_file, 'w', encoding='utf-8') as f:
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
                "tiene_ocr": ocr_text is not None and len(ocr_text) > 0,
                "imagenes": len(list((extract_subdir / "images").glob("*.png"))) if (extract_subdir / "images").exists() else 0
            }

            metadata_file = extract_subdir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print("[OK]")

        except Exception as e:
            print(f"[ERROR {str(e)[:20]}]")
            errores["total"] += 1
            errores["pdfs"].append({
                "pdf": pdf_id,
                "razon": str(e)[:80]
            })

    # Guardar reportes
    if errores["total"] > 0:
        with open(ERROR_REPORT, 'w', encoding='utf-8') as f:
            json.dump(errores, f, ensure_ascii=False, indent=2)

    if idiomas_raros["detectados"]:
        with open(IDIOMA_REPORT, 'w', encoding='utf-8') as f:
            json.dump(idiomas_raros, f, ensure_ascii=False, indent=2)

    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN FASE 1")
    print("=" * 80)
    print(f"Total: {total}")
    print(f"Exitosos: {total - errores['total']}")
    print(f"Errores: {errores['total']}")
    print(f"Tasa exito: {100 * (total - errores['total']) / total:.1f}%")
    print(f"\nCarpeta: {EXTRACT_DIR}/")

    if errores["total"] > 0:
        print(f"Reporte errores: {ERROR_REPORT}")

    if idiomas_raros["detectados"]:
        print(f"Idiomas detectados: {IDIOMA_REPORT}")
        for idioma, pdfs in idiomas_raros["detectados"].items():
            print(f"  - {idioma}: {len(pdfs)}")

    print("\nFASE 1 COMPLETADA")

if __name__ == "__main__":
    main()
