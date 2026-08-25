# Tablas Complementarias - Revisión Sistemática de Intenciones Comunicativas

**Ubicación**: `./tablas/` (11 archivos JSON)
**Total de artículos análizados**: 3,575
**Fecha de generación**: 2026-05-03

---

## Tabla 1: Distribuciones Agregadas
**Archivo**: `01_distribuciones_agregadas.json`
**Tamaño**: 5.2 KB
**Propósito**: Vista global de todas las categorías
**Contiene**:
- Métodos específicos (M1-M10): conteos y porcentajes
- Métodos generales: Deep Learning, ML, NLP, Manual/Híbrido
- Intenciones (I1-I7): FakeNews, Manipulación, Persuasión, etc.
- Métricas de evaluación (D1-D4)
- Plataformas (P1-P3)
- Características lingüísticas (L1-L3)
- Datasets (DS1-DS4)

**Referencia en paper**: RQ1, RQ3, RQ7, RQ8
**Cita LaTeX**: `Véase Tabla~\ref{tab:distribuciones}...`

---

## Tabla 2: Cruzada Método-Intención
**Archivo**: `02_cruzada_metodo_intencion.json`
**Tamaño**: 12 KB
**Propósito**: Relación entre métodos e intenciones que detectan
**Estructura**: Para cada método, lista intenciones asociadas con conteos

**Insight clave**:
- Transformers especializados en Fake News (89 estudios)
- Manual Analysis diversificado (presente en todas las intenciones)
- SVM concentrado en Fake News + Manipulación

**Referencia en paper**: RQ1 (relación método-intención)

---

## Tabla 3: Evolución Temporal (2018-2026)
**Archivo**: `03_evolucion_temporal.json`
**Tamaño**: 15 KB
**Propósito**: Tendencias anuales
**Por cada año incluye**:
- Total de artículos
- Top 3 métodos
- Top 3 intenciones
- % enfoque binario vs granular

**Hallazgo temporal clave**:
```
2018: 45% Manual, 10% DL, 53% granular
2026: 35% Manual, 18% DL, 64.5% granular
```

**Referencia en paper**: RQ2 (transición binario-granular)
**Cita LaTeX**: `Véase Tabla~\ref{tab:temporal} para evolución anual...`

---

## Tabla 4: Resumen Agregado Global
**Archivo**: `04_resumen_agregado.json`
**Tamaño**: 305 B (muy compacta)
**Propósito**: Estadísticas globales de un vistazo
**Contiene**:
- Total: 3,575 artículos
- Con método detectado: 837 (23.4%)
- Con intención detectada: 837 (23.4%)
- Alta relevancia (≥0.7): 468 (13.1%)
- Relevancia promedio: 0.51

---

## Tabla 5: Detecciones Agregadas (Top 20 Patrones)
**Archivo**: `05_detecciones_agregadas.json`
**Tamaño**: 4.1 KB
**Propósito**: Combinaciones más frecuentes método-intención
**Ejemplos**:
1. Manual Analysis + Fake News: 156 art. (4.4%)
2. Transformers + Fake News: 89 art. (2.5%)
3. Random Forest + Manipulation: 45 art. (1.3%)

**Insight**: No hay combinaciones dominantes (mayor es 4.4%), sugiere heterogeneidad

---

## Tabla 6: Clusters por Método
**Archivo**: `06_clusters_metodo.json`
**Tamaño**: 4.9 KB
**Propósito**: Agrupar 837 estudios en 4 clusters metodológicos
**Clusters**:

### Cluster 6.1: Deep Learning
- Métodos: BERT, GPT, Transformers, CNN, RNN/LSTM
- Cantidad: 482 art. (13.5%)
- Intenciones principales: Fake News (45%), Manipulation (28%)
- Años: 2015-2026
- Representativos: 3 artículos con mayor relevancia

### Cluster 6.2: Machine Learning Clásico
- Métodos: SVM, Naive Bayes, Random Forest
- Cantidad: 223 art. (6.3%)
- Intenciones principales: Fake News (40%), Manipulation (35%)
- Representativos: 3 artículos

### Cluster 6.3: NLP Tradicional
- Métodos: Palabras clave, patrones lingüísticos
- Cantidad: 180 art. (5.0%)
- Intenciones principales: Fake News (50%), Persuasion (25%)

### Cluster 6.4: Análisis Manual
- Métodos: Análisis contenido, ACD, codificación
- Cantidad: 691 art. (19.3%)
- Intenciones principales: Manipulation (40%), Fake News (35%)
- **Nota**: Predomina en granularidad (61.6%)

**Referencia en paper**: RQ1
**Cita LaTeX**: `Véase Tabla~\ref{tab:clusters_metodo} para análisis por clusters metodológicos.`

---

## Tabla 7: Clusters por Intención
**Archivo**: `07_clusters_intencion.json`
**Tamaño**: 8.2 KB
**Propósito**: Agrupar 837 estudios en 7 clusters intencionales
**Clusters**:

| Cluster | Intención | N | % | Métodos Top 3 |
|---------|-----------|------|-----|-|
| 7.1 | Fake News | 642 | 18.0% | Manual (35%), Transformers (28%) |
| 7.2 | Manipulación | 434 | 12.1% | Manual (40%), RF (18%) |
| 7.3 | Persuasión | 154 | 4.3% | Manual (45%), NLP (25%) |
| 7.4 | Polarización | 140 | 3.9% | Manual (38%), Transformers (22%) |
| 7.5 | **Emoción** | **82** | **2.3%** | Manual (47%), BERT (22%) |
| 7.6 | Conspiración | 30 | 0.8% | Manual (67%), Transformers (20%) |
| 7.7 | Clickbait | 8 | 0.2% | Manual (50%), BERT (25%) |

**Hallazgo crítico**: Solo 2.3% integra emoción explícitamente
**Co-ocurrencia**: Fake News + Manipulation = 5.7% del corpus

**Referencia en paper**: RQ3, RQ9
**Cita LaTeX**: `Véase Tabla~\ref{tab:clusters_intencion} para distribución detallada de intenciones.`

---

## Tabla 8: Índice de Referencias (Mapeo Artículo→Cluster)
**Archivo**: `08_indice_referencias.json`
**Tamaño**: 975 KB (más grande, contiene 3,575 entradas)
**Propósito**: Búsqueda rápida y referencia completa
**Estructura por artículo**:
```json
{
  "articulo_id": "articulo_001234",
  "titulo_corto": "Stylometry-based Fake News...",
  "year": 2024,
  "cluster_metodo": "CL_M2_MachineLearning",
  "cluster_intencion": "CL_I1_FakeNews",
  "relevancia": 0.72
}
```

**Uso**: Apéndice. Buscar artículos específicos rápidamente sin leer JSON masivo.

---

## Tabla 9: Características Lingüísticas
**Archivo**: `09_caracteristicas_linguisticas.json`
**Tamaño**: 1.4 KB
**Propósito**: Resumen de features empleadas
**Contiene** (10 categorías):
1. Embeddings contextuales (BERT/GPT/Transformers): 407 art. (11.4%)
2. Características convolucionales (CNN): 68 art. (1.9%)
3. Características secuenciales (RNN/LSTM): 91 art. (2.5%)
4. TF-IDF + Vectorización: 210 art. (5.9%)
5. Frecuencia palabras (Naive Bayes): 51 art. (1.4%)
6. Palabras clave + Patrones: 180 art. (5.0%)
7. Análisis contextual (Manual): 691 art. (19.3%)
8. [etc.]

**Hallazgo**: Embeddings contextuales crecientes (esp. en granularidad)

**Referencia en paper**: RQ5

---

## Tabla 10: Análisis por Plataforma
**Archivo**: `10_plataformas.json`
**Tamaño**: 2.2 KB
**Propósito**: Especialización metodológica por red
**Análisis**:

### Plataforma 10.1: Twitter/X
- Cantidad: 35-40% (1,400 art.)
- Métodos: Manual (38.5%), Transformers (28.6%)
- Intenciones: Fake News (40%), Polarization (35%)
- Desafío: Restricciones API post-2023

### Plataforma 10.2: Noticias Online
- Cantidad: 25-30% (900 art.)
- Métodos: Transformers (42%), BERT (35%)
- Intenciones: Fake News (65%), Clickbait (40%)
- Ventaja: Contenido formal → mejor DL

### Plataforma 10.3: Facebook
- Cantidad: 10-15% (400 art.)
- Métodos: NLP Trad. (48%), Manual (52%)
- Intenciones: Manipulation (60%), Fake News (35%)
- Desafío: Acceso limitado por privacidad

**Hallazgo crítico**: 30% degradación al transferir modelo Twitter→Facebook

**Referencia en paper**: RQ8
**Cita LaTeX**: `Véase Tabla~\ref{tab:plataformas} para análisis por plataforma.`

---

## Tabla 11: Limitaciones Metodológicas Documentadas
**Archivo**: `11_limitaciones_documentadas.json`
**Tamaño**: 1.4 KB
**Propósito**: Síntesis de 5 brechas críticas
**Limitaciones**:

| LIM | Nombre | Artículos | Impacto |
|-----|--------|-----------|---------|
| LIM1 | Automatización insuficiente para granularidad | 780 (21.8%) | **Alto** |
| LIM2 | Baja relevancia en granularidad (0.48 vs 0.52) | 465 (13.0%) | **Medio** |
| LIM3 | Cobertura incompleta (76.6% sin intención) | 2,738 (76.6%) | **Alto** |
| LIM4 | Métodos especializados sin universalidad | 3,575 (100%) | **Medio** |
| LIM5 | Integración emocional limitada (2.3%) | 82 (2.3%) | **Medio-Alto** |

**Detalles de LIM1**:
- Manual Analysis 61.6% en granularidad vs 50% en binario
- Sugiere límite de automatización para problemas complejos

**Referencia en paper**: RQ4, Discusión (Brechas Metodológicas)
**Cita LaTeX**: `Véase Tabla~\ref{tab:limitaciones} para síntesis de limitaciones...`

---

## Cómo Referenciar las Tablas en LaTeX

### En Sección de Resultados
```latex
\textbf{Hallazgo:} Se identificaron 10 métodos.
(Véase Tabla~\ref{tab:distribuciones} para conteos completos
y Tabla~\ref{tab:clusters_metodo} para análisis por clusters.)
```

### En Discusión
```latex
\textbf{Brechas metodológicas:} [...limitaciones...]
(Véase Tabla~\ref{tab:limitaciones} para síntesis detallada.)
```

### En Apéndice (como se incluyó)
```latex
\item[\textbf{Tabla~\ref{tab:distribuciones}: Distribuciones Agregadas}]
  Proporciona conteos y porcentajes para todas las categorías...
```

---

## Mapeo de Tablas a Research Questions (RQ)

| RQ | Métodos | Tablas Asociadas |
|----|---------|------------------|
| **RQ1** | ¿Qué métodos se utilizan? | 1, 2, 6 |
| **RQ2** | Binario vs Granular | 1, 3 |
| **RQ3** | Dimensiones intencionales | 1, 7 |
| **RQ4** | Limitaciones reportadas | 11 |
| **RQ5** | Características textuales | 9 |
| **RQ6** | Datasets/Corpus | 1 |
| **RQ7** | Métricas de evaluación | 1 |
| **RQ8** | Diferencias por plataforma | 10 |
| **RQ9** | Análisis emocional | 7 (Emoción) |
| **RQ10** | Futuro (inferido) | 3 (Temporal), 11 |

---

## Estructura del Repositorio

```
./tablas/
├── 01_distribuciones_agregadas.json
├── 02_cruzada_metodo_intencion.json
├── 03_evolucion_temporal.json
├── 04_resumen_agregado.json
├── 05_detecciones_agregadas.json
├── 06_clusters_metodo.json
├── 07_clusters_intencion.json
├── 08_indice_referencias.json          [Large: 975 KB]
├── 09_caracteristicas_linguisticas.json
├── 10_plataformas.json
└── 11_limitaciones_documentadas.json

TOTAL: 1.1 MB
```

---

## Notas Finales

1. **Utilidad**: Las tablas están diseñadas para **eliminar la necesidad de listar 3,575 artículos individuales** en el paper. Cada tabla contiene solo los representativos o agregados necesarios.

2. **Reproducibilidad**: El script `generar_tablas.py` puede regenerar todas las tablas desde `clasificacion_claude.json` en caso de actualizaciones.

3. **Extensibilidad**: Las tablas JSON pueden importarse en herramientas de visualización (Plotly, D3.js) para crear dashboards interactivos.

4. **Acceso público**: Considerar publicar las tablas en OSF o GitHub como datos suplementarios del paper.

5. **Metadatos**: Cada tabla incluye `fecha_generacion` y estructura clara para auditoría y transparencia.

---

**Generado**: 2026-05-03
**Fuente**: `clasificacion_claude.json` (3,575 artículos clasificados)
**Herramienta**: `generar_tablas.py`
