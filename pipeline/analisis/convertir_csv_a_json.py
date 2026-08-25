#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte emails_autores_encontrados.csv a formato JSON para la herramienta de correos
"""

import csv
import json
import sys
import io
from pathlib import Path

# Configurar encoding para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("[*] Leyendo emails_autores_encontrados.csv...\n")

articulos = []

try:
    # Intentar diferentes encodings
    encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
    csv_content = None

    for encoding in encodings:
        try:
            with open('emails_autores_encontrados.csv', 'r', encoding=encoding) as f:
                csv_content = f.read()
            print(f"[OK] CSV leido con encoding: {encoding}\n")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if not csv_content:
        raise Exception("No se pudo leer el archivo con ningun encoding")

    # Parsear CSV
    lines = csv_content.splitlines()
    reader = csv.DictReader(lines)

    for i, row in enumerate(reader, 1):
        # Transformar a formato JSON para herramienta de correos
        articulo = {
            'titulo': row.get('titulo', '').strip(),
            'año': int(row.get('año', 2025)) if row.get('año', '').isdigit() else 2025,
            'autor_contacto': row.get('autor', 'Autor Desconocido').strip(),
            'email_autor': row.get('email', '').strip() if row.get('email', '').strip() else 'contacto@ejemplo.com',
            'doi': row.get('doi', 'N/A').strip(),
            'articulo_id': row.get('articulo_id', '').strip()
        }
        articulos.append(articulo)

        if i <= 3:
            print(f"[{i}] {articulo['autor_contacto']} - {articulo['titulo'][:60]}...")
            print(f"    Email: {articulo['email_autor']}\n")

    print(f"\n[OK] Convertidos {len(articulos)} articulos\n")

    # Guardar como JSON
    output_file = 'emails_autores_completo.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articulos, f, ensure_ascii=False, indent=2)

    print(f"[OK] JSON guardado en: {output_file}")
    print(f"\n[*] RESUMEN:")
    print(f"    Total articulos: {len(articulos)}")

    # Contar emails
    con_email = sum(1 for a in articulos if a['email_autor'] != 'contacto@ejemplo.com')
    sin_email = len(articulos) - con_email

    print(f"    Con email: {con_email}")
    print(f"    Sin email (placeholder): {sin_email}")
    print(f"\n[*] Proximo paso:")
    print(f"    1. Completa los emails faltantes en {output_file}")
    print(f"    2. Sube el JSON a la herramienta de correos")
    print(f"    3. Envia las solicitudes de acceso a articulos\n")

except FileNotFoundError:
    print("[ERROR] No se encontro emails_autores_encontrados.csv")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
