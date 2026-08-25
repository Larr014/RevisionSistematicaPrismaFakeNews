# Análisis: POLARIDAD vs GRANULARIDAD en Detección de Intenciones

## Resumen Ejecutivo

La literatura sobre Fake News está dividida:
- **44.1%** enfoque BINARIO (¿es fake news o no?)
- **55.9%** enfoque GRANULAR (¿qué tipo de fake news?)

**Hallazgo crítico**: La tendencia 2022-2026 muestra un giro hacia GRANULARIDAD (60-64%), pero sin métodos automáticos efectivos (61.6% aún manual).

---

## 1. POLARIDAD vs GRANULARIDAD - Definiciones

### POLARIDAD (Enfoque Binario)
- **Pregunta**: "¿Es este texto fake news?"
- **Respuesta**: SI / NO
- **Métodos asociados**: Transformers (28.6%), Manual (38.5%), BERT (13.4%)
- **Relevancia alcanzada**: 0.52/1.0 (más alta)
- **Artículos**: 283 (44.1% de trabajos sobre fake news)

**Ejemplo**: Detectar si un tweet es desinformación o información veraz.

### GRANULARIDAD (Enfoque Multinivel)
- **Pregunta**: "¿CUÁL ES la intención específica del fake news?"
- **Respuesta**: Manipulación + Polarización + Conspiración + Emoción + etc.
- **Métodos asociados**: Manual predominante (61.6%), NLP (17.3%)
- **Relevancia alcanzada**: 0.48/1.0 (más baja)
- **Artículos**: 359 (55.9% de trabajos sobre fake news)

**Ejemplo**: Identificar que un tweet no solo es fake news, sino que su INTENCIÓN es "manipular narrativa + polarizar sociedad + apelación emocional".

---

## 2. ESTADÍSTICAS DETALLADAS

### Distribución de Enfoques (642 artículos con Fake News)

| Enfoque | Cantidad | % | Características |
|---------|----------|---|---|
| **BINARIO (Solo SI/NO)** | 283 | 44.1% | Detecta presencia pero no tipo |
| **GRANULAR (Multi-intención)** | 359 | 55.9% | Identifica tipo específico de fake |

### Métodos Utilizados

#### ENFOQUE BINARIO (Polaridad)
```
1. Manual Analysis       109 artículos (38.5%) - MÉTODO BASE
2. Transformers          81 artículos (28.6%) - MÉTODO AVANZADO
3. NLP Tradicional       50 artículos (17.7%)
4. BERT                  38 artículos (13.4%)
5. RNN/LSTM              37 artículos (13.1%)
```

#### ENFOQUE GRANULAR (Granularidad)
```
1. Manual Analysis      221 artículos (61.6%) - ALTAMENTE PREVALENTE
2. Transformers         72 artículos (20.1%)
3. NLP Tradicional      62 artículos (17.3%)
4. BERT                 38 artículos (10.6%)
5. RandomForest         31 artículos (8.6%)
```

**Interpretación**: Los trabajos granulares usan MÁS análisis manual (61.6% vs 38.5%), lo que indica que **la granularidad NO está automatizada**.

### Relevancia Alcanzada

| Enfoque | Relevancia Promedio | Interpretación |
|---------|------------------|---|
| BINARIO | 0.52/1.0 | **7.7% MÁS relevante** |
| GRANULAR | 0.48/1.0 | Menor relevancia percibida |

**Paradoja**: Aunque más difícil, los trabajos BINARIOS logran mayor relevancia documentada. Posible razón: son más fáciles de evaluar objetivamente (SI/NO correcto), mientras que granularidad requiere validación manual compleja.

---

## 3. TIPOS DE GRANULARIDAD DETECTADOS

Cuando literatura explora granularidad en Fake News, identifica estos tipos:

| Tipo | Frecuencia en Granularidad | Descripción |
|------|---------------------------|---|
| **Manipulación Narrativa** | 304 (84.7%) | Distorsión intencional de hechos/contexto |
| **Polarización** | 85 (23.7%) | Diseñado para dividir y radicalizar |
| **Persuasión Estratégica** | 67 (18.7%) | Convencimiento mediante argumentación falsa |
| **Emocionaliación** | 34 (9.5%) | Apelación emocional extrema |
| **Conspiración** | 24 (6.7%) | Narrativas conspirativas falsas |
| **Clickbait** | 4 (1.1%) | Sensacionalismo de titulares |

**Observación**: Manipulación Narrativa (84.7%) es la intención DOMINANTE en fake news granular. La mayoría de desinformación NO es accidental, es **manipulación deliberada**.

---

## 4. EVOLUCIÓN TEMPORAL: DEL BINARIO AL GRANULAR

### Distribución por Años (2019-2026)

```
2019: 21 Binario | 24 Granular  → 53.3% Granular (EQUILIBRIO)
2020: 32 Binario | 13 Granular  → 28.9% Granular (RETORNO A BINARIO)
2021: 34 Binario | 24 Granular  → 41.4% Granular (RECUPERACION)
2022: 34 Binario | 41 Granular  → 54.7% Granular (GIRO HACIA GRANULAR)
2023: 31 Binario | 43 Granular  → 58.1% Granular (CONSOLIDACION)
2024: 38 Binario | 59 Granular  → 60.8% Granular (TENDENCIA CLARA)
2025: 49 Binario | 73 Granular  → 59.8% Granular (ESTABILIDAD)
2026: 33 Binario | 60 Granular  → 64.5% Granular (PICO ACTUAL)
```

### Interpretación

1. **2019-2020**: Pregunta dominante: "¿Es fake news?" (BINARIO)
2. **2020-2021**: Pandemia causó retorno a detectar presencia (41.4% granular)
3. **2022-2026**: Giro claro hacia granularidad (60-64%)

**Conclusión**: La comunidad investigadora está evolucionando de "detectar presencia" a "entender intención".

---

## 5. CRÍTICA: SESGO ACTUAL EN LITERATURA

### Lo que LA MAYORÍA HACE (Polaridad/Binario)

```
Input: Tweet → [Red Neuronal] → Output: "FAKE / REAL"
Métrica: Accuracy 95% (¿es correcto el binario?)
```

**Problema**: No responde "¿para qué?" — solo "¿es o no?"

### Lo que MINORÍA INTENTA (Granularidad)

```
Input: Tweet → [Análisis Semántico Manual] → Output: "FAKE + MANIPULACIÓN + POLARIZACIÓN"
Métrica: Relevancia 0.48 (difícil de validar)
```

**Problema**: Requiere evaluación humana, no escala automáticamente.

### La Brecha

- ✓ **Binario es FÁCIL** de automatizar con ML (28.6% Transformers)
- ✗ **Granular es DIFÍCIL** de automatizar (solo 10.6% BERT, 20.1% Transformers)
- **Resultado**: 61.6% de trabajos granulares siguen siendo MANUALES

---

## 6. IMPLICACIONES PARA TU INVESTIGACIÓN

### Tu Propuesta vs Literatura Actual

**Status Quo** (55.9% de trabajos, pero sin buena automatización):
```
Fake News + Manipulación + Polarización (detección MIXTA, sin jerarquía)
```

**Tu Enfoque (PROPUESTO)** - Taxonomía Estructurada:
```
1. Categoría Principal: Tipo de Desinformación
   ├─ Engaño Deliberado
   ├─ Distorsión Intencional
   ├─ Amplificación Emocional
   └─ Influencia Política

2. Intención Secundaria: Efecto Buscado
   ├─ Manipular
   ├─ Polarizar
   ├─ Radicalizar
   ├─ Vender
   └─ Influenciar
```

### Ventaja de tu Enfoque

1. **Novedad**: Literatura NO tiene taxonomía clara de granularidad
2. **Automatizable**: Puedes diseñar prompts de Claude para detectarla
3. **Relevancia**: Responde pregunta que literatura 2022-2026 está haciendo
4. **Impacto**: Primera revisión sistemática que MAPEA intenciones en fake news

---

## 7. RECOMENDACIÓN: TAXONOMÍA PROPUESTA

Si quieres proponer tu propio set de intenciones, sugiero esta estructura (basada en análisis):

### NIVEL 1: Categorías Amplias (Tipos de Desinformación)

```
A. ENGAÑO DELIBERADO (Fake News radicales)
   - Falsificación completa
   - Conspiración
   - Pseudociencia

B. DISTORSIÓN INTENCIONAL (Verdad tergiversada)
   - Cita fuera de contexto
   - Contexto falso
   - Sensacionalismo (Clickbait)

C. AMPLIFICACIÓN EMOCIONAL (Movimiento social)
   - Polarización deliberada
   - Emocionaliación extrema
   - Radicalizacion

D. INFLUENCIA POLÍTICA (Objetivo específico)
   - Persuasión electoral
   - Propaganda de régimen
   - Campañas coordinadas
```

### NIVEL 2: Intenciones Específicas (Efecto Buscado)

```
I1_Engaño_Puro        → "Creer información falsa"
I2_Manipulación       → "Distorsionar percepción"
I3_Polarización       → "Dividir a la sociedad"
I4_Emocionalizacion   → "Provocar reacción emocional"
I5_Radicalizacion     → "Llevar a acción extrema"
I6_Venta/Ganancia     → "Beneficio económico"
I7_Influencia_Politica → "Cambiar voto/opinion"
I8_Desinformación_Generada → "Contenido creado por IA"
```

---

## 8. SIGUIENTE PASO

**¿Quieres que reclasifiquemos los 3,575 artículos usando tu nueva taxonomía?**

Para eso necesito confirmar:
1. ¿Aceptas esta estructura de intenciones, o tienes otra en mente?
2. ¿Quieres agregar más niveles de granularidad?
3. ¿Quieres que re-ejecute el script de Claude con tu nueva taxonomía?

---

**Documento generado**: 2026-04-28
**Basado en**: Clasificación de 3,575 artículos con Claude AI
**Fuente de datos**: `clasificacion_claude.json`
