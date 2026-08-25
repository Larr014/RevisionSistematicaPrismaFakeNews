#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exporta articulos_filtrados_elegibilidad.json a formato RIS
"""

import json
import os

INPUT_JSON = r"C:\Users\Luis Rojas\.openclaw\workspace\tablas\15_articulos_filtrados_elegibilidad.json"
OUTPUT_RIS = r"C:\Users\Luis Rojas\.openclaw\workspace\articulos_filtrados_elegibilidad.ris"

print("="*70)
print("EXPORTAR ARTICULOS FILTRADOS A FORMATO RIS")
print("="*70)

# Leer JSON
print("\n[PASO 1] Leyendo JSON...")
with open(INPUT_JSON, 'r', encoding='utf-8') as f:
    datos = json.load(f)

articulos = datos.get("articulos", [])
print(f"  OK: {len(articulos)} articulos cargados")

# Exportar a RIS
print("\n[PASO 2] Exportando a RIS...")

ris_content = ""

for art in articulos:
    ris_content += "TY  - JOUR\n"  # Tipo: Journal Article (asumido)

    if art.get('titulo'):
        ris_content += f"TI  - {art['titulo']}\n"

    for autor in art.get('autores', []):
        ris_content += f"AU  - {autor}\n"

    if art.get('year'):
        ris_content += f"PY  - {art['year']}\n"

    if art.get('doi'):
        ris_content += f"DO  - {art['doi']}\n"

    # Agregar campos personalizados para metadatos de clasificacion
    metodos = ", ".join(art.get('metodos', []))
    if metodos:
        ris_content += f"KW  - METODOS: {metodos}\n"

    intenciones = ", ".join(art.get('intenciones', []))
    if intenciones:
        ris_content += f"KW  - INTENCIONES: {intenciones}\n"

    if art.get('relevancia'):
        ris_content += f"KW  - RELEVANCIA: {art['relevancia']}\n"

    ris_content += f"ID  - {art['articulo_id']}\n"
    ris_content += "ER  -\n\n"

# Guardar RIS
with open(OUTPUT_RIS, 'w', encoding='utf-8') as f:
    f.write(ris_content)

tamanio_kb = os.path.getsize(OUTPUT_RIS) / 1024

print(f"\n[PASO 3] Resultado:")
print(f"  OK: {len(articulos)} articulos exportados")
print(f"  Archivo: {OUTPUT_RIS}")
print(f"  Tamanio: {tamanio_kb:.1f} KB")
print("\n" + "="*70 + "\n")
