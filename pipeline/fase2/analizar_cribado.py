#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza el proceso de cribado (screening) documentado en clasificacion_articulos.json
Genera informe detallado para la sección de PRISMA
"""

import json
from collections import defaultdict, Counter
import os

INPUT_FILE = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_articulos.json"
OUTPUT_DIR = r"C:\Users\Luis Rojas\.openclaw\workspace\tablas"

print("="*70)
print("ANALISIS DEL CRIBADO (SCREENING) - REVISIÓN SISTEMÁTICA PRISMA")
print("="*70)

# Leer datos
print("\n[PASO 1] Leyendo clasificacion_articulos.json...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

articulos = data.get("articulos", [])
total = len(articulos)

print(f"  OK: {total} articulos cargados")

# Analizar criterios de cribado
print("\n[PASO 2] Analizando criterios de cribado...")

# Criterio 1: Presencia de abstract
con_abstract = sum(1 for a in articulos if a.get("abstract"))
sin_abstract = total - con_abstract
pct_abstract = con_abstract * 100 / total

print(f"\n  1. Presencia de Abstract (metadata completa):")
print(f"     - CON abstract: {con_abstract} ({pct_abstract:.1f}%)")
print(f"     - SIN abstract: {sin_abstract} ({100-pct_abstract:.1f}%)")

# Criterio 2: Año de publicación
years_data = [a.get("year") for a in articulos if a.get("year")]
if years_data:
    min_year = min(years_data)
    max_year = max(years_data)
    print(f"\n  2. Rango de años cubiertos:")
    print(f"     - Periodo: {min_year}-{max_year}")

    # Distribución por año
    year_counts = Counter(years_data)
    print(f"     - Años representados: {len(year_counts)}")
    print(f"     - Años con mayor cobertura: {sorted(year_counts.items(), key=lambda x: -x[1])[:5]}")

# Criterio 3: Relevancia general (métrica clave)
relevancia_scores = [a.get("relevancia_general", 0) for a in articulos]
relevancia_distribucion = {
    "muy_baja (0.0-0.1)": sum(1 for r in relevancia_scores if r <= 0.1),
    "baja (0.1-0.4)": sum(1 for r in relevancia_scores if 0.1 < r <= 0.4),
    "media (0.4-0.7)": sum(1 for r in relevancia_scores if 0.4 < r <= 0.7),
    "alta (0.7-1.0)": sum(1 for r in relevancia_scores if r > 0.7)
}

print(f"\n  3. Distribucion de RELEVANCIA (criterio principal de cribado):")
for nivel, count in relevancia_distribucion.items():
    pct = count * 100 / total
    print(f"     - {nivel:20s}: {count:5d} ({pct:5.1f}%)")

relevancia_promedio = sum(relevancia_scores) / len(relevancia_scores)
print(f"     - Relevancia PROMEDIO: {relevancia_promedio:.2f}")

# Criterio 4: Presencia de métodos
con_metodos = sum(1 for a in articulos if a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", []))
sin_metodos = total - con_metodos

print(f"\n  4. Presencia de METODOS identificados:")
print(f"     - CON metodos: {con_metodos} ({con_metodos*100/total:.1f}%)")
print(f"     - SIN metodos: {sin_metodos} ({sin_metodos*100/total:.1f}%)")

# Criterio 5: Presencia de intenciones
con_intenciones = sum(1 for a in articulos if a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", []))
sin_intenciones = total - con_intenciones

print(f"\n  5. Presencia de INTENCIONES identificadas:")
print(f"     - CON intenciones: {con_intenciones} ({con_intenciones*100/total:.1f}%)")
print(f"     - SIN intenciones: {sin_intenciones} ({sin_intenciones*100/total:.1f}%)")

# DECISIÓN DE CRIBADO (Relevancia >= 0.4 como umbral mínimo)
print("\n" + "="*70)
print("[PASO 3] DECISIÓN DE CRIBADO")
print("="*70)

UMBRAL_RELEVANCIA = 0.4
articulos_incluidos = [a for a in articulos if a.get("relevancia_general", 0) >= UMBRAL_RELEVANCIA]
articulos_excluidos = [a for a in articulos if a.get("relevancia_general", 0) < UMBRAL_RELEVANCIA]

incluidos_count = len(articulos_incluidos)
excluidos_count = len(articulos_excluidos)

print(f"\nCRITERIO: Relevancia >= {UMBRAL_RELEVANCIA}")
print(f"  INCLUIDOS (relevancia alta):   {incluidos_count:4d} ({incluidos_count*100/total:5.1f}%)")
print(f"  EXCLUIDOS (relevancia baja):   {excluidos_count:4d} ({excluidos_count*100/total:5.1f}%)")

# Análisis de excluidos por razón
print(f"\nDESTRIBUCION DE ARTICULOS EXCLUIDOS (n={excluidos_count}):")

excluidos_por_razon = {
    "Sin abstract/metadata": sum(1 for a in articulos_excluidos if not a.get("abstract")),
    "Sin metodos ni intenciones": sum(1 for a in articulos_excluidos
        if not a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
        and not a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])),
    "NLP/ML generico (sin intenciones especificas)": sum(1 for a in articulos_excluidos
        if a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
        and not a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])),
    "Intenciones pero sin contexto digital/NLP": sum(1 for a in articulos_excluidos
        if not a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
        and a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])),
}

for razon, count in excluidos_por_razon.items():
    if count > 0:
        pct = count * 100 / excluidos_count
        print(f"  - {razon:50s}: {count:4d} ({pct:5.1f}%)")

# Análisis de incluidos
print(f"\nCARACTERISTICAS DE ARTICULOS INCLUIDOS (n={incluidos_count}):")

if incluidos_count > 0:
    incluidos_con_metodos = sum(1 for a in articulos_incluidos
        if a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", []))
    incluidos_con_intenciones = sum(1 for a in articulos_incluidos
        if a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", []))
    incluidos_ambos = sum(1 for a in articulos_incluidos
        if a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
        and a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", []))

    print(f"  - CON metodos:      {incluidos_con_metodos:4d} ({incluidos_con_metodos*100/incluidos_count:5.1f}%)")
    print(f"  - CON intenciones:  {incluidos_con_intenciones:4d} ({incluidos_con_intenciones*100/incluidos_count:5.1f}%)")
    print(f"  - CON ambos:        {incluidos_ambos:4d} ({incluidos_ambos*100/incluidos_count:5.1f}%)")
else:
    incluidos_con_metodos = 0
    incluidos_con_intenciones = 0
    incluidos_ambos = 0
    print(f"  - CON metodos:      {0:4d} (N/A)")
    print(f"  - CON intenciones:  {0:4d} (N/A)")
    print(f"  - CON ambos:        {0:4d} (N/A)")

# Generar tabla de cribado para JSON
print("\n" + "="*70)
print("[PASO 4] Generando archivos de salida...")
print("="*70)

# Archivo 1: Resumen ejecutivo del cribado
cribado_resumen = {
    "tipo": "cribado_ejecutivo",
    "fecha_generacion": "2026-05-04",
    "titulo": "Etapa 1: Screening de Titulos y Abstracts",
    "protocolo": "PRISMA 2020",
    "estadisticas_globales": {
        "total_registros_iniciales": total,
        "criterios_inclusion": [
            "Presencia de titulo en metadata RIS",
            "Articulo con relevancia >= 0.4 (sobre analisis de contenido digital, NLP, o intenciones)",
            "Posee abstract para posteriori revision de texto completo"
        ],
        "criterios_exclusion": [
            "Relevancia < 0.4",
            "Falta de titulo o metadata basica"
        ]
    },
    "resultados_cribado": {
        "total_procesados": total,
        "incluidos": incluidos_count,
        "excluidos": excluidos_count,
        "inclusion_rate_pct": round(incluidos_count * 100 / total, 1)
    },
    "metricas_calidad": {
        "articulos_con_abstract": con_abstract,
        "articulos_con_abstract_pct": round(con_abstract * 100 / total, 1),
        "articulos_con_metodos": con_metodos,
        "articulos_con_metodos_pct": round(con_metodos * 100 / total, 1),
        "articulos_con_intenciones": con_intenciones,
        "articulos_con_intenciones_pct": round(con_intenciones * 100 / total, 1),
        "relevancia_promedio": round(relevancia_promedio, 2),
        "relevancia_min": round(min(relevancia_scores), 2),
        "relevancia_max": round(max(relevancia_scores), 2)
    },
    "distribucion_relevancia": {
        "muy_baja_0_0_a_0_1": relevancia_distribucion["muy_baja (0.0-0.1)"],
        "baja_0_1_a_0_4": relevancia_distribucion["baja (0.1-0.4)"],
        "media_0_4_a_0_7": relevancia_distribucion["media (0.4-0.7)"],
        "alta_0_7_a_1_0": relevancia_distribucion["alta (0.7-1.0)"]
    },
    "años_cubiertos": {
        "min": min_year if years_data else None,
        "max": max_year if years_data else None,
        "cantidad_unica": len(year_counts) if years_data else 0
    }
}

with open(os.path.join(OUTPUT_DIR, "12_cribado_screening.json"), "w", encoding="utf-8") as f:
    json.dump(cribado_resumen, f, indent=2, ensure_ascii=False)

print(f"  [OK] 12_cribado_screening.json")

# Archivo 2: Lista de articulos INCLUIDOS para siguiente etapa
articulos_incluidos_lista = {
    "tipo": "articulos_incluidos_cribado",
    "fecha_generacion": "2026-05-04",
    "etapa": "Para buscar texto completo y revision de elegibilidad",
    "total": incluidos_count,
    "articulos": [
        {
            "articulo_id": a["id"],
            "titulo": a["titulo"],
            "autores": a.get("autores", []),
            "year": a.get("year"),
            "doi": a.get("doi"),
            "relevancia": a["relevancia_general"],
            "metodos_detectados": a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", []),
            "intenciones_detectadas": a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])
        }
        for a in sorted(articulos_incluidos, key=lambda x: -x.get("relevancia_general", 0))
    ]
}

with open(os.path.join(OUTPUT_DIR, "13_articulos_incluidos.json"), "w", encoding="utf-8") as f:
    json.dump(articulos_incluidos_lista, f, indent=2, ensure_ascii=False)

print(f"  [OK] 13_articulos_incluidos.json ({incluidos_count} articulos)")

# Archivo 3: Lista de articulos EXCLUIDOS con justificación
articulos_excluidos_lista = {
    "tipo": "articulos_excluidos_cribado",
    "fecha_generacion": "2026-05-04",
    "etapa": "Screening rechazados por baja relevancia",
    "total": excluidos_count,
    "razon_exclusion": "Relevancia < 0.7 segun evaluacion de Claude",
    "articulos": [
        {
            "articulo_id": a["id"],
            "titulo": a["titulo"],
            "year": a.get("year"),
            "doi": a.get("doi"),
            "relevancia": a["relevancia_general"],
            "metodos_detectados": a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", []),
            "intenciones_detectadas": a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", []),
            "razon_probable": (
                "Sin metodos ni intenciones" if (
                    not a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
                    and not a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])
                ) else (
                    "NLP generico sin intenciones especificas" if (
                        a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
                        and not a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])
                    ) else (
                        "Intenciones sin contexto digital/NLP" if (
                            not a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
                            and a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])
                        ) else "Baja relevancia"
                    )
                )
            )
        }
        for a in sorted(articulos_excluidos, key=lambda x: -x.get("relevancia_general", 0))[:100]  # Top 100 excluidos
    ]
}

with open(os.path.join(OUTPUT_DIR, "14_articulos_excluidos_muestra.json"), "w", encoding="utf-8") as f:
    json.dump(articulos_excluidos_lista, f, indent=2, ensure_ascii=False)

print(f"  [OK] 14_articulos_excluidos_muestra.json (Top 100 de {excluidos_count})")

# Resumen final
print("\n" + "="*70)
print("RESUMEN DEL CRIBADO (SCREENING)")
print("="*70)
print(f"\nFlujo PRISMA:")
print(f"  Registros identificados:         {total:6d}")
print(f"  [1] CON abstract:                 {con_abstract:6d} ({pct_abstract:.1f}%)")
print(f"  [2] SIN abstract:                 {sin_abstract:6d} ({100-pct_abstract:.1f}%)")
print(f"\n  Registros evaluados (screening): {total:6d}")
print(f"  [3] INCLUIDOS (relevancia>=0.4):  {incluidos_count:6d} ({incluidos_count*100/total:.1f}%)")
print(f"  [4] EXCLUIDOS (relevancia<0.4):   {excluidos_count:6d} ({excluidos_count*100/total:.1f}%)")
print(f"\n  Para buscar texto completo:      {incluidos_count:6d}")
print(f"  [5] CON metodos Y intenciones:    {incluidos_ambos:6d}")
print(f"  [6] Solo CON metodos:             {incluidos_con_metodos - incluidos_ambos:6d}")
print(f"  [7] Solo CON intenciones:         {incluidos_con_intenciones - incluidos_ambos:6d}")

print("\n" + "="*70)
print("[OK] Analisis completado")
print("="*70 + "\n")
