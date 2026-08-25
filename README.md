# Identificación Granular de Intenciones Comunicativas en Publicaciones Digitales
## Una Revisión Sistemática de Literatura Asistida por LLM (2020–2026)

**Autor:** Luis Rojas Rubio  
**Afiliación:** Doctorado en Informática, Universidad Americana de Europa   
**Estado:** Paper en revisión  
**Dashboard:** https://revisionsistematicaprismafakenews.streamlit.app/
---

## Descripción

Este repositorio contiene todos los artefactos reproducibles de una Revisión Sistemática de Literatura (RSL) que identifica y clasifica las **intenciones comunicativas granulares** (más allá de la detección binaria real/fake) en publicaciones digitales, con foco en el período 2020–2026.

El pipeline combina búsqueda en 6 bases de datos, deduplicación, y clasificación semántica asistida por **Claude Sonnet 5** en dos etapas (metadatos + texto completo), siguiendo el protocolo **PRISMA 2020**.

---

## Resultados Clave

| Métrica | Valor |
|---------|-------|
| Artículos identificados (6 BD) | 3.575 |
| Elegibles tras cribado Etapa 2 | 373 |
| PDFs analizados (Etapa 3) | 549 |
| **Corpus final incluido** | **324** |
| Dimensiones de intención comunicativa | 13 |
| Período cubierto | 2020–2026 |
| Preguntas de investigación | 9 PI |

---

## Estructura del Repositorio

```
├── paper/                          # Paper LaTeX completo
│   ├── mainv9.tex                  # Versión actual (onecolumn, journal)
│   ├── references.bib              # Bibliografía BibTeX
│   ├── validacion_doble_ciego.txt  # Muestra inter-evaluador n=30
│   ├── th9_subcategorias.json      # Subcategorías dimensión TH9
│   └── *.txt                       # Secciones del paper en texto plano
│
├── figuras/                        # Figuras del paper (PNG)
│   ├── 01_metodos_especificos.png
│   ├── 02_intenciones.png
│   ├── 03_relevancia.png
│   ├── 04_tendencia_temporal.png
│   └── 05_metodos_generales.png
│
├── pipeline/
│   ├── fase1/                      # Extracción de texto desde PDFs
│   ├── fase2/                      # Clasificación semántica con LLM (metadatos)
│   └── analisis/                   # Síntesis, tablas y reportes
│
├── tablas/                         # 22 JSON de síntesis estadística
│
├── prisma/                         # Documentación PRISMA 2020
│   ├── Etapa 2/                    # Resultados por base de datos (×6)
│   ├── Etapa 3/                    # Corpus deduplicado
│   ├── *_GENERADO.xlsx             # Excel PRISMA generados automáticamente
│   └── generar_*.py                # Scripts generadores de Excel
│
├── docs/                           # Documentación y análisis
│   ├── ANALISIS_POLARIDAD_vs_GRANULARIDAD.md
│   ├── RESPUESTAS_PREGUNTAS_INVESTIGACION.md
│   ├── TABLAS_README.md
│   └── ...
│
├── clasificacion_claude.json       # Resultados Etapa 2 (3.575 artículos, 4.5 MB)
├── clasificacion_pdfs_completos.json  # Resultados Etapa 3 (549 artículos, 1.7 MB)
├── fase2_relevancia_alta.json      # Corpus incluido E3 (324 artículos)
├── fase2_relevancia_baja.json      # Corpus excluido E3 (225 artículos)
└── sintesis_hallazgos_revision.json
```

---

## Pipeline de Clasificación

```
6 Bases de Datos (Scopus, WoS, ACM, IEEE, Scholar, SciELO)
        │
        ▼
Búsqueda + Deduplicación → 3.575 artículos (AllDeduplicated.json)
        │
        ▼ Etapa 2: Cribado semántico de metadatos (Claude Sonnet 5)
373 elegibles / 3.202 excluidos (clasificacion_claude.json)
        │
        ▼ Descarga de PDFs (acceso institucional + open access)
549 PDFs obtenidos
        │
        ▼ Etapa 3: Análisis de texto completo (Claude Sonnet 5)
324 INCLUIDOS / 225 excluidos (clasificacion_pdfs_completos.json)
        │
        ▼ Síntesis cuantitativa
tablas/*.json + figuras/*.png → paper/mainv9.tex
```

---

## Reproducibilidad

### Requisitos

```bash
pip install anthropic openpyxl pymupdf pdfplumber streamlit
```

Se requiere acceso a la **Claude API** o **Claude CLI** (`claude`) para ejecutar los scripts de clasificación.

### Ejecución del pipeline (orden)

```bash
# Etapa 1: Extraer texto de PDFs (requiere pdfs/ en workspace)
py pipeline/fase1/fase1_extraccion_pdfs_final.py

# Etapa 2: Clasificación semántica de metadatos
py pipeline/fase2/clasificar_claude_cli.py

# Etapa 3: Clasificación de texto completo
py pipeline/fase2/procesar_pdfs_clasificacion_v3.py

# Síntesis: generar tablas JSON
py pipeline/analisis/generar_tablas_json.py

# PRISMA: generar Excel de documentación
py prisma/generar_screening_decisions.py
py prisma/generar_data_extraction_form.py
py prisma/generar_verification_log.py
py prisma/generar_ambiguous_cases.py
py prisma/generar_author_contact_log.py

# Visualización interactiva (Streamlit)
https://revisionsistematicaprismafakenews.streamlit.app/
py -m streamlit run pipeline/fase2/visor_fase2.py
```

> **Nota sobre los PDFs:** Los PDFs originales (549 artículos, ~1.3 GB) no se distribuyen en este repositorio por derechos de autor de las editoriales. Los resultados de clasificación completos están disponibles en `clasificacion_pdfs_completos.json`.

---

## Tablas de Síntesis (`tablas/`)

| Archivo | Contenido |
|---------|-----------|
| `01_distribuciones_agregadas.json` | Distribución de métodos e intenciones en el corpus |
| `02_cruzada_metodo_intencion.json` | Tabla cruzada método × intención |
| `03_evolucion_temporal.json` | Tendencia temporal 2020–2026 |
| `04_resumen_agregado.json` | Estadísticas resumen del corpus |
| `05_detecciones_agregadas.json` | Detecciones por categoría |
| `06_clusters_metodo.json` | Clusters de métodos similares |
| `07_clusters_intencion.json` | Clusters de co-ocurrencia de intenciones |
| `08_indice_referencias.json` | Índice bibliográfico del corpus |
| `09_caracteristicas_linguisticas.json` | Idioma y plataforma por artículo |
| `10_plataformas.json` | Distribución de plataformas estudiadas |
| `11_limitaciones_documentadas.json` | Limitaciones metodológicas del corpus |
| `12_hallazgos_nuevos.json` | Hallazgos emergentes |
| `13_datasets_referencias.json` | Datasets utilizados en el corpus |

Los archivos `*_h.json` son versiones con cabeceras expandidas para facilitar la lectura.

---

## Documentación PRISMA 2020

| Documento | Descripción |
|-----------|-------------|
| `SCREENING_DECISIONS_GENERADO.xlsx` | Decisiones de cribado: 3.575 → 373 → 324 |
| `DATA_EXTRACTION_FORM_GENERADO.xlsx` | Extracción de datos: 324 artículos × 7 dimensiones |
| `VERIFICATION_LOG_GENERADO.xlsx` | Validación inter-evaluador: κ=0.113, κw=0.229 (n=30) |
| `AMBIGUOUS_CASES_LOG_GENERADO.xlsx` | Casos ambiguos: borde, casi-elegibles, discrepancias E2→E3 |
| `AUTHOR_CONTACT_LOG_GENERADO.xlsx` | Contacto a autores para obtención de texto completo |

---

## Las 13 Dimensiones de Intención Comunicativa

El pipeline identifica las siguientes categorías granulares:

1. **I1** Fake News / Desinformación
2. **I2** Propaganda / Manipulación
3. **I3** Clickbait / Enganche emocional
4. **I4** Sátira / Parodia
5. **I5** Rumor / Especulación
6. **I6** Verificación de hechos (Fact-checking)
7. **I7** Sesgo mediático / Framing
8. **I8** Manipulación emocional
9. **I9** Intención neutra / Informativa
10. **I10** Desinformación de salud
11. **I11** Desinformación política
12. **I12** Intención de impersonación
13. **TH9** Subcategorías adicionales (granularidad extendida)

---

## Criterios de Inclusión/Exclusión (SPIDER)

Los criterios formalizados están en `prisma/CriterioScreaning.json`.

**Umbral de relevancia LLM:** ≥ 0.40 (escala 0–1)  
**Período:** 2020–2026  
**Requisitos:** presencia de al menos 1 intención comunicativa + 1 método NLP/ML  

---

## Cita

```bibtex
@article{rojas2026rsl,
  title   = {Identificación Granular de Intenciones Comunicativas en Publicaciones
             Digitales: Una RSL Asistida por LLM (2020--2026)},
  author  = {Rojas Rubio, Luis},
  journal = {[Revista por confirmar]},
  year    = {2026},
  note    = {En revisión}
}
```

---

## Licencia

El código de este repositorio se distribuye bajo licencia **MIT**.  
Los datos de clasificación (`clasificacion_*.json`, `tablas/`) se distribuyen bajo **CC BY 4.0**.  
Los PDFs originales de los artículos **no se distribuyen** (sujetos a derechos de autor de las editoriales).
