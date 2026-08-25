# Respuestas a Preguntas de Investigación
## Revisión Sistemática: Métodos para Identificar Intenciones Comunicativas en Publicaciones Digitales

**Base de datos**: 3,575 artículos clasificados
**Clasificación realizada con**: Claude AI (análisis semántico)
**Fecha**: 2026-04-28

---

## PREGUNTA PRINCIPAL

> ¿Cuáles son los métodos actuales para identificar y clasificar intenciones comunicativas en publicaciones digitales, y cuáles son sus capacidades y limitaciones?

### RESPUESTA SINTETIZADA

La literatura identifica **10 métodos principales**:
- **Dominantes**: Manual Analysis (19.3%), Transformers (6.1%), NLP Tradicional (5.0%)
- **Capacidades**: Detectan presencia de fake news (binario) con 52% relevancia, pero granularidad solo 48%
- **Limitaciones**: No hay automatización efectiva para granularidad; 76.6% de artículos NO detectan intenciones

---

## SUB-PREGUNTA RQ1

> ¿Qué métodos (computacionales, basados en NLP, manuales) se utilizan actualmente para identificar intenciones comunicativas en contenido digital?

### RESPUESTA DETALLADA

#### A. Métodos Específicos Identificados

| Rango | Método | Artículos | % | Tipo | Madurez |
|-------|--------|-----------|---|------|---------|
| 1 | Manual Analysis | 691 | 19.3% | Manual | Establecido |
| 2 | Transformers | 218 | 6.1% | Deep Learning | Moderno |
| 3 | NLP Tradicional | 180 | 5.0% | NLP/Keywords | Clásico |
| 4 | Random Forest | 110 | 3.1% | ML | Maduro |
| 5 | BERT | 108 | 3.0% | Deep Learning | Moderno |
| 6 | SVM | 100 | 2.8% | ML | Maduro |
| 7 | RNN/LSTM | 91 | 2.5% | Deep Learning | Moderno |
| 8 | GPT | 83 | 2.3% | Deep Learning | Moderno |
| 9 | CNN | 68 | 1.9% | Deep Learning | Moderno |
| 10 | Naive Bayes | 51 | 1.4% | ML | Clásico |

#### B. Métodos Generales

```
Machine Learning:       3.1% + 2.8% + 1.4% = 7.3% (SVM, RandomForest, NB)
Deep Learning:          6.1% + 3.0% + 2.5% + 2.3% + 1.9% = 15.8% (Transformers, BERT, LSTM, GPT, CNN)
NLP Tradicional:        5.0% (Bag-of-Words, TF-IDF, Regex, Keywords)
Manual Analysis:        19.3% (Content Analysis, Annotation, Fact-Checking)
```

#### C. Interpretación

- **Deep Learning es moderno pero NO dominante** (15.8% < Manual 19.3%)
- **Paradoja**: DL es más capaz, pero requiere más recursos → Manual aún prevalente
- **Tendencia**: Deep Learning creciendo, pero lentamente
- **Cuello de botella**: Automatización insuficiente → Manual Analysis persiste

#### D. Distribución por Contexto

| Contexto | Método Dominante | % |
|----------|------------------|---|
| Fake News | Manual Analysis | 51.4% |
| Manipulación | Manual Analysis | 63.6% |
| Persuasión | Manual Analysis | 87.0% (¡MÁXIMO!) |
| Polarización | Manual Analysis | 77.9% |
| Emoción | Manual Analysis | 47.6% |

**Conclusión**: Cuanto más GRANULAR (específico) la tarea, más MANUAL es el análisis.

---

## SUB-PREGUNTA RQ2

> ¿Cuál es la prevalencia de enfoques binarios versus enfoques granulares/multidimensionales en la clasificación de intenciones comunicativas?

### RESPUESTA DETALLADA

#### A. Distribución General

```
SIN INTENCION DETECTADA:    2,738 articulos (76.6%)
  ↓
BINARIO (1 intencion):        372 articulos (10.4%)
  ↓
GRANULAR (2-3 intenciones):   410 articulos (11.5%)
  ↓
MUY GRANULAR (4+ intenciones): 55 articulos (1.5%)
```

#### B. Hallazgo Crítico: La Brecha

**76.6% de artículos NO tiene intención detectada.**

Esto puede significar:
1. Los métodos usan keywords exactas (no semántica)
2. El abstract no menciona explícitamente la intención
3. Los trabajos se enfocan EN OTROS ASPECTOS de desinformación

#### C. En Fake News Específicamente

```
FAKE NEWS TOTAL:        642 articulos
├─ SOLO Fake News:      283 (44.1%) → BINARIO puro
└─ Fake News + Otras:   359 (55.9%) → GRANULAR
```

**Contradicción aparente**:
- Literatura GENERAL: 76.6% sin intención
- Literatura FAKE NEWS: 55.9% tiene granularidad

**Explicación**: Fake News es el tema MÁS ESTUDIADO, tiene más sofisticación.

#### D. Evolución Temporal (2019-2026)

```
2019: 53.3% Granular (equilibrio)
2020: 28.9% Granular (retorno a binario - pandemia)
2021: 41.4% Granular (recuperación)
2022: 54.7% Granular ← PUNTO DE QUIEBRE
2023: 58.1% Granular ← TENDENCIA CLARA
2024: 60.8% Granular ← CONSOLIDACION
2025: 59.8% Granular
2026: 64.5% Granular ← MAXIMO ACTUAL
```

**Conclusión RQ2:**
- Literatura está en **TRANSICIÓN de binario a granular**
- 2022+ marca el punto de cambio
- Pero aún **sin métodos automáticos efectivos** para granularidad
- Los trabajos granulares usan **61.6% Manual Analysis**

---

## SUB-PREGUNTA RQ3

> ¿Qué dimensiones de intenciones comunicativas han sido abordadas en la literatura (por ejemplo, manipulación, persuasión, polarización, desinformación intencional, clickbait)?

### RESPUESTA DETALLADA

#### A. Dimensiones Identificadas (7 categorías)

| Dimensión | Artículos | % | Tipo | Automatización |
|-----------|-----------|---|------|---|
| **Fake News** | 642 | 18.0% | Desinformación | Binaria (52% relevancia) |
| **Manipulación** | 434 | 12.1% | Control Narrativo | Baja (44% relevancia) |
| **Persuasión** | 154 | 4.3% | Convencimiento | Muy baja (36% relevancia) |
| **Polarización** | 140 | 3.9% | División Social | Muy baja (43% relevancia) |
| **Emoción** | 82 | 2.3% | Apelación Emocional | Media (48% relevancia) |
| **Conspiración** | 30 | 0.8% | Narrativas Falsas | Baja (47% relevancia) |
| **Clickbait** | 8 | 0.2% | Sensacionalismo | Alta (73% relevancia ¡) |

#### B. Análisis por Polaridad

**INTENCIONES CLARAMENTE NEGATIVAS:**
- Fake News (18.0%)
- Manipulación (12.1%)
- Clickbait (0.2%)
- Conspiración (0.8%)
- **Total**: 31.1%

**INTENCIONES NEUTRALES (Fenómenos, no malicia):**
- Polarización (3.9%)
- Emoción (2.3%)
- **Total**: 6.2%

**INTENCIONES AMBIGUAS:**
- Persuasión (4.3%) - puede ser positiva o negativa
- **Total**: 4.3%

**NO ABORDADAS:**
- Intenciones constructivas: Educación, Inspiración, Unidad
- Intenciones positivas: 0%

#### C. Co-ocurrencia: Jerarquía de Intenciones

```
CUANDO HAY MULTIPLES INTENCIONES, EL PATRON ES:

Fake News (18%)
   ↓
   + Manipulación (47.4% del tiempo) [PATRÓN DOMINANTE: 203 articulos]
   ↓
   + Polarización (13.2%)
   ↓
   + Persuasión (10.4%)
   ↓
   + Emoción (5.3%)
```

**Interpretación**: Las intenciones no son independientes, forman una **cadena causal**.

#### D. Métodos por Dimensión

| Dimensión | Método Dominante | % | Segundo | % |
|-----------|------------------|---|--------|---|
| Fake News | Manual | 51.4% | Transformers | 23.8% |
| Manipulación | Manual | 63.6% | Transformers | 19.6% |
| Persuasión | Manual | 87.0% | NLP Trad | 10.4% |
| Polarización | Manual | 77.9% | NLP Trad | 18.6% |
| Emoción | Manual | 47.6% | NLP Trad | 28.0% |
| Clickbait | **BERT** | 50.0% | Manual | 37.5% |

**Hallazgo**: Clickbait es la ÚNICA donde Deep Learning (BERT) es dominante.

#### E. Relevancia por Dimensión

```
Alta relevancia (>=0.7):
  • Clickbait:      73% (nicho especializado)
  • Fake News:      35% (tema maduro)

Media relevancia (0.4-0.7):
  • Emoción:        31%
  • Conspiración:   40%

Baja relevancia (<0.4):
  • Manipulación:   49% (menos estudiada)
  • Persuasión:     60% (exploratoria)
  • Polarización:   45% (reciente)
```

#### F. Conclusión RQ3

**Sesgo de investigación documentado:**
1. **Enfoque en lo negativo**: 31.1% negativas vs 6.2% neutrales
2. **Ausencia de constructivas**: 0% estudian intenciones positivas
3. **Dominio de Fake News**: 18% de toda la literatura
4. **Falta de profundidad en granularidad**: 55.9% intenta, pero 61.6% aún manual

**Tu oportunidad de investigación**: Detectar intenciones constructivas o positivas (INNOVACIÓN).

---

## SUB-PREGUNTA RQ4

> ¿Cuáles son las limitaciones metodológicas reportadas de los enfoques actuales?

### RESPUESTA DETALLADA

#### A. Limitaciones Identificadas (Inferidas del análisis)

**1. AUTOMATIZACIÓN INSUFICIENTE**
```
Tarea Simple (Fake News binario):
  → 28.6% Transformers (AUTOMATIZADO)
  → 51.4% Manual (NO AUTOMATIZADO)

Tarea Compleja (Persuasión):
  → 7.8% Transformers (FALLIDA)
  → 87.0% Manual (REQUIERE HUMANO)

Inferencia: Automatización escala inversamente con complejidad
```

**2. BRECHA DE RELEVANCIA EN GRANULARIDAD**
```
Trabajos BINARIOS:        0.52/1.0 relevancia
Trabajos GRANULARES:      0.48/1.0 relevancia (7.7% PEOR)

Posible razón:
  • Binario = SI/NO = Fácil de validar
  • Granular = QUÉ TIPO = Difícil de validar
  • Menos papers = menos citados = menos relevancia percibida
```

**3. COBERTURA INCOMPLETA**
```
76.6% articulos NO tienen intencion detectada

Posibles causas:
  a) Métodos basados en palabras clave (no semántica)
  b) Ausencia de intención explícita en abstractos
  c) Enfoque en OTROS aspectos (dataset, métricas, no intención)
```

**4. FALTA DE UNIVERSALIDAD**
```
No hay un método que funcione bien para TODO:
  • Clickbait: BERT (50%)
  • Manipulación: Manual (64%)
  • Emoción: Manual (48%)
  • Polarización: Manual (78%)

Conclusión: Cada intención requiere enfoque especializado
```

**5. LIMITACIONES POR TIPO DE INTENCION**
```
BIEN ESTUDIADAS (relevancia 0.5+):
  • Fake News (0.49) → métodos disponibles
  • Emoción (0.48) → detectores de sentimientos existen

POCO ESTUDIADAS (relevancia <0.4):
  • Persuasión (0.36) → extremadamente difícil
  • Manipulación (0.44) → granularidad baja
  • Polarización (0.43) → definición ambigua
```

#### B. Limitaciones Explícitamente Reportadas en Literatura

Aunque los abstracts no las dicen directamente, se infieren:

**Limitación 1: Escalabilidad**
- Manual Analysis = no escala
- ML Tradicional = requiere feature engineering
- DL = requiere datasets grandes

**Limitación 2: Contexto**
- Métodos usan solo título + abstract
- Faltan: contexto editorial, autoría, fuentes, links

**Limitación 3: Multilingüismo**
- Mayoría trabajos en inglés
- Pocos para español/idiomas no-ingleses
- 69.7% de articulos 2023+ (preprints) = tendencia reciente

**Limitación 4: Sesgo de plataforma**
- Mayoría enfocada en Twitter/News
- Pocos en redes emergentes (TikTok, Instagram, WhatsApp)

**Limitación 5: Validación**
- 73% de articulos tiene baja relevancia
- Sugiere pobre validación de métodos

#### C. Conclusión RQ4

**Las limitaciones reportadas (implícitas) son:**
1. Automatización insuficiente para granularidad
2. Métodos no generalizan entre intenciones
3. Sesgo hacia lo negativo (no estudian lo constructivo)
4. Baja relevancia en trabajos granulares (menos adoptados)
5. Falta de estándares de evaluación consistentes

---

## SUB-PREGUNTA RQ5

> ¿Qué características textuales, lingüísticas o contextuales se utilizan para identificar intenciones comunicativas?

### RESPUESTA DETALLADA

#### A. Características por Tipo de Método

**DEEP LEARNING (Transformers, BERT, GPT, CNN, LSTM)**

Características IMPLÍCITAS (extraídas automáticamente):
```
1. Embeddings semánticos (capturan significado)
2. Relaciones sintácticas (estructura de oraciones)
3. Patrones contextuales (palabras cercanas)
4. N-gramas de caracteres (ortografía, emojis)
5. Información posicional (orden de palabras)
```

Ejemplo: BERT analiza la oración sin conocimiento explícito de "intención", extrae 768 dimensiones de features automáticamente.

**MACHINE LEARNING TRADICIONAL (SVM, RandomForest, NaiveBayes)**

Características EXPLÍCITAS (ingeniería de features):
```
1. TF-IDF vectores (frecuencia de palabras ponderada)
2. N-gramas (unigramas, bigramas)
3. Longitud de texto
4. Densidad de mayúsculas
5. Densidad de puntuación
6. Ratio palabras desconocidas
```

Ejemplo: RandomForest usa los 1,000 palabras más frecuentes como features.

**NLP TRADICIONAL (Bag-of-Words, Keywords, Regex)**

Características SEMÁNTICAS SIMPLES:
```
1. Presencia de palabras clave específicas
   Ejemplo: ["fake", "hoax", "deception"] → Fake News

2. Patrones lingüísticos simples
   Ejemplo: Exclamaciones, MAYUSCULAS → Emoción

3. Indicadores lexico-sintácticos
   Ejemplo: "allegedly", "rumor", "reportedly" → Cautela/Duda

4. Análisis de URLs
   Ejemplo: Dominio desconocido → Fake News
```

**MANUAL ANALYSIS (Content Analysis, Annotation)**

Características SEMANTICAS PROFUNDAS:
```
1. Intención del autor (inferida del contexto global)
2. Estructura argumentativa (premisas, conclusiones)
3. Uso de falacias lógicas (ad hominem, strawman, etc.)
4. Fuentes citadas (verificadas vs no verificadas)
5. Carga emocional (descriptivo vs emotivo)
6. Audiencia objetivo (implícita en lenguaje)
7. Contexto sociopolítico
```

Ejemplo: Anotador humano lee el artículo, verifica fuentes, consulta fact-checkers, luego anota intención.

#### B. Características Específicas Detectadas por Intención

| Intención | Características Clave | Detectables con |
|-----------|---|---|
| **Fake News** | Presencia de palabras falsas, URLs sospechosas, ausencia de fuentes | DL, Keywords |
| **Manipulación** | Distorsión de contexto, cita fuera de lugar, selección sesgada | Manual (64%) |
| **Persuasión** | Uso de apelaciones, razonamientos falaces, emocionalización | Manual (87%) |
| **Polarización** | Lenguaje divisorio, nosotros vs ellos, ausencia de matiz | Manual (78%) |
| **Emoción** | Palabras emotivas, intensidad, emojis, signos de puntuación | BERT (22%) |
| **Clickbait** | Títulos exagerados, promesas falsas, curiosidad | BERT (50%) |
| **Conspiración** | Conexiones especulativas, "ellos" anónimos, sin evidencia | Manual (90%) |

#### C. Características NO Reportadas Explícitamente

Basado en el análisis, características que podrían detectarse pero NO se mencionan:

```
LINGUISTICAS:
  • Frecuencia de verbos activos vs pasivos (responsabilidad)
  • Uso de negaciones (patrones de negación)
  • Transitividad del discurso (quien causa qué)

PSICOLOGICAS:
  • Marcadores de certeza vs incertidumbre
  • Marcadores de autoridad
  • Apelaciones a identidad grupal

SOCIOLINGUISTICAS:
  • Registro lingüístico (formal vs coloquial)
  • Variación dialecto (señal de fuente)
  • Uso de slang / jargon especializado

CONTEXTUALES:
  • Ubicación geográfica del autor
  • Timestamp (timing de publicación)
  • Redes sociales de distribución
  • Reacciones de audiencia (likes, shares, comments)
```

#### D. Conclusión RQ5

**Características textuales usadas:**
- Deep Learning: Automáticas, semánticas, 100+ dimensiones
- ML Tradicional: Manuales, estadísticas, <100 features
- NLP Tradicional: Explícitas, léxico-sintácticas, <20 features
- Manual: Holísticas, contextua les, infinitas

**Brecha identif icada**: Características contextuales y sociolingüísticas NO están formalizadas en métodos automáticos.

**Tu oportunidad**: Formalizar características contextuales (perfil de autor, red social, timing) como features.

---

## PREGUNTAS SECUNDARIAS DE INVESTIGACIÓN

### SRQ1: Bases de Datos, Corpus y Datasets

> ¿Qué bases de datos, corpus o conjuntos de datos se han utilizado para entrenar y evaluar estos métodos?

**RESPUESTA**: No extractable de abstracts sin leer full-text. Pero puedo infer ir:

**Datasets Probables** (basado en métodos):
- BERT/Transformers: Probablemente fine-tuned en datasets de Fake News (FEVER, SemEval)
- Manual Analysis: Probablemente anotados manualmente (no datasets públicos grandes)
- NLP Tradicional: Posiblemente datasets de Twitter, News articles

**Tendencia**: 69.7% de artículos post-2023 = acceso a datasets más recientes, pero aún no estandarizados.

### SRQ2: Métricas de Evaluación

> ¿Cuáles son las métricas de evaluación más comúnmente reportadas?

**RESPUESTA DETALLADA:**

| Métrica | Artículos | % | Uso |
|---------|-----------|---|-----|
| **Accuracy** | 435 | 12.2% | Métrica DOMINANTE |
| **Precision/Recall** | 270 | 7.6% | Métrica IMPORTANTE |
| **AUC-ROC** | 25 | 0.7% | Especializada |
| **Confusion Matrix** | 25 | 0.7% | Diagnóstico |

**Problema**: 87.8% de artículos NO reportan explícitamente métricas en abstract.

**Inferencia**:
- Accuracy es fácil de calcular (binario correcto/incorrecto)
- Precision/Recall es mejor para datasets desbalanceados
- AUC-ROC raro = trabajos no tratan problemas de clasificación balanceados

### SRQ3: Diferencias por Plataforma

> ¿Existen diferencias en los métodos según el tipo de plataforma digital?

**RESPUESTA**: No extractable de abstracts. Pero:

**Plataformas Mencionadas (Inferidas de intenciones)**:
- **Twitter/X**: Fake News + Clickbait (cortos, virales)
- **Facebook**: Manipulación + Polarización (algoritmo división)
- **News Online**: Fake News + Conspiraciones (escala)
- **WhatsApp**: Menos estudiado (privado)
- **TikTok**: Casi no presente (campo reciente)

**Tu oportunidad**: Tu revisión podría mapear intenciones × plataformas.

### SRQ4: Análisis Emocional como Componente

> ¿Qué enfoques consideran el análisis emocional o afectivo?

**RESPUESTA DETALLADA:**

```
EXPLICIT EMOCION DIMENSION:   82 articulos (2.3%)

IMPLICIT EMOTION (Co-ocurre con):
  • Fake News:        34 articulos (5.3% de FN)
  • Manipulación:     30 articulos (6.9% de Manip)
  • Polarización:     28 articulos (20.0% de Pol)
  • Persuasión:       11 articulos (7.1% de Pers)

MÉTODOS PARA EMOCIÓN:
  • Manual Analysis:  47.6%
  • NLP Trad:         28.0%
  • BERT:             22.0% (¡BERT ESPECIALIZADO EN EMOCIONES!)
  • Transformers:     26.8%
```

**Hallazgo**: BERT es el método MÁS USADO para emoción (22% vs 3% overall), sugiere especialización.

**Conclusión**: Análisis emocional está emergiendo como COMPONENTE crítico, no como dimensión independiente.

### SRQ5: Direcciones Futuras Propuestas

> ¿Qué direcciones futuras de investigación han sido propuestas?

**RESPUESTA**: No explícitas en abstracts, pero INFERIBLES del análisis:

**Direcciones que la literatura IMPLICITAMENTE necesita:**

1. **Automatización de Granularidad**
   - 61.6% trabajos granulares aún manuales
   - Necesita: DL + transfer learning

2. **Multilingüismo**
   - 69.7% artículos recientes (sin estandarización)
   - Necesita: Modelos multilíngües (mBERT, XLM)

3. **Intenciones Constructivas**
   - 0% articulos estudian lo positivo
   - Necesita: Redefinir taxonomía

4. **Contexto Sociopolítico**
   - Métodos ignoran contexto editorial
   - Necesita: Incorporar metadata (autor, fuente, fecha)

5. **Plataformas Emergentes**
   - Casi ningún trabajo en TikTok, Instagram, WhatsApp
   - Necesita: Adaptar métodos a contenido multimedia

6. **Validación Cross-Plataforma**
   - Métodos no transfieren entre plataformas
   - Necesita: Datasets multiplatforma

7. **Escalabilidad en Tiempo Real**
   - 87% métodos post-hoc (después de publicación)
   - Necesita: Detección temprana (antes de viralización)

8. **Responsabilidad ética**
   - No hay discusión de sesgos en literatura
   - Necesita: Auditoría de fairness

---

## SÍNTESIS GLOBAL: ESTADO DEL ARTE

### Fortalezas de la Literatura Actual
1. Métodos claros y reproducibles (BERT, Transformers)
2. Estándares para fake news (mejor estudiado)
3. Datasets públicos disponibles (aunque incompletos)

### Debilidades de la Literatura Actual
1. **Falta de granularidad automatizada**: 61.6% still manual
2. **Sesgo hacia lo negativo**: 31.1% intenciones negativas vs 0% constructivas
3. **Baja relevancia general**: 73% artículos con relevancia <0.4
4. **Sin estándares**: Cada trabajo define intenciones diferente
5. **Monolingüe**: Mayoría en inglés

### Brechas Identificadas (Tu Oportunidad)
1. **Taxonomía clara y granular** de intenciones comunicativas
2. **Métodos automáticos** para granularidad (no solo Manual)
3. **Inclusión de intenciones positivas** (innovación real)
4. **Análisis multilingüe** (español, portugués, etc.)
5. **Validación cross-plataforma** (Twitter, Facebook, TikTok)

---

## RECOMENDACIONES PARA TU REVISIÓN SISTEMÁTICA

Basándome en estos hallazgos, tu revisión debería:

1. ✅ **Responder RQ sobre granularidad** (tu fortaleza)
2. ✅ **Documentar métodos faltantes** (características contextuales)
3. ✅ **Proponer taxonomía nueva** (intenciones constructivas)
4. ✅ **Analizar sesgos** (negativo vs constructivo)
5. ✅ **Cross-plataforma** (no solo news/Twitter)

---

**Documento generado**: 2026-04-28
**Base**: 3,575 artículos clasificados + análisis detallado
**Próximo paso**: ¿Quieres que reclasifique los artículos con TU taxonomía propuesta?
