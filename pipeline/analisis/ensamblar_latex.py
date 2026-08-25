#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE  = Path(__file__).parent
PAPER = BASE / "paper"

# Leer preámbulo del tex original (hasta \begin{document})
with open(BASE / "main_v3_overleaf.tex", encoding="utf-8") as f:
    original = f.read()

preamble_end = original.find(r'\begin{document}') + len(r'\begin{document}')
preamble = original[:preamble_end]

# Leer bloque de agradecimientos y referencias del original
agradec_start = original.find(r'\section*{Agradecimientos}')
refs_end      = original.find(r'\end{document}')
closing       = original[agradec_start:refs_end].strip()

# Leer secciones desde los txt generados
def read(name):
    return (PAPER / name).read_text(encoding="utf-8")

sections = [
    read("01_introduccion.txt"),
    read("02_fundamentos_conceptuales.txt"),
    read("03_materiales_metodos.txt"),
    read("04_metodologia.txt"),
    read("05_resultados.txt"),
    read("06_discusion.txt"),
    read("07_conclusiones.txt"),
]
tables = read("08_tablas.txt")

# Ensamblar
parts = [
    preamble,
    "",
    *sections,
    "",
    r"\onecolumn",
    tables,
    "",
    closing,
    "",
    r"\end{document}",
]

output = "\n\n".join(parts)

out_path = PAPER / "main_v4.tex"
out_path.write_text(output, encoding="utf-8")
print(f"LaTeX generado: {out_path}")
print(f"Tamaño: {out_path.stat().st_size:,} bytes")

# Verificar que no quedan NRESULT/TODO sin resolver
import re
pendientes = re.findall(r'\\(?:NRESULT|TODO)\{[^}]*\}', output)
if pendientes:
    print(f"\nATENCION — {len(pendientes)} pendiente(s) sin resolver:")
    for p in pendientes:
        print(f"  {p[:80]}")
else:
    print("\nSin pendientes — paper limpio.")
