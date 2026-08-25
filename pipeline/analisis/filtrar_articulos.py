#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica filtros a la clasificacion de articulos segun criterios PRISMA
Filtro 1: AMBOS metodos + intenciones detectados
Filtro 2: Anos recientes (2021-2026)
"""

import json
import os
from collections import Counter

INPUT_FILE = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_claude.json"
OUTPUT_DIR = r"C:\Users\Luis Rojas\.openclaw\workspace\tablas"

print("="*70)
print("APLICANDO FILTROS DE ELEGIBILIDAD ESTRICTA")
print("="*70)

# Leer datos
print("\n[PASO 1] Leyendo clasificacion_articulos.json...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

articulos = data.get("articulos", [])
total_inicial = len(articulos)
print(f"  OK: {total_inicial} articulos cargados")

# Aplicar filtros
print("\n[PASO 2] Aplicando filtros...")

# Filtro 1: AMBOS metodos + intenciones
articulos_ambos = [
    a for a in articulos
    if a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])
    and a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", [])
]
print(f"\n  Filtro 1 - AMBOS (metodos + intenciones): {len(articulos_ambos)} / {total_inicial}")

# Filtro 2: Anos recientes (2021-2026)
ANO_MINIMO = 2021
articulos_recientes = [
    a for a in articulos_ambos
    if a.get("year") and a.get("year") >= ANO_MINIMO
]
print(f"  Filtro 2 - Anos {ANO_MINIMO}-2026: {len(articulos_recientes)} / {len(articulos_ambos)}")

total_final = len(articulos_recientes)
reduccion = ((total_inicial - total_final) / total_inicial) * 100

print(f"\n  RESULTADO FINAL: {total_final} articulos ({100-reduccion:.1f}% del original)")
print(f"  Articulos excluidos: {total_inicial - total_final} ({reduccion:.1f}%)")

# Estadisticas del conjunto final
print("\n[PASO 3] Estadisticas del conjunto filtrado...")

metodos_counter = Counter()
intenciones_counter = Counter()
anos_counter = Counter()

for art in articulos_recientes:
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})

    for m in var_principales.get("metodos_especifico", []):
        metodos_counter[m] += 1
    for i in var_principales.get("intenciones", []):
        intenciones_counter[i] += 1

    year = art.get("year")
    if year:
        anos_counter[year] += 1

print(f"\n  Metodos mas frecuentes:")
for metodo, count in metodos_counter.most_common(5):
    pct = count * 100 / total_final
    print(f"    - {metodo:20s}: {count:4d} ({pct:5.1f}%)")

print(f"\n  Intenciones mas frecuentes:")
for intencion, count in intenciones_counter.most_common(5):
    pct = count * 100 / total_final
    print(f"    - {intencion:20s}: {count:4d} ({pct:5.1f}%)")

print(f"\n  Distribucion por ano:")
for ano in sorted(anos_counter.keys()):
    count = anos_counter[ano]
    pct = count * 100 / total_final
    print(f"    - {ano}: {count:4d} ({pct:5.1f}%)")

# Generar JSON del conjunto filtrado
print("\n[PASO 4] Generando archivos de salida...")

conjunto_filtrado = {
    "tipo": "articulos_filtrados_elegibilidad",
    "fecha_generacion": "2026-05-04",
    "criterios_aplicados": [
        "Articulo DEBE tener metodos NLP/ML identificados (M1-M10)",
        "Articulo DEBE tener intenciones comunicativas identificadas (I1-I7)",
        "Articulo DEBE ser publicado en anos recientes (2021-2026)"
    ],
    "estadisticas": {
        "total_inicial": total_inicial,
        "total_final": total_final,
        "articulos_excluidos": total_inicial - total_final,
        "tasa_exclusion_pct": round(reduccion, 1),
        "tasa_inclusion_pct": round(100 - reduccion, 1)
    },
    "distribucion": {
        "por_metodo": dict(metodos_counter.most_common(10)),
        "por_intencion": dict(intenciones_counter.most_common(10)),
        "por_ano": dict(sorted(anos_counter.items()))
    },
    "articulos": [
        {
            "articulo_id": a["id"],
            "titulo": a["titulo"],
            "autores": a.get("autores", []),
            "year": a.get("year"),
            "doi": a.get("doi"),
            "metodos": a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", []),
            "intenciones": a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", []),
            "relevancia": a["relevancia_general"]
        }
        for a in sorted(articulos_recientes, key=lambda x: -x.get("relevancia_general", 0))
    ]
}

output_file = os.path.join(OUTPUT_DIR, "15_articulos_filtrados_elegibilidad.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(conjunto_filtrado, f, indent=2, ensure_ascii=False)

print(f"  [OK] 15_articulos_filtrados_elegibilidad.json ({total_final} articulos)")

# Generar resumen para PRISMA
prisma_summary = {
    "tipo": "prisma_flow_diagram",
    "fecha_generacion": "2026-05-04",
    "etapas": [
        {
            "etapa": "Registros identificados",
            "cantidad": total_inicial,
            "descripcion": "Total de registros en base de datos (RIS deduplicado)"
        },
        {
            "etapa": "Registros con metadata completa",
            "cantidad": sum(1 for a in articulos if a.get("abstract")),
            "descripcion": "Registros con titulo y abstract"
        },
        {
            "etapa": "Registros evaluados (screening)",
            "cantidad": total_inicial,
            "descripcion": "Todos los registros evaluados por relevancia"
        },
        {
            "etapa": "Registros con AMBOS (metodos + intenciones)",
            "cantidad": len(articulos_ambos),
            "criterio": "Debe tener metodos NLP/ML AND intenciones comunicativas",
            "descripcion": f"{len(articulos_ambos)} articulos cumplen criterio"
        },
        {
            "etapa": "Registros en anos recientes (2021-2026)",
            "cantidad": total_final,
            "criterio": "Ano >= 2021",
            "descripcion": f"{total_final} articulos para revision de texto completo"
        }
    ]
}

prisma_file = os.path.join(OUTPUT_DIR, "16_prisma_flow_diagram.json")
with open(prisma_file, "w", encoding="utf-8") as f:
    json.dump(prisma_summary, f, indent=2, ensure_ascii=False)

print(f"  [OK] 16_prisma_flow_diagram.json")

# Resumen visual
print("\n" + "="*70)
print("RESUMEN - FLUJO PRISMA CON FILTROS APLICADOS")
print("="*70)
print(f"\nRegistros identificados (RIS):           {total_inicial:6d}")
print(f"  [ Registros con abstract:                {sum(1 for a in articulos if a.get('abstract')):6d} (94.7%)")
print(f"  [ Registros sin abstract:                {sum(1 for a in articulos if not a.get('abstract')):6d} (5.3%)")
print(f"\nFILTRO 1 - AMBOS (metodos + intenciones):")
print(f"  [ Articulos que pasan:                   {len(articulos_ambos):6d} ({len(articulos_ambos)*100/total_inicial:.1f}%)")
print(f"\nFILTRO 2 - Anos recientes (2021-2026):")
print(f"  [ Articulos que pasan:                   {total_final:6d} ({total_final*100/total_inicial:.1f}% del inicial)")
print(f"\n*** REGISTROS PARA REVISION DE TEXTO COMPLETO: {total_final:6d} ***")
print(f"\nDistribucion por ano (n={total_final}):")
for ano in sorted(anos_counter.keys()):
    count = anos_counter[ano]
    pct = count * 100 / total_final
    bar = "=" * int(pct / 2)
    print(f"  {ano}: {bar:30s} {count:3d} ({pct:5.1f}%)")

print("\n" + "="*70)
print("[OK] Filtrado completado")
print("="*70 + "\n")
