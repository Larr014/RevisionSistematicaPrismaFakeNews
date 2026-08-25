#!/usr/bin/env python3
import json
import re
from pathlib import Path

pdf_dir = Path("pdfs")

# Encontrar todos los PDFs
pdf_files = list(pdf_dir.glob("*.pdf"))
pdf_ids = {}

for pdf in sorted(pdf_files):
    match = re.search(r'articulo_(\d+)', pdf.name)
    if match:
        art_id = f"articulo_{int(match.group(1)):06d}"
        pdf_ids[art_id] = pdf.stat().st_size

# Cargar datos originales
try:
    with open("articulos_filtrados_elegibilidad.ris", 'r', encoding='utf-8') as f:
        articulos_originales = {}
        current = {}
        for line in f:
            line = line.strip()
            if line.startswith("TI  - "):
                current['titulo'] = line.replace("TI  - ", "")
            elif line.startswith("ID  - "):
                current['id'] = line.replace("ID  - ", "")
            elif line == "ER  -":
                if 'id' in current:
                    articulos_originales[current['id']] = current
                current = {}
except FileNotFoundError:
    print("[ERROR] No se encuentra articulos_filtrados_elegibilidad.ris")
    exit(1)

# Calcular estado
descargados = {art_id: articulos_originales.get(art_id, {}) for art_id in pdf_ids}
pendientes_ids = set(articulos_originales.keys()) - set(pdf_ids.keys())

print("\n" + "="*70)
print("ESTADO COMPLETO DE DESCARGAS")
print("="*70)

print(f"\nTotal elegibles: {len(articulos_originales)}")
print(f"Descargados: {len(pdf_ids)} ({len(pdf_ids)/len(articulos_originales)*100:.1f}%)")
print(f"Pendientes: {len(pendientes_ids)} ({len(pendientes_ids)/len(articulos_originales)*100:.1f}%)")

print(f"\n[DESCARGADOS - {len(pdf_ids)} artículos]")
for i, (art_id, size) in enumerate(sorted(pdf_ids.items())[:10], 1):
    art = descargados.get(art_id, {})
    titulo = art.get('titulo', 'N/A')[:50]
    tamaño_mb = size / (1024*1024)
    print(f"  {i}. {art_id}: {titulo}... ({tamaño_mb:.1f} MB)")

if len(pdf_ids) > 10:
    print(f"  ... y {len(pdf_ids) - 10} más")

print(f"\n[PENDIENTES - {len(pendientes_ids)} artículos]")
pendientes_list = sorted(pendientes_ids)
for i, art_id in enumerate(pendientes_list[:5], 1):
    art = articulos_originales.get(art_id, {})
    titulo = art.get('titulo', 'N/A')[:50]
    print(f"  {i}. {art_id}: {titulo}...")

if len(pendientes_ids) > 5:
    print(f"  ... y {len(pendientes_ids) - 5} más")

print("\n" + "="*70)
