#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('clasificacion_pdfs_completos.json', encoding='utf-8') as f:
    data = json.load(f)

CRITERIOS = {
    'secuencial_pipeline': {
        'desc': 'Enfoques secuenciales o pipeline para clasificacion de texto (palabras->emociones->intenciones), alineado con el framework de 4 capas propuesto',
        'keywords': ['sequenti', 'pipeline', 'layer', 'cascade', 'hierarchi', 'multistage', 'step-by-step', 'sequential', 'secuencial', 'chain']
    },
    'clasificacion_multiclase': {
        'desc': 'Clasificacion multiclase vs binaria o granularidad fina, directamente alineado con el objetivo de superar la clasificacion binaria',
        'keywords': ['multiclass', 'multi-class', 'granular', 'fine-grained', 'beyond binary', 'multi-label', 'multi-category', 'multi-intent', 'specific categor', 'granularidad']
    },
    'emocion_intencion': {
        'desc': 'Relacion entre emociones e intenciones o uso de emociones para clasificar desinformacion, clave para la matriz emocion-intencion del modelo',
        'keywords': ['emotion', 'sentiment', 'affect', 'feeling', 'plutchik', 'emocion', 'emotional cue', 'affective', 'anger', 'fear', 'disgust', 'joy', 'sadness', 'trust', 'anticipation', 'surprise']
    },
    'intencion_comunicativa': {
        'desc': 'Clasificacion de intenciones comunicativas especificas (manipular, alarmar, difamar, polarizar, ridiculizar, confundir, desinformar), variable dependiente central',
        'keywords': ['intent', 'manipulat', 'alarm', 'defam', 'polariz', 'satiriz', 'mislead', 'desinform', 'communicat', 'propaganda', 'framing', 'spin', 'disinform', 'purpose', 'motiv']
    },
    'corpus_anotacion': {
        'desc': 'Construccion de corpus, anotacion con LLMs o multiples anotadores, acuerdo inter-anotador, aplicable a Fase 0 de construccion del dataset',
        'keywords': ['corpus', 'annotation', 'label', 'llm', 'gpt', 'multi-llm', 'inter-annotator', 'agreement', 'kappa', 'crowdsourc', 'condorcet', 'ensemble label', 'etiquetad']
    },
    'transformer_bert': {
        'desc': 'Modelos BERT/Transformer/RoBERTa como linea de comparacion (baseline) para la evaluacion experimental',
        'keywords': ['bert', 'roberta', 'transformer', 'pre-train', 'pretrain', 'fine-tun', 'language model', 'plm', 't5', 'xlm', 'deberta', 'electra']
    },
    'fake_news_deteccion': {
        'desc': 'Deteccion de fake news con NLP/ML, problema central de la investigacion',
        'keywords': ['fake news', 'misinformation', 'disinformation', 'false information', 'rumor', 'clickbait', 'credibility', 'verif', 'fact-check']
    },
    'redes_sociales_texto': {
        'desc': 'Analisis de publicaciones en redes sociales, fuente de datos del corpus propuesto',
        'keywords': ['twitter', 'social media', 'tweet', 'facebook', 'reddit', 'social network', 'online platform', 'digital media']
    },
    'taxonomia_ontologia': {
        'desc': 'Propuesta de taxonomia, ontologia o tipologia de desinformacion, base para la taxonomia de 7 intenciones',
        'keywords': ['taxonom', 'ontolog', 'typolog', 'framework', 'nomenclat', 'schema', 'hierarchy of']
    },
    'limitacion_binario': {
        'desc': 'Limitaciones de enfoques binarios o necesidad de mayor granularidad, justificacion del problema de investigacion',
        'keywords': ['binary', 'limitation', 'insufficient', 'inadequate', 'beyond', 'coarse', 'oversimplif', 'lack of', 'two-class', 'true/false']
    }
}

arts = data.get('articulos', [])
resultados = []

for a in arts:
    hallazgos = a.get('hallazgos_nuevos', [])
    if not hallazgos:
        continue
    cl = a.get('clasificacion', {})
    vp = cl.get('variables_principales', {})

    for h in hallazgos:
        h_lower = h.lower()
        criterios_match = []
        for crit_key, crit_data in CRITERIOS.items():
            for kw in crit_data['keywords']:
                if kw.lower() in h_lower:
                    criterios_match.append(crit_key)
                    break
        if criterios_match:
            resultados.append({
                'id': a.get('id', ''),
                'titulo': a.get('titulo', ''),
                'year': a.get('year'),
                'autores': a.get('autores', []),
                'relevancia_general': a.get('relevancia_general', 0),
                'intenciones': vp.get('intenciones', []),
                'metodos': vp.get('metodos_especifico', []),
                'hallazgo': h,
                'criterios': criterios_match,
                'num_criterios': len(criterios_match),
            })

resultados.sort(key=lambda x: (-x['num_criterios'], -x['relevancia_general']))

output = {
    'meta': {
        'tesis': 'Modelo computacional de clasificacion de intenciones comunicativas en redes sociales (palabras->emociones->intenciones)',
        'autor': 'Luis Alberto Rojas Rubio',
        'total_hallazgos_relevantes': len(resultados),
        'total_articulos_fuente': len(set(r['id'] for r in resultados)),
        'criterios': {k: v['desc'] for k, v in CRITERIOS.items()}
    },
    'hallazgos': resultados
}

with open('hallazgos_relevantes_tesis.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

from collections import Counter
print(f'JSON generado: hallazgos_relevantes_tesis.json')
print(f'Total hallazgos relevantes: {len(resultados)}')
print(f'Articulos fuente: {len(set(r["id"] for r in resultados))}')
print()
print('Distribucion por criterio:')
crit_counter = Counter(c for r in resultados for c in r['criterios'])
for k, v in crit_counter.most_common():
    print(f'  {k}: {v}')
print()
print('Top 5 con mayor cobertura de criterios:')
for r in resultados[:5]:
    print(f'  [{r["num_criterios"]} crit | rel={r["relevancia_general"]:.2f}] {r["titulo"][:65]}')
    print(f'    >> {r["hallazgo"][:120]}')
    print(f'    Criterios: {", ".join(r["criterios"])}')
    print()
