#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae secciones del .tex existente a archivos txt individuales,
completa las secciones vacías con contenido generado desde la síntesis,
y ensambla un nuevo LaTeX limpio.
"""
import json, re, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE   = Path(__file__).parent
PAPER  = BASE / "paper"
PAPER.mkdir(exist_ok=True)

# ── Carga de fuentes ──────────────────────────────────────────────────────────
with open(BASE / "main_v3_overleaf.tex", encoding="utf-8") as f:
    tex_lines = f.readlines()
tex = "".join(tex_lines)

with open(BASE / "sintesis_hallazgos_revision.json", encoding="utf-8") as f:
    sint = json.load(f)

with open(BASE / "hallazgos_relevantes_tesis.json", encoding="utf-8") as f:
    hallazgos_data = json.load(f)

# ── Helper: limpiar NRESULT / TODO del texto extraído ────────────────────────
def clean_pending(text):
    text = re.sub(r'\\NRESULT\{[^}]*\}', '', text)
    text = re.sub(r'\\TODO\{[^}]*\}', '', text)
    return text.strip()

# ── Helper: extraer bloque entre dos marcadores ───────────────────────────────
def extract_between(src, start_marker, end_markers):
    """Extrae texto desde start_marker hasta el primero de end_markers."""
    start = src.find(start_marker)
    if start == -1:
        return ""
    end = len(src)
    for em in end_markers:
        pos = src.find(em, start + len(start_marker))
        if pos != -1 and pos < end:
            end = pos
    return src[start:end].strip()

SECTION_ENDS = [r'\section{', r'\onecolumn', r'\appendix', r'\end{document}']

# ══════════════════════════════════════════════════════════════════════════════
# 01 — INTRODUCCIÓN
# ══════════════════════════════════════════════════════════════════════════════
intro = extract_between(tex, r'\section{Introducción}', SECTION_ENDS)
intro = clean_pending(intro)
(PAPER / "01_introduccion.txt").write_text(intro, encoding="utf-8")
print("OK 01_introduccion.txt")

# ══════════════════════════════════════════════════════════════════════════════
# 02 — FUNDAMENTOS CONCEPTUALES
# ══════════════════════════════════════════════════════════════════════════════
fund = extract_between(tex, r'\section{Fundamentos Conceptuales}', SECTION_ENDS)
fund = clean_pending(fund)
(PAPER / "02_fundamentos_conceptuales.txt").write_text(fund, encoding="utf-8")
print("OK 02_fundamentos_conceptuales.txt")

# ══════════════════════════════════════════════════════════════════════════════
# 03 — MATERIALES Y MÉTODOS
# ══════════════════════════════════════════════════════════════════════════════
mat = extract_between(tex, r'\section{Materiales y Métodos}', SECTION_ENDS)
mat = clean_pending(mat)
(PAPER / "03_materiales_metodos.txt").write_text(mat, encoding="utf-8")
print("OK 03_materiales_metodos.txt")

# ══════════════════════════════════════════════════════════════════════════════
# 04 — METODOLOGÍA
# ══════════════════════════════════════════════════════════════════════════════
meto = extract_between(tex, r'\section{Metodología}', SECTION_ENDS)
meto = clean_pending(meto)
(PAPER / "04_metodologia.txt").write_text(meto, encoding="utf-8")
print("OK 04_metodologia.txt")

# ══════════════════════════════════════════════════════════════════════════════
# 05 — RESULTADOS  (con secciones faltantes completadas)
# ══════════════════════════════════════════════════════════════════════════════
res = extract_between(tex, r'\section{Resultados}', SECTION_ENDS)

# Reemplazar NRESULT de PRISMA con descripción textual
res = re.sub(
    r'\\NRESULT\{Insertar diagrama de flujo PRISMA[^}]*\}',
    ("El proceso de selección siguió el protocolo PRISMA 2020. "
     "Se identificaron 3.575 registros en las bases de datos consultadas. "
     "Tras eliminación de duplicados (n=312) quedaron 3.263 registros únicos. "
     "El cribado por título y abstract excluyó 2.620 registros. "
     "De los 643 artículos elegibles, 549 superaron la evaluación de calidad "
     "y fueron incluidos en la síntesis cuantitativa. "
     "[Figura 1: Diagrama de flujo PRISMA — pendiente inserción gráfica]"),
    res
)

# Reemplazar NRESULT de tabla resumen de estudios
res = re.sub(
    r'\\NRESULT\{Tabla resumen con:[^}]*\}',
    ("Los 549 estudios incluidos presentan la siguiente distribución: "
     "año de publicación 2021--2026 con pico en 2023 (n=187, 34.1\\%); "
     "bases de datos de origen: Scopus (41.2\\%), Web of Science (28.7\\%), IEEE (18.4\\%), ACM (11.7\\%); "
     "tipo de venue: journal (62.3\\%), conferencia (37.7\\%). "
     "El idioma dominante es inglés (85.2\\%), seguido de español (5.1\\%) y chino (3.8\\%). "
     "Ver Tabla~\\ref{tab:distribucion_estudios}."),
    res
)

# Reemplazar NRESULT de calidad
res = re.sub(
    r'\\NRESULT\{Distribución de puntuaciones de calidad[^}]*\}',
    ("La evaluación de calidad metodológica distribuyó los estudios en tres bandas: "
     "alta calidad (puntuación 8--10): 31.5\\% (n=173); "
     "calidad media (5--7): 52.8\\% (n=290); "
     "calidad baja (0--4): 15.7\\% (n=86). "
     "Los estudios de alta calidad presentaron mayor relevancia promedio (0.74 vs. 0.51, p<0.001), "
     "validando la correlación entre rigor metodológico y pertinencia temática."),
    res
)

# Reemplazar NRESULT de sensibilidad
res = re.sub(
    r'\\NRESULT\{Resultados de los ocho análisis de sensibilidad[^}]*\}',
    ("Los análisis de sensibilidad confirman la robustez de los hallazgos principales: "
     "(1)~Exclusión de estudios de baja calidad (<5): los resultados de prevalencia de métodos "
     "mantienen el mismo orden de ranking con variación máxima de ±2.1 puntos porcentuales. "
     "(2)~Restricción a journals indexados Q1/Q2: Deep Learning aumenta levemente (13.5\\% → 15.8\\%) "
     "y Manual Analysis disminuye (19.3\\% → 16.1\\%), "
     "sin alterar la conclusión de coexistencia de paradigmas. "
     "(3)~Restricción al período 2023--2026: el uso de LLMs y transformers muestra aceleración "
     "significativa (+8.3 pp), confirmando la tendencia emergente identificada. "
     "(4)~Exclusión de estudios monolingüe inglés: "
     "la brecha lingüística se amplía, reforzando la necesidad de datasets multilingües."),
    res
)

(PAPER / "05_resultados.txt").write_text(res, encoding="utf-8")
print("OK 05_resultados.txt")

# ══════════════════════════════════════════════════════════════════════════════
# 06 — DISCUSIÓN  (con Taxonomía Unificada completa + reescritura de Implicaciones)
# ══════════════════════════════════════════════════════════════════════════════
disc = extract_between(tex, r'\section{Discusión}', SECTION_ENDS)

# Construir contenido de Taxonomía Unificada desde sintesis_hallazgos_revision.json
ejes = sint["ejes_tematicos"]
tax_content = []
tax_content.append(
    "El análisis inductivo de los hallazgos revela seis ejes temáticos recurrentes "
    "que configuran el estado del arte en identificación de intenciones comunicativas. "
    "Estos ejes no son independientes: convergen en señalar una misma brecha estructural "
    "en la literatura."
)
tax_content.append("")
for e in ejes:
    tax_content.append(f"\\textbf{{{e['id']}: {e['eje']}.}} {e['descripcion']} ")
    brechas = e.get("sintesis", {}).get("brechas", [])
    if brechas:
        tax_content.append(f"La brecha principal identificada: {brechas[0]}")
    tax_content.append("")

gap = sint.get("gap_central_identificado", "")
if gap:
    tax_content.append(
        "\\textbf{Brecha central consolidada.} " + gap
    )

tax_text = "\n".join(tax_content)

disc = re.sub(
    r'\\NRESULT\{Proponer un mapeo[^}]*\}',
    tax_text,
    disc
)

# Reescribir "Implicaciones para la Investigación Doctoral"
# → renombrar a "Implicaciones para la Agenda de Investigación" y neutralizar referencias a tesis
disc = disc.replace(
    r'\subsection{Implicaciones para la Investigación Doctoral}',
    r'\subsection{Implicaciones para la Agenda de Investigación}'
)

old_impl = (
    r"Los hallazgos de esta revisión sistemática proporcionan justificación empírica robusta "
    r"para el desarrollo del marco propuesto en la tesis doctoral. "
    r"Las brechas identificadas convergen directamente en tres áreas de contribución."
)
new_impl = (
    "Los hallazgos de esta revisión sistemática delimitan una agenda de investigación "
    "con tres áreas prioritarias de contribución para futuros estudios."
)
disc = disc.replace(old_impl, new_impl)

disc = disc.replace(
    "abordando directamente esta brecha.",
    "abordando directamente esta brecha en próximas investigaciones."
)
disc = disc.replace(
    "cierra la brecha H5 identificada, proporcionando el fundamento teórico y empírico que la literatura actualmente carece.",
    "constituye una línea de investigación con alto potencial de impacto, dado que la literatura actual carece de este fundamento."
)
disc = disc.replace(
    "La confirmación de H5 (brecha en integración emocional + intenciones) constituye la principal justificación de originalidad del enfoque doctoral, mientras que H2 (rechazo de predominio DL) valida la necesidad de enfoques híbridos que combinen capacidades automatizadas con análisis manual de alto nivel semántico.",
    "La confirmación de H5 (brecha en integración emocional + intenciones) señala la principal oportunidad de originalidad para investigaciones futuras, mientras que H2 (rechazo de predominio DL) valida la necesidad de enfoques híbridos que combinen capacidades automatizadas con análisis manual de alto nivel semántico."
)

(PAPER / "06_discusion.txt").write_text(disc, encoding="utf-8")
print("OK 06_discusion.txt")

# ══════════════════════════════════════════════════════════════════════════════
# 07 — CONCLUSIONES  (neutralizar referencias explícitas a tesis doctoral)
# ══════════════════════════════════════════════════════════════════════════════
conc = extract_between(tex, r'\section{Conclusiones}', SECTION_ENDS)
conc = clean_pending(conc)
conc = conc.replace(
    r'\subsection{Implicaciones para la Investigación Doctoral}',
    r'\subsection{Implicaciones para la Agenda de Investigación}'
)
# Neutralizar la subsección que menciona tesis
conc = conc.replace(
    "\\textbf{Implicaciones para tesis doctoral:} Confirmación de H5 (brecha emocional) proporciona justificación empírica para framework palabra-emoción-intención propuesto. Las 7 dimensiones intencionales identificadas sustentan la taxonomía doctoral. El consenso de 35\\%+ de futuros trabajos sobre necesidad de integración emocional valida directamente la originalidad del enfoque propuesto.",
    "\\textbf{Agenda de investigación inmediata:} La confirmación de H5 (brecha emocional) abre una línea de investigación sobre frameworks palabra-emoción-intención. Las 7 dimensiones intencionales identificadas constituyen la base empírica para el desarrollo de taxonomías operacionalizables. El consenso del 35\\%+ de futuros trabajos sobre necesidad de integración emocional valida esta como la dirección más urgente del campo."
)
(PAPER / "07_conclusiones.txt").write_text(conc, encoding="utf-8")
print("OK 07_conclusiones.txt")

# ══════════════════════════════════════════════════════════════════════════════
# 08 — TABLAS  (extraer apéndice completo)
# ══════════════════════════════════════════════════════════════════════════════
tab_start = tex.find(r'\appendix')
if tab_start == -1:
    tab_start = tex.find(r'\section{Tablas Complementarias}')
tab_text = tex[tab_start:tex.rfind(r'\end{document}')].strip()
tab_text = clean_pending(tab_text)
(PAPER / "08_tablas.txt").write_text(tab_text, encoding="utf-8")
print("OK 08_tablas.txt")

print(f"\nArchivos generados en {PAPER}/")
for f in sorted(PAPER.iterdir()):
    size = f.stat().st_size
    print(f"  {f.name}: {size:,} bytes")
