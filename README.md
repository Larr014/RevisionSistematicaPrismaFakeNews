# Identificación Granular de Intenciones Comunicativas en Publicaciones Digitales
## Una Revisión Sistemática de Literatura Asistida por LLM (2021–2026)

**Autor:** Luis Rojas Rubio  
**Afiliación:** Doctorado en Informática, Universidad Americana de Europa   
**Estado:** Paper en revisión  
**Dashboard:** https://revisionsistematicaprismafakenews.streamlit.app/
---

## Descripción

Este repositorio contiene todos los artefactos reproducibles de una Revisión Sistemática de Literatura (RSL) que identifica y clasifica las **intenciones comunicativas granulares** (más allá de la detección binaria real/fake) en publicaciones digitales, con foco en el período 2021–2026.

El pipeline combina búsqueda en 6 bases de datos (4–6 de abril de 2026), deduplicación, y clasificación asistida por **Claude Sonnet 5** en dos etapas (cribado de metadatos: abril de 2026; texto completo: julio de 2026), siguiendo el protocolo **PRISMA 2020**. La puntuación de relevancia (≥ 0.4) se aplica solo en la etapa de texto completo.

---

## Resultados Clave

| Métrica | Valor |
|---------|-------|
| Registros exportados (6 BD) | 4.073 |
| Tras duplicados dentro de cada base | 3.708 |
| Registros únicos (duplicados entre bases: 133) | 3.575 |
| Elegibles tras cribado de metadatos (Etapa 2) | 643 |
| Textos completos obtenidos y analizados (Etapa 3) | 549 (94 no obtenidos) |
| **Corpus final incluido (relevancia ≥ 0.4)** | **324** |
| Dimensiones de intención comunicativa | 13 |
| Período cubierto | 2021–2026 |
| Preguntas de investigación | 9 PI |

> Las exportaciones por base fueron: Scopus 1.051, Web of Science 1.026, ACM 1.375, IEEE Xplore 202, Google Scholar 200 y SciELO 219. En las iteraciones con exceso de resultados (Scopus, WoS y ACM, iteración 2) se exportaron los 1.000 primeros por relevancia.
> Los 9 artículos de 2020 del corpus incluido (324) corresponden a versiones previas (preprints) de trabajos publicados desde 2021, obtenidas mediante herramientas de acceso abierto.

---

## Estructura del Repositorio

```
├── paper/                          # Paper LaTeX
│   ├── mainv11.tex                 # Versión actual
│   └── references.bib              # Bibliografía BibTeX
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
│   ├── 0 SEARCH_QUERY_ITERATIONS.xlsx  # Cadenas, fechas y resultados por iteración
│   ├── 1 SEARCH_RESULTS_LOG.xlsx   # Registros por base (únicos dentro de cada base)
│   ├── Etapa 2/                    # Registros por base tras fusionar iteraciones (×6)
│   ├── Etapa 3/                    # Corpus deduplicado entre bases (3.575)
│   ├── *_GENERADO.xlsx             # Excel PRISMA generados automáticamente
│   └── generar_*.py                # Scripts generadores de Excel
│
├── docs/                           # Documentación y análisis
│   ├── ANALISIS_POLARIDAD_vs_GRANULARIDAD.md
│   ├── RESPUESTAS_PREGUNTAS_INVESTIGACION.md
│   ├── TABLAS_README.md
│   └── ...
│
├── clasificacion_claude.json       # Resultados Etapa 2: cribado de metadatos (3.575 artículos, 4.5 MB)
├── clasificacion_pdfs_completos.json  # Resultados Etapa 3: texto completo (549 artículos, 1.7 MB)
├── fase2_relevancia_alta.json      # Corpus incluido E3 (324 artículos)
├── fase2_relevancia_baja.json      # Corpus excluido E3 (225 artículos)
└── sintesis_hallazgos_revision.json
```

---

## Pipeline de Clasificación

```
6 Bases de Datos (Scopus, WoS, ACM, IEEE, Scholar, SciELO) — 4.073 registros exportados
        │
        ▼ Duplicados dentro de cada base (365) → 3.708
        ▼ Duplicados entre bases, Zotero por DOI (133) → 3.575 (prisma/Etapa 3/AllDeduplicated.json)
        │
        ▼ Etapa 2: Cribado de metadatos (Claude Sonnet 5, título + resumen + keywords)
        │   Elegible = método NLP/ML + intención comunicativa + año ≥ 2021 (sin umbral de relevancia)
643 elegibles / 2.932 excluidos (clasificacion_claude.json; pipeline/analisis/filtrar_articulos.py)
        │
        ▼ Obtención de texto completo (APIs de acceso abierto, acceso institucional, descarga manual, solicitud al autor)
549 textos completos obtenidos / 94 no obtenidos
        │
        ▼ Etapa 3: Análisis de texto completo (Claude Sonnet 5, primeros 12.000 caracteres)
        │   Relevancia 0–1; se incluye con relevancia ≥ 0.4
324 INCLUIDOS / 225 excluidos (clasificacion_pdfs_completos.json)
        │
        ▼ Síntesis cuantitativa
tablas/*.json + figuras/*.png → paper/mainv11.tex
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
py -m streamlit run app.py
```

> **Nota sobre los PDFs:** Los PDFs originales (549 artículos, ~1.3 GB) no se distribuyen en este repositorio por derechos de autor de las editoriales. Los resultados de clasificación completos están disponibles en `clasificacion_pdfs_completos.json`.

---

## Tablas de Síntesis (`tablas/`)

| Archivo | Contenido |
|---------|-----------|
| `01_distribuciones_agregadas.json` | Distribución de métodos e intenciones en el corpus |
| `02_cruzada_metodo_intencion.json` | Tabla cruzada método × intención |
| `03_evolucion_temporal.json` | Tendencia temporal 2021–2026 |
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
| `SCREENING_DECISIONS_GENERADO.xlsx` | Decisiones de cribado: 4.073 → 3.575 → 643 → 549 → 324 |
| `DATA_EXTRACTION_FORM_GENERADO.xlsx` | Extracción de datos: 324 artículos × 7 hojas temáticas (índice, métodos, intenciones, datasets, métricas, contexto, hallazgos) |
| `VERIFICATION_LOG_GENERADO.xlsx` | Validación inter-evaluador (n=30): acuerdo exacto 40 %, κ=0.053, κw=0.174 |
| `AMBIGUOUS_CASES_LOG_GENERADO.xlsx` | Casos ambiguos: borde, casi-elegibles, discrepancias E2→E3 |
| `AUTHOR_CONTACT_LOG_GENERADO.xlsx` | Contacto a autores para obtención de texto completo (cronología parcialmente verificada; ver hoja 3_Timeline) |

---

## Las 13 Dimensiones de Intención Comunicativa

El vocabulario inicial del pipeline fue I1–I7 (Fake News, Manipulación, Persuasión, Clickbait, Polarización, Emoción, Conspiración). El análisis de texto completo y el campo `hallazgos_nuevos` permitieron consolidar *post-hoc* 13 dimensiones en tres grupos:

| Grupo | Dimensiones |
|-------|-------------|
| Desinformación estructural | Fake News, Desinformación, Evaluación de Credibilidad, Rumores, Sátira |
| Intenciones de impacto | Manipulación, Emociones, Polaridad, Contenido Tóxico |
| Comportamiento coordinado | Actividad de Bots, Deepfakes, Comportamiento Coordinado, Actividad Sospechosa |

---

## Criterios de Elegibilidad y Relevancia

**Etapa 2 (metadatos).** Elegible si cumple las tres condiciones: al menos 1 método NLP/ML identificado, al menos 1 intención comunicativa identificada y año de publicación ≥ 2021. El modelo también asigna una puntuación de relevancia, pero no se usa como criterio de exclusión en esta etapa.

**Etapa 3 (texto completo).** El modelo puntúa la relevancia de 0 a 1 (1.0 identifica intenciones directamente; 0.7 NLP o análisis de contenido digital; 0.4 NLP/ML general; 0.1 sin relación con el dominio). Umbral de inclusión: **≥ 0.4**.

`prisma/CriterioScreaning.json` conserva la especificación de cribado del protocolo; los criterios efectivamente aplicados son los descritos arriba y en el paper.

---

## Cita

```bibtex
@article{rojas2026rsl,
  title   = {Identificación Granular de Intenciones Comunicativas en Publicaciones
             Digitales: Una RSL Asistida por LLM (2021--2026)},
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
