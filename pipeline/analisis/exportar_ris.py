#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exporta referencias de articulos filtrados en formato RIS
Para los 643 articulos seleccionados por criterios de elegibilidad
"""

import json
import os

INPUT_FILE = r"C:\Users\Luis Rojas\.openclaw\workspace\tablas\15_articulos_filtrados_elegibilidad.json"
OUTPUT_DIR = r"C:\Users\Luis Rojas\.openclaw\workspace"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "articulos_filtrados.ris")

print("="*70)
print("EXPORTANDO REFERENCIAS EN FORMATO RIS")
print("="*70)

# Leer articulos filtrados
print("\n[1/3] Leyendo articulos filtrados...")
try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    articulos = data.get("articulos", [])
    print(f"  OK: {len(articulos)} articulos cargados")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

# Generar RIS
print("\n[2/3] Convirtiendo a formato RIS...")

ris_content = []

for idx, art in enumerate(articulos, 1):
    ris_record = []

    # Tipo de documento (asumiendo journal articles)
    ris_record.append("TY  - JOUR")

    # Titulo
    if art.get("titulo"):
        ris_record.append(f"TI  - {art['titulo']}")

    # Autores
    for author in art.get("autores", []):
        ris_record.append(f"AU  - {author}")

    # Ano
    if art.get("year"):
        ris_record.append(f"DA  - {art['year']}/01/01/")
        ris_record.append(f"PY  - {art['year']}")

    # DOI
    if art.get("doi"):
        ris_record.append(f"DO  - {art['doi']}")

    # ID del articulo (como referencia interna)
    ris_record.append(f"ID  - {art.get('articulo_id', '')}")

    # Relevancia como notas personalizadas
    relevancia = art.get("relevancia", 0)
    ris_record.append(f"N1  - Relevancia: {relevancia}")

    # Metodos detectados
    if art.get("metodos"):
        metodos_str = "; ".join(art["metodos"])
        ris_record.append(f"N2  - Metodos: {metodos_str}")

    # Intenciones detectadas
    if art.get("intenciones"):
        intenciones_str = "; ".join(art["intenciones"])
        ris_record.append(f"N3  - Intenciones: {intenciones_str}")

    # Marcador de fin de registro
    ris_record.append("ER  - ")

    ris_content.append("\n".join(ris_record))

# Escribir archivo RIS
print(f"  Convirtiendo {len(articulos)} articulos...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(ris_content))

print(f"  OK: Archivo RIS generado")

# Estadisticas
print("\n[3/3] Resumen:")
print("="*70)
print(f"Archivo guardado:     {OUTPUT_FILE}")
print(f"Articulos exportados: {len(articulos)}")
print(f"Tamaño archivo:       {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")
print("="*70)

print("\nFormato RIS - Campos incluidos:")
print("  TY   - Tipo (JOUR = Journal Article)")
print("  TI   - Titulo del articulo")
print("  AU   - Autores (uno por linea)")
print("  DA   - Fecha de publicacion")
print("  PY   - Ano de publicacion")
print("  DO   - DOI")
print("  ID   - Identificador interno")
print("  N1   - Relevancia (metrica interna)")
print("  N2   - Metodos NLP/ML detectados")
print("  N3   - Intenciones comunicativas detectadas")
print("  ER   - Fin de registro")

print("\nSe puede importar en:")
print("  - Zotero (Import -> RIS)")
print("  - Mendeley (File -> Import)")
print("  - Endnote")
print("  - RefWorks")
print("  - Cualquier gestor bibliografico compatible")

print("\n[OK] Proceso completado exitosamente\n")
