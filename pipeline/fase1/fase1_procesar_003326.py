#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intenta procesar articulo_003326 con múltiples estrategias
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import re
import os
import time

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"

PDF_DIR = Path("pdfs")
EXTRACT_DIR = Path("pdfs_extraido")

def cleanup_text(text):
    if not text:
        return ""
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\n+', '\n', text)
    text = '\n'.join(line.strip() for line in text.split('\n'))
    text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t\r')
    return text.strip()

def extract_text_pdftotext(pdf_path, timeout=30):
    """Intenta extracción con timeout configurable"""
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
            stdout, stderr = result.communicate(timeout=timeout)
            if result.returncode == 0 and stdout:
                text = cleanup_text(stdout)
                return text if len(text) > 50 else None  # Reducir threshold
        except subprocess.TimeoutExpired:
            result.kill()
            result.wait()
    except Exception as e:
        print(f"    Error: {e}")
    return None

def extract_ocr_safe(pdf_path, extract_subdir):
    """OCR seguro"""
    try:
        images_dir = extract_subdir / "images"
        images_dir.mkdir(exist_ok=True)

        subprocess.run(
            ["pdfimages", "-png", str(pdf_path), str(images_dir / "img")],
            capture_output=True,
            timeout=15
        )

        ocr_text = ""
        image_files = sorted(images_dir.glob("img*.png"))[:3]

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
                    stdout, stderr = result.communicate(timeout=2)
                    if result.returncode == 0 and stdout and len(stdout.strip()) > 5:
                        ocr_text += "\n" + cleanup_text(stdout)
                except subprocess.TimeoutExpired:
                    result.kill()
                    result.wait()
            except:
                pass

        return cleanup_text(ocr_text) if ocr_text else None
    except:
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
    print("Reintentando: articulo_003326.pdf")
    print("=" * 80)
    print()

    pdf_name = "articulo_003326.pdf"
    pdf_path = PDF_DIR / pdf_name
    pdf_id = pdf_path.stem

    if not pdf_path.exists():
        print(f"ERROR: {pdf_name} no existe")
        return

    print(f"Tamaño: {pdf_path.stat().st_size / 1024:.1f} KB")
    print()

    extract_subdir = EXTRACT_DIR / pdf_id
    extract_subdir.mkdir(exist_ok=True)

    # Estrategia 1: pdftotext normal
    print("Estrategia 1: pdftotext (30s timeout)...", end=" ", flush=True)
    text = extract_text_pdftotext(pdf_path, timeout=30)
    if text:
        print(f"OK ({len(text)} chars)")
    else:
        print("FALLO")

    # Estrategia 2: pdftotext con timeout mayor
    if not text:
        print("Estrategia 2: pdftotext (60s timeout)...", end=" ", flush=True)
        text = extract_text_pdftotext(pdf_path, timeout=60)
        if text:
            print(f"OK ({len(text)} chars)")
        else:
            print("FALLO")

    # Estrategia 3: Sin timeout (puede tardar)
    if not text:
        print("Estrategia 3: pdftotext (sin timeout)...", end=" ", flush=True)
        text = extract_text_pdftotext(pdf_path, timeout=300)
        if text:
            print(f"OK ({len(text)} chars)")
        else:
            print("FALLO")

    if not text:
        print("\n❌ No se pudo extraer texto del PDF")
        return

    # OCR
    print("Extrayendo OCR...", end=" ", flush=True)
    ocr_text = extract_ocr_safe(pdf_path, extract_subdir)
    if ocr_text:
        print(f"OK ({len(ocr_text)} chars)")
    else:
        print("SIN OCR")

    # Guardar
    full_content = text
    if ocr_text and len(ocr_text) > 10:
        full_content += "\n\n" + "="*80 + "\n[OCR]\n" + "="*80 + "\n" + ocr_text

    idioma = detect_language(full_content)

    with open(extract_subdir / "content.txt", 'w', encoding='utf-8') as f:
        f.write(full_content)

    metadata = {
        "pdf_id": pdf_id,
        "fecha_procesamiento": datetime.now().isoformat(),
        "tamaño_bytes": pdf_path.stat().st_size,
        "caracteres_text": len(text),
        "caracteres_ocr": len(ocr_text) if ocr_text else 0,
        "caracteres_totales": len(full_content),
        "idioma": idioma,
        "tiene_ocr": ocr_text is not None and len(ocr_text) > 10,
        "imagenes": len(list((extract_subdir / "images").glob("*.png"))) if (extract_subdir / "images").exists() else 0,
        "estrategia": "Multiple timeouts"
    }

    with open(extract_subdir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("RESULTADO: articulo_003326")
    print("=" * 80)
    print(f"✓ Procesado exitosamente")
    print(f"  Caracteres texto: {len(text)}")
    print(f"  Caracteres OCR: {len(ocr_text) if ocr_text else 0}")
    print(f"  Total: {len(full_content)}")
    print(f"  Idioma: {idioma}")

if __name__ == "__main__":
    main()
