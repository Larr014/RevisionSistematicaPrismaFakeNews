#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte tablas JSON a formato LaTeX tabular para compilación directa en Overleaf
"""

import json
import os
from pathlib import Path

INPUT_FILE = r"C:\Users\Luis Rojas\.openclaw\workspace\clasificacion_claude.json"
OUTPUT_FILE = r"C:\Users\Luis Rojas\.openclaw\workspace\tablas_latex.tex"

def load_data():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_label(codigo):
    """Traduce códigos a etiquetas"""
    labels = {
        "M1_BERT": "BERT", "M2_GPT": "GPT", "M3_Transformers": "Transformers",
        "M4_CNN": "CNN", "M5_RNN_LSTM": "RNN/LSTM", "M6_SVM": "SVM",
        "M7_NaiveBayes": "Naive Bayes", "M8_RandomForest": "Random Forest",
        "M9_NLP_Traditional": "NLP Trad.", "M10_ManualAnalysis": "Manual",
        "I1_FakeNews": "Fake News", "I2_Manipulation": "Manipulación",
        "I3_Persuasion": "Persuasión", "I4_Clickbait": "Clickbait",
        "I5_Polarization": "Polarización", "I6_Emotion": "Emoción",
        "I7_Conspiracy": "Conspiración", "P1_Twitter": "Twitter/X",
        "P2_Facebook": "Facebook", "P3_News": "Noticias",
        "L1_English": "Inglés", "L2_Spanish": "Español", "L3_Multilingual": "Multilingüe",
    }
    return labels.get(codigo, codigo)

def tabla_distribuciones(data):
    """Tabla 1: Distribuciones agregadas en formato LaTeX"""
    articulos = data['articulos']

    from collections import defaultdict
    metodos = defaultdict(int)
    intenciones = defaultdict(int)

    for art in articulos:
        cls = art['clasificacion']
        for m in cls['variables_principales'].get('metodos_especifico', []):
            metodos[m] += 1
        for i in cls['variables_principales'].get('intenciones', []):
            intenciones[i] += 1

    latex = r"""
\begin{table}[H]
\centering
\caption{Distribución de Métodos Específicos Identificados}
\label{tab:latex_metodos}
\begin{tabular}{|l|c|c|}
\hline
\textbf{Método} & \textbf{N} & \textbf{\%} \\
\hline
"""

    total = len(articulos)
    for m in sorted(metodos.items(), key=lambda x: x[1], reverse=True):
        pct = round(100 * m[1] / total, 1)
        latex += f"{get_label(m[0])} & {m[1]} & {pct}\% \\\\\n"

    latex += r"""\hline
\end{tabular}
\end{table}

\begin{table}[H]
\centering
\caption{Distribución de Intenciones Comunicativas Detectadas}
\label{tab:latex_intenciones}
\begin{tabular}{|l|c|c|}
\hline
\textbf{Intención} & \textbf{N} & \textbf{\%} \\
\hline
"""

    for i in sorted(intenciones.items(), key=lambda x: x[1], reverse=True):
        pct = round(100 * i[1] / total, 1)
        latex += f"{get_label(i[0])} & {i[1]} & {pct}\% \\\\\n"

    latex += r"""\hline
\end{tabular}
\end{table}
"""
    return latex

def tabla_temporal(data):
    """Tabla 2: Evolución temporal"""
    articulos = data['articulos']
    from collections import defaultdict

    temporal = defaultdict(lambda: {'total': 0, 'binario': 0, 'granular': 0})

    for art in articulos:
        year = art.get('year')
        if not year or year < 2018:
            continue

        cls = art['clasificacion']
        temporal[year]['total'] += 1

        intenciones = cls['variables_principales'].get('intenciones', [])
        if len(intenciones) <= 1:
            temporal[year]['binario'] += 1
        else:
            temporal[year]['granular'] += 1

    latex = r"""
\begin{table}[H]
\centering
\caption{Evolución Temporal: Enfoque Binario vs. Granular (2018-2026)}
\label{tab:latex_temporal}
\begin{tabular}{|c|c|c|c|c|}
\hline
\textbf{Año} & \textbf{Total} & \textbf{Binario} & \textbf{Granular} & \textbf{\% Granular} \\
\hline
"""

    for year in sorted(temporal.keys()):
        data_year = temporal[year]
        total = data_year['total']
        granular_pct = round(100 * data_year['granular'] / total, 1) if total > 0 else 0
        latex += f"{year} & {total} & {data_year['binario']} & {data_year['granular']} & {granular_pct}\% \\\\\n"

    latex += r"""\hline
\end{tabular}
\end{table}
"""
    return latex

def tabla_plataformas(data):
    """Tabla 3: Análisis por plataforma"""
    articulos = data['articulos']
    from collections import defaultdict

    plataformas = defaultdict(int)

    for art in articulos:
        cls = art['clasificacion']
        p_list = cls['variables_adicionales'].get('plataforma', [])
        for p in p_list:
            plataformas[p] += 1

    latex = r"""
\begin{table}[H]
\centering
\caption{Estudios por Plataforma Digital}
\label{tab:latex_plataformas}
\begin{tabular}{|l|c|c|}
\hline
\textbf{Plataforma} & \textbf{N} & \textbf{\%} \\
\hline
"""

    total = len(articulos)
    for p in sorted(plataformas.items(), key=lambda x: x[1], reverse=True):
        pct = round(100 * p[1] / total, 1)
        latex += f"{get_label(p[0])} & {p[1]} & {pct}\% \\\\\n"

    latex += r"""\hline
\end{tabular}
\end{table}
"""
    return latex

def tabla_limitaciones(data):
    """Tabla 4: Limitaciones documentadas"""
    articulos = data['articulos']

    latex = r"""
\begin{table}[H]
\centering
\caption{Limitaciones Metodológicas Identificadas}
\label{tab:latex_limitaciones}
\begin{tabular}{|l|c|p{5cm}|}
\hline
\textbf{Limitación} & \textbf{Impacto} & \textbf{Descripción} \\
\hline
Automatización insuficiente & Alto & Manual Analysis prevalece en granularidad (61.6\%) \\
\hline
Baja relevancia granular & Medio & 0.48 vs 0.52 (binario) \\
\hline
Cobertura incompleta & Alto & 76.6\% sin intención detectada \\
\hline
Métodos especializados & Medio & Sin solución universal \\
\hline
Integración emocional & Medio-Alto & Solo 2.3\% integra emoción \\
\hline
\end{tabular}
\end{table}
"""
    return latex

def main():
    print("Generando tablas en formato LaTeX para Overleaf...")
    data = load_data()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("% ============================================================\n")
        f.write("% TABLAS EN FORMATO LATEX - PARA COMPILACION DIRECTA EN OVERLEAF\n")
        f.write("% ============================================================\n\n")

        f.write("\\usepackage{float}  % Para [H] positioning\n")
        f.write("\\usepackage{array}  % Para tablas avanzadas\n\n")

        f.write(tabla_distribuciones(data))
        f.write(tabla_temporal(data))
        f.write(tabla_plataformas(data))
        f.write(tabla_limitaciones(data))

        f.write("\n% ============================================================\n")
        f.write("% FIN DE TABLAS\n")
        f.write("% ============================================================\n")

    print(f"OK: Tablas LaTeX guardadas en {OUTPUT_FILE}")
    print(f"Tamaño: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")

if __name__ == "__main__":
    main()
