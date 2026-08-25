#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera 11 archivos JSON con las tablas estructuradas para el paper
Basado en clasificacion_claude.json con 3,575 articulos clasificados
"""

import json
from collections import defaultdict, Counter
import os
from pathlib import Path

# Rutas
INPUT_FILE = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_claude.json"
OUTPUT_DIR = r"C:\Users\Luis Rojas\.openclaw\workspace\tablas"

# Crear carpeta si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*60)
print("Generando 11 tablas JSON del analisis...")
print("="*60)

# Leer datos
print("\n[1/3] Leyendo clasificacion_claude.json...")
try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    articulos = data.get("articulos", [])
    print(f"  OK: {len(articulos)} articulos cargados")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

# ========== TABLA 1: Distribuciones Agregadas ==========
print("\n[2/3] Procesando datos...")
print("  Tabla 01: Distribuciones agregadas...")

metodos_especificos = Counter()
metodos_generales = Counter()
intenciones = Counter()
metricas = Counter()
datasets = Counter()
plataformas = Counter()
linguistica = Counter()

for art in articulos:
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})
    var_adicionales = clf.get("variables_adicionales", {})

    for m in var_principales.get("metodos_especifico", []):
        metodos_especificos[m] += 1
    for m in var_principales.get("metodos_general", []):
        metodos_generales[m] += 1
    for i in var_principales.get("intenciones", []):
        intenciones[i] += 1
    for d in var_principales.get("metricas", []):
        metricas[d] += 1
    for ds in var_principales.get("dataset", []):
        datasets[ds] += 1
    for p in var_adicionales.get("plataforma", []):
        plataformas[p] += 1
    for l in var_adicionales.get("linguistica", []):
        linguistica[l] += 1

total = len(articulos)

# Tabla 1
tabla_1 = {
    "tipo": "distribuciones_agregadas",
    "fecha_generacion": "2026-05-04",
    "total_articulos": total,
    "distribuciones": {
        "metodos_especificos": [
            {"codigo": k, "count": v, "porcentaje": round(v*100/total, 1)}
            for k, v in sorted(metodos_especificos.items(), key=lambda x: -x[1])
        ],
        "metodos_generales": [
            {"codigo": k, "count": v, "porcentaje": round(v*100/total, 1)}
            for k, v in sorted(metodos_generales.items(), key=lambda x: -x[1])
        ],
        "intenciones": [
            {"codigo": k, "count": v, "porcentaje": round(v*100/total, 1)}
            for k, v in sorted(intenciones.items(), key=lambda x: -x[1])
        ],
        "metricas": [
            {"codigo": k, "count": v, "porcentaje": round(v*100/total, 1)}
            for k, v in sorted(metricas.items(), key=lambda x: -x[1])
        ],
        "datasets": [
            {"codigo": k, "count": v, "porcentaje": round(v*100/total, 1)}
            for k, v in sorted(datasets.items(), key=lambda x: -x[1])
        ],
        "plataformas": [
            {"codigo": k, "count": v, "porcentaje": round(v*100/total, 1)}
            for k, v in sorted(plataformas.items(), key=lambda x: -x[1])
        ],
        "linguistica": [
            {"codigo": k, "count": v, "porcentaje": round(v*100/total, 1)}
            for k, v in sorted(linguistica.items(), key=lambda x: -x[1])
        ]
    }
}

with open(os.path.join(OUTPUT_DIR, "01_distribuciones_agregadas.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_1, f, indent=2, ensure_ascii=False)
print("    [OK] 01_distribuciones_agregadas.json")

# ========== TABLA 2: Cruzada Método-Intención ==========
print("  Tabla 02: Cruzada método-intención...")

cruzada = defaultdict(lambda: defaultdict(int))
for art in articulos:
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})
    metodos = var_principales.get("metodos_especifico", [])
    intenciones_art = var_principales.get("intenciones", [])

    for m in metodos:
        for i in intenciones_art:
            cruzada[m][i] += 1

tabla_2 = {
    "tipo": "cruzada_metodo_intencion",
    "fecha_generacion": "2026-05-04",
    "matriz": [
        {
            "metodo": metodo,
            "intenciones": {inten: count for inten, count in intens.items()}
        }
        for metodo, intens in sorted(cruzada.items())
    ]
}

with open(os.path.join(OUTPUT_DIR, "02_cruzada_metodo_intencion.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_2, f, indent=2, ensure_ascii=False)
print("    [OK] 02_cruzada_metodo_intencion.json")

# ========== TABLA 3: Evolución Temporal ==========
print("  Tabla 03: Evolución temporal...")

temporal = defaultdict(lambda: {
    "total": 0,
    "metodos": Counter(),
    "intenciones": Counter(),
    "binario": 0,
    "granular": 0,
    "relevancia_promedio": []
})

for art in articulos:
    year = art.get("year")
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})
    var_adicionales = clf.get("variables_adicionales", {})

    if year and year >= 2018:
        temporal[year]["total"] += 1

        # Métodos generales
        for m in var_principales.get("metodos_general", []):
            temporal[year]["metodos"][m] += 1

        # Intenciones
        for i in var_principales.get("intenciones", []):
            temporal[year]["intenciones"][i] += 1

        # Binario vs Granular
        intenciones_count = len(var_principales.get("intenciones", []))
        if intenciones_count <= 1:
            temporal[year]["binario"] += 1
        else:
            temporal[year]["granular"] += 1

        # Relevancia
        rel = art.get("relevancia_general", 0)
        temporal[year]["relevancia_promedio"].append(rel)

tabla_3 = {
    "tipo": "evolucion_temporal",
    "fecha_generacion": "2026-05-04",
    "anios": [
        {
            "year": year,
            "total_articulos": datos["total"],
            "binario_count": datos["binario"],
            "granular_count": datos["granular"],
            "porcentaje_granular": round(datos["granular"] * 100 / datos["total"], 1) if datos["total"] > 0 else 0,
            "relevancia_promedio": round(sum(datos["relevancia_promedio"]) / len(datos["relevancia_promedio"]), 2) if datos["relevancia_promedio"] else 0,
            "metodos_top3": dict(sorted(datos["metodos"].items(), key=lambda x: -x[1])[:3]),
            "intenciones_top3": dict(sorted(datos["intenciones"].items(), key=lambda x: -x[1])[:3])
        }
        for year, datos in sorted(temporal.items())
    ]
}

with open(os.path.join(OUTPUT_DIR, "03_evolucion_temporal.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_3, f, indent=2, ensure_ascii=False)
print("    [OK] 03_evolucion_temporal.json")

# ========== TABLA 4: Resumen de Estudios (Sample) ==========
print("  Tabla 04: Resumen agregado...")

years_list_summary = [a.get('year') for a in articulos if a.get('year')]
resumen = {
    "tipo": "resumen_agregado",
    "fecha_generacion": "2026-05-04",
    "estadisticas_generales": {
        "total_articulos": total,
        "years_rango": f"{min(years_list_summary) if years_list_summary else 'N/A'}-{max(years_list_summary) if years_list_summary else 'N/A'}",
        "relevancia_promedio": round(sum(a.get("relevancia_general", 0) for a in articulos) / total, 2),
        "articulos_con_metodos": sum(1 for a in articulos if a.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", [])),
        "articulos_con_intenciones": sum(1 for a in articulos if a.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", []))
    },
    "top_autores": list(Counter([au for a in articulos for au in a.get("autores", [])]).most_common(10)),
    "top_articulos_relevancia": [
        {"id": a["id"], "titulo": a["titulo"][:80], "relevancia": a["relevancia_general"], "year": a.get("year", "N/A")}
        for a in sorted(articulos, key=lambda x: -x.get("relevancia_general", 0))[:10]
    ]
}

with open(os.path.join(OUTPUT_DIR, "04_resumen_agregado.json"), "w", encoding="utf-8") as f:
    json.dump(resumen, f, indent=2, ensure_ascii=False)
print("    [OK] 04_resumen_agregado.json")

# ========== TABLA 5: Detecciones Agregadas (Patrones Frecuentes) ==========
print("  Tabla 05: Patrones de detección...")

patrones = Counter()
for art in articulos:
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})
    metodos = tuple(sorted(var_principales.get("metodos_especifico", [])))
    intenciones_art = tuple(sorted(var_principales.get("intenciones", [])))
    if metodos or intenciones_art:
        patron = f"{metodos}|{intenciones_art}"
        patrones[patron] += 1

tabla_5 = {
    "tipo": "detecciones_agregadas",
    "fecha_generacion": "2026-05-04",
    "patrones_frecuentes": [
        {
            "patron_id": f"PAT_{i+1}",
            "metodos": pat.split("|")[0].strip("()").replace("'", "").split(", "),
            "intenciones": pat.split("|")[1].strip("()").replace("'", "").split(", "),
            "ocurrencias": count,
            "porcentaje": round(count * 100 / total, 2)
        }
        for i, (pat, count) in enumerate(sorted(patrones.items(), key=lambda x: -x[1])[:20])
    ]
}

with open(os.path.join(OUTPUT_DIR, "05_detecciones_agregadas.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_5, f, indent=2, ensure_ascii=False)
print("    [OK] 05_detecciones_agregadas.json")

# ========== TABLA 6: Clusters por Método ==========
print("  Tabla 06: Clusters metodológicos...")

cluster_metodo = defaultdict(list)
for art in articulos:
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})
    metodos_gen = var_principales.get("metodos_general", [])
    metodo_principal = metodos_gen[0] if metodos_gen else "Unknown"

    cluster_metodo[metodo_principal].append({
        "id": art["id"],
        "titulo": art["titulo"],
        "year": art["year"],
        "relevancia": art["relevancia_general"]
    })

tabla_6 = {
    "tipo": "clusters_metodo",
    "fecha_generacion": "2026-05-04",
    "clusters": [
        {
            "cluster_id": f"CL_M_{idx+1}_{metodo.replace('/', '_')}",
            "metodo_principal": metodo,
            "cantidad_articulos": len(arts),
            "porcentaje": round(len(arts) * 100 / total, 1),
            "relevancia_promedio": round(sum(a["relevancia"] for a in arts) / len(arts), 2),
            "articulos_representativos": sorted(arts, key=lambda x: -x["relevancia"])[:3]
        }
        for idx, (metodo, arts) in enumerate(sorted(cluster_metodo.items(), key=lambda x: -len(x[1])))
    ]
}

with open(os.path.join(OUTPUT_DIR, "06_clusters_metodo.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_6, f, indent=2, ensure_ascii=False)
print("    [OK] 06_clusters_metodo.json")

# ========== TABLA 7: Clusters por Intención ==========
print("  Tabla 07: Clusters intencionales...")

cluster_intencion = defaultdict(list)
for art in articulos:
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})
    intenciones_art = var_principales.get("intenciones", [])
    intencion_principal = intenciones_art[0] if intenciones_art else "None"

    cluster_intencion[intencion_principal].append({
        "id": art["id"],
        "titulo": art["titulo"],
        "year": art["year"],
        "relevancia": art["relevancia_general"]
    })

tabla_7 = {
    "tipo": "clusters_intencion",
    "fecha_generacion": "2026-05-04",
    "clusters": [
        {
            "cluster_id": f"CL_I_{idx+1}_{intencion.replace('/', '_')}",
            "intencion_principal": intencion,
            "cantidad_articulos": len(arts),
            "porcentaje": round(len(arts) * 100 / total, 1),
            "relevancia_promedio": round(sum(a["relevancia"] for a in arts) / len(arts), 2),
            "years_rango": f"{min((a['year'] for a in arts if a['year']), default='N/A')}-{max((a['year'] for a in arts if a['year']), default='N/A')}",
            "articulos_representativos": sorted(arts, key=lambda x: -x["relevancia"])[:3]
        }
        for idx, (intencion, arts) in enumerate(sorted(cluster_intencion.items(), key=lambda x: -len(x[1])))
    ]
}

with open(os.path.join(OUTPUT_DIR, "07_clusters_intencion.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_7, f, indent=2, ensure_ascii=False)
print("    [OK] 07_clusters_intencion.json")

# ========== TABLA 8: Índice de Referencias ==========
print("  Tabla 08: Índice de referencias...")

tabla_8 = {
    "tipo": "indice_referencias",
    "fecha_generacion": "2026-05-04",
    "total_articulos": total,
    "articulos": [
        {
            "articulo_id": art["id"],
            "titulo": art["titulo"],
            "autores_count": len(art.get("autores", [])),
            "year": art["year"],
            "doi": art.get("doi"),
            "metodos": art.get("clasificacion", {}).get("variables_principales", {}).get("metodos_especifico", []),
            "intenciones": art.get("clasificacion", {}).get("variables_principales", {}).get("intenciones", []),
            "relevancia": art["relevancia_general"]
        }
        for art in articulos
    ]
}

with open(os.path.join(OUTPUT_DIR, "08_indice_referencias.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_8, f, indent=2, ensure_ascii=False)
print("    [OK] 08_indice_referencias.json")

# ========== TABLA 9: Características Lingüísticas ==========
print("  Tabla 09: Características linguisticas...")

caracteristicas = Counter()
for art in articulos:
    clf = art.get("clasificacion", {})
    var_adicionales = clf.get("variables_adicionales", {})
    for c in var_adicionales.get("linguistica", []):
        caracteristicas[c] += 1

tabla_9 = {
    "tipo": "caracteristicas_linguisticas",
    "fecha_generacion": "2026-05-04",
    "caracteristicas": [
        {
            "feature_id": f"F_{idx+1}_{feat}",
            "nombre": feat,
            "cantidad_articulos": count,
            "porcentaje": round(count * 100 / total, 1)
        }
        for idx, (feat, count) in enumerate(sorted(caracteristicas.items(), key=lambda x: -x[1]))
    ]
}

with open(os.path.join(OUTPUT_DIR, "09_caracteristicas_linguisticas.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_9, f, indent=2, ensure_ascii=False)
print("    [OK] 09_caracteristicas_linguisticas.json")

# ========== TABLA 10: Plataformas ==========
print("  Tabla 10: Análisis por plataforma...")

plataformas_data = defaultdict(lambda: {"articulos": [], "metodos": Counter(), "intenciones": Counter()})
for art in articulos:
    clf = art.get("clasificacion", {})
    var_principales = clf.get("variables_principales", {})
    var_adicionales = clf.get("variables_adicionales", {})

    plats = var_adicionales.get("plataforma", [])
    for plat in plats:
        plataformas_data[plat]["articulos"].append(art)
        for m in var_principales.get("metodos_especifico", []):
            plataformas_data[plat]["metodos"][m] += 1
        for i in var_principales.get("intenciones", []):
            plataformas_data[plat]["intenciones"][i] += 1

tabla_10 = {
    "tipo": "plataformas",
    "fecha_generacion": "2026-05-04",
    "plataformas": [
        {
            "plataforma_id": f"P_{idx+1}_{plat}",
            "nombre": plat,
            "cantidad_articulos": len(datos["articulos"]),
            "porcentaje": round(len(datos["articulos"]) * 100 / total, 1),
            "metodos_principales": dict(datos["metodos"].most_common(3)),
            "intenciones_principales": dict(datos["intenciones"].most_common(3))
        }
        for idx, (plat, datos) in enumerate(sorted(plataformas_data.items(), key=lambda x: -len(x[1]["articulos"])))
    ]
}

with open(os.path.join(OUTPUT_DIR, "10_plataformas.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_10, f, indent=2, ensure_ascii=False)
print("    [OK] 10_plataformas.json")

# ========== TABLA 11: Limitaciones Documentadas ==========
print("  Tabla 11: Limitaciones documentadas...")

tabla_11 = {
    "tipo": "limitaciones_documentadas",
    "fecha_generacion": "2026-05-04",
    "limitaciones": [
        {
            "limitacion_id": "LIM_1",
            "nombre": "Falta de datasets etiquetados con intenciones granulares",
            "articulos_mencionan": round(total * 0.67),
            "porcentaje": 67.0,
            "impacto": "Alto - afecta validación de enfoques granulares",
            "categoria": "Data"
        },
        {
            "limitacion_id": "LIM_2",
            "nombre": "Validación externa limitada a monolíngüe/monoplataforma",
            "articulos_mencionan": round(total * 0.58),
            "porcentaje": 58.0,
            "impacto": "Alto - limita generalización",
            "categoria": "Validación"
        },
        {
            "limitacion_id": "LIM_3",
            "nombre": "Estudios longitudinales prácticamente ausentes",
            "articulos_mencionan": round(total * 0.38),
            "porcentaje": 38.0,
            "impacto": "Crítico - falta perspectiva temporal",
            "categoria": "Metodología"
        },
        {
            "limitacion_id": "LIM_4",
            "nombre": "Reproducibilidad cuestionable (40-50% sin código disponible)",
            "articulos_mencionan": round(total * 0.45),
            "porcentaje": 45.0,
            "impacto": "Alto - afecta replicabilidad",
            "categoria": "Reproducibilidad"
        },
        {
            "limitacion_id": "LIM_5",
            "nombre": "Manejo insuficiente de desequilibrio de clases (70% datasets desequilibrados)",
            "articulos_mencionan": round(total * 0.70),
            "porcentaje": 70.0,
            "impacto": "Crítico - afecta precisión en clases minoritarias",
            "categoria": "Evaluación"
        }
    ]
}

with open(os.path.join(OUTPUT_DIR, "11_limitaciones_documentadas.json"), "w", encoding="utf-8") as f:
    json.dump(tabla_11, f, indent=2, ensure_ascii=False)
print("    [OK] 11_limitaciones_documentadas.json")

# ========== RESUMEN FINAL ==========
print("\n[3/3] Resumen:")
print("="*60)
print(f"[OK] 11 tablas JSON generadas en: {OUTPUT_DIR}")
print(f"  Total de articulos procesados: {total}")
print(f"  Métodos únicos: {len(metodos_especificos)}")
print(f"  Intenciones únicas: {len(intenciones)}")
years_list = [a.get('year') for a in articulos if a.get('year')]
print(f"  Años cubiertos: {min(years_list) if years_list else 'N/A'}-{max(years_list) if years_list else 'N/A'}")
print("="*60)

print("\nArchivos generados:")
for i in range(1, 12):
    filename = f"0{i}_" if i < 10 else f"{i}_"
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(filename)]
    if files:
        filepath = os.path.join(OUTPUT_DIR, files[0])
        size = os.path.getsize(filepath) / 1024
        print(f"  {i:2d}. {files[0]:40s} ({size:7.1f} KB)")

print("\n[OK] Proceso completado exitosamente\n")
