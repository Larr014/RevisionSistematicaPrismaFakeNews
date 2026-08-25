import re
import pandas as pd
import requests
import sys
import os
import time
from difflib import SequenceMatcher

SEMANTIC_SCHOLAR_API_KEY = ''  # Opcional
CORE_API_KEY = ''  # Opcional

def parse_ris_file(ris_path):
    records = []
    current_record = {}
    authors_list = []
    keywords_list = []
    tag_mapping = {
        'TI': 'Title', 'T1': 'Title',
        'AU': 'Authors', 'A1': 'Authors',
        'PY': 'Year', 'Y1': 'Year',
        'DO': 'DOI',
        'JO': 'Source', 'JF': 'Source', 'T2': 'Source',
        'SN': 'ISSN/ISBN',
        'UR': 'URL',
        'VL': 'Volume',
        'IS': 'Issue',
        'SP': 'Start Page',
        'EP': 'End Page',
        'KW': 'Keywords',
        'LA': 'Language'
    }
    with open(ris_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == 'ER  -':
            if current_record:
                if authors_list:
                    current_record['Authors'] = '; '.join(authors_list)
                if keywords_list:
                    current_record['Keywords'] = '; '.join(keywords_list)
                records.append(current_record)
                current_record = {}
                authors_list = []
                keywords_list = []
            continue
        match = re.match(r'^([A-Z][A-Z0-9])\s*-\s*(.*)', line)
        if match:
            tag, value = match.groups()
            if tag in ('AU', 'A1'):
                authors_list.append(value)
            elif tag == 'KW':
                keywords_list.append(value)
            elif tag in tag_mapping:
                field = tag_mapping[tag]
                if field not in current_record:
                    current_record[field] = value
                elif tag == 'SN':
                    current_record[field] += f"; {value}"
    if current_record:
        if authors_list:
            current_record['Authors'] = '; '.join(authors_list)
        if keywords_list:
            current_record['Keywords'] = '; '.join(keywords_list)
        records.append(current_record)
    return records

def records_to_dataframe(records):
    columns = [
        'Title', 'Authors', 'Year', 'DOI', 'Source', 'ISSN/ISBN', 'URL',
        'Volume', 'Issue', 'Start Page', 'End Page', 'Keywords', 'Language'
    ]
    rows = []
    for record in records:
        row = {col: record.get(col, '') for col in columns}
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)

def extract_doi(val):
    if not val: return ''
    val = val.strip()
    if re.match(r'^\d+\.\d+\/', val): 
        return val
    return ''

def extract_isbn(val):
    if not val: return ''
    found = re.findall(r'\b(?:97[89][- ]?)?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?[\dX]\b', val)
    return found[0].replace(' ','') if found else ''

def extract_issn(val):
    if not val: return ''
    found = re.findall(r'\b\d{4}-\d{3}[\dXx]\b', val)
    return found[0] if found else ''

def similar(a, b):
    a = (a or '').strip().lower()
    b = (b or '').strip().lower()
    return SequenceMatcher(None, a, b).ratio()

def similar_any(a, b):
    set_a = set(x.strip().lower() for x in (a or '').split(';') if x.strip())
    set_b = set(x.strip().lower() for x in (b or '').split(';') if x.strip())
    if not set_a or not set_b: return 0
    scores = [SequenceMatcher(None, x, y).ratio() for x in set_a for y in set_b]
    return max(scores) if scores else 0

def api_crossref(doi=None, isbn=None, issn=None, title=None):
    base = "https://api.crossref.org/works"
    params = {}
    if doi:
        url = f"{base}/{doi}"
        r = requests.get(url)
        if r.status_code != 200: return {}
        msg = r.json()['message']
        return crossref_parse(msg)
    elif isbn or issn:
        params['filter'] = []
        if isbn: params['filter'].append(f"isbn:{isbn}")
        if issn: params['filter'].append(f"issn:{issn}")
        params['filter'] = ",".join(params['filter'])
        params['rows'] = 1
        r = requests.get(base, params=params)
        if r.status_code != 200: return {}
        items = r.json().get('message', {}).get('items', [])
        if not items: return {}
        return crossref_parse(items[0])
    elif title:
        params = {'query.title': title, 'rows': 1}
        r = requests.get(base, params=params)
        if r.status_code != 200: return {}
        items = r.json().get('message', {}).get('items', [])
        if not items: return {}
        return crossref_parse(items[0])
    return {}

def crossref_parse(data):
    return {
        'Title': data.get('title', [''])[0] if data.get('title') else '',
        'Authors': '; '.join(
            [f"{a.get('given','')} {a.get('family','')}".strip() for a in data.get('author',[])]
        ),
        'Year': data.get('issued', {}).get('date-parts', [[None]])[0][0] if data.get('issued') else '',
        'DOI': data.get('DOI', ''),
        'Source': data.get('container-title', [''])[0] if data.get('container-title') else '',
        'ISSN/ISBN': '; '.join(data.get('ISSN', [])) if data.get('ISSN') else '',
        'URL': data.get('URL', ''),
        'Volume': data.get('volume', ''),
        'Issue': data.get('issue', ''),
        'Start Page': data.get('page', '').split('-')[0] if data.get('page') else '',
        'End Page': data.get('page', '').split('-')[-1] if data.get('page') and '-' in data['page'] else '',
        'Keywords': '; '.join(data.get('subject', [])) if data.get('subject') else '',
        'Language': data.get('language', ''),
    }

def api_semanticscholar(doi=None, isbn=None, issn=None, title=None):
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY: headers['x-api-key'] = SEMANTIC_SCHOLAR_API_KEY
    if doi:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,year,venue,url,volume,issue,doi,fieldsOfStudy,journal,pages,externalIds"
        r = requests.get(url, headers=headers)
        if r.status_code != 200: return {}
        data = r.json()
        return semantic_parse(data)
    elif title:
        url = f'https://api.semanticscholar.org/graph/v1/paper/search?query={title}&fields=title,authors,year,venue,url,volume,issue,doi,fieldsOfStudy,journal,pages,externalIds&limit=1'
        r = requests.get(url, headers=headers)
        if r.status_code != 200: return {}
        items = r.json().get('data', [])
        if not items: return {}
        return semantic_parse(items[0])
    return {}

def semantic_parse(paper):
    return {
        'Title': paper.get('title', ''),
        'Authors': '; '.join([a.get('name', '') for a in paper.get('authors', [])]),
        'Year': paper.get('year', ''),
        'DOI': paper.get('doi',''),
        'Source': paper.get('venue',''),
        'ISSN/ISBN': '',  
        'URL': paper.get('url',''),
        'Volume': paper.get('volume',''),
        'Issue': paper.get('issue',''),
        'Start Page': paper.get('pages','').split('-')[0] if paper.get('pages') else '',
        'End Page': paper.get('pages','').split('-')[-1] if paper.get('pages') and '-' in paper['pages'] else '',
        'Keywords': '; '.join(paper.get('fieldsOfStudy', [])),
        'Language': ''
    }

def api_openalex(doi=None, isbn=None, issn=None, title=None):
    if doi:
        url = f"https://api.openalex.org/works/doi:{doi}"
        r = requests.get(url)
        if r.status_code != 200: return {}
        data = r.json()
        return openalex_parse(data)
    elif title:
        url = f"https://api.openalex.org/works?title.search={title}&per-page=1"
        r = requests.get(url)
        if r.status_code != 200: return {}
        items = r.json().get('results', [])
        if not items: return {}
        return openalex_parse(items[0])
    return {}

def openalex_parse(work):
    return {
        'Title': work.get('title', ''),
        'Authors': '; '.join([a['author']['display_name'] for a in work.get('authorships', []) if 'author' in a]),
        'Year': work.get('publication_year', ''),
        'DOI': work.get('doi', ''),
        'Source': work.get('host_venue', {}).get('display_name', ''),
        'ISSN/ISBN': work.get('host_venue', {}).get('issn_l', ''),
        'URL': work.get('host_venue', {}).get('url', ''),
        'Volume': work.get('biblio', {}).get('volume', ''),
        'Issue': work.get('biblio', {}).get('issue', ''),
        'Start Page': work.get('biblio', {}).get('first_page', ''),
        'End Page': work.get('biblio', {}).get('last_page', ''),
        'Keywords': '',  
        'Language': work.get('language', '')
    }

def api_core(doi=None, isbn=None, issn=None, title=None):
    if not CORE_API_KEY: return {}
    headers = {'Authorization': f'Bearer {CORE_API_KEY}'}
    if doi:
        url = f'https://api.core.ac.uk/v3/search/works?doi={doi}'
    elif title:
        url = f'https://api.core.ac.uk/v3/search/works?q={title}&limit=1'
    else:
        return {}
    r = requests.get(url, headers=headers)
    if r.status_code != 200: return {}
    data = r.json()
    hits = data.get('results', [])
    if not hits: return {}
    rec = hits[0].get('data', {})
    return {
        'Title': rec.get('title', ''),
        'Authors': '; '.join((rec.get('authors', []) or [])),
        'Year': rec.get('publishedDate', '')[:4] if rec.get('publishedDate') else '',
        'DOI': rec.get('doi', ''),
        'Source': rec.get('publisher', ''),
        'ISSN/ISBN': '',
        'URL': rec.get('downloadUrl', ''),
        'Volume': '',
        'Issue': '',
        'Start Page': '',
        'End Page': '',
        'Keywords': '; '.join(rec.get('topics', [])) if rec.get('topics') else '',
        'Language': rec.get('language', '')
    }

def api_share(doi=None, isbn=None, issn=None, title=None):
    base_url = "https://share.osf.io/api/v2/search/creativeworks/_search"
    headers = {'Content-Type': 'application/json'}
    if doi:
        query = {"query": {"term": {"identifiers": doi}}, "size": 1}
    elif title:
        query = {"query": {"bool": {"must": [{"multi_match": {"query": title, "fields": ["title", "description"]}}]}}, "size": 1}
    else:
        return {}
    try:
        resp = requests.post(base_url, json=query, headers=headers)
        if resp.status_code != 200: return {}
        data = resp.json()
        hits = data.get('hits', {}).get('hits', [])
        if not hits: return {}
        rec = hits[0]['_source']
    except Exception: return {}

    authors_list = []
    for x in rec.get('contributors', []):
        if isinstance(x, dict) and 'name' in x:
            authors_list.append(x.get('name', ''))
        elif isinstance(x, str):
            authors_list.append(x)

    identifiers = rec.get('identifiers', [])
    doi = ''
    for i in identifiers:
        if isinstance(i, str) and i.startswith('10.'):
            doi = i
            break

    return {
        'Title': rec.get('title', ''),
        'Authors': '; '.join(authors_list),
        'Year': rec.get('date_published', '')[:4] if rec.get('date_published') else '',
        'DOI': doi,
        'Source': rec.get('publisher', ''),
        'ISSN/ISBN': '',
        'URL': rec.get('uris', {}).get('canonicalUri', ''),
        'Volume': '',
        'Issue': '',
        'Start Page': '',
        'End Page': '',
        'Keywords': '; '.join(rec.get('tags', [])) if rec.get('tags') else '',
        'Language': rec.get('languages', [None])[0] if rec.get('languages') else ''
    }

AVAILABLE_APIS = [
    ('Crossref', api_crossref),
    ('Semantic Scholar', api_semanticscholar),
    ('OpenAlex', api_openalex),
    ('CORE', api_core),
    ('SHARE', api_share),
]

def update_record_fields(orig, newvals):
    if newvals.get('DOI') and (not orig.get('DOI') or orig.get('DOI') != newvals['DOI']):
        orig['DOI'] = newvals['DOI']
        if newvals.get('URL'):
            orig['URL'] = newvals['URL']
    for k, v in newvals.items():
        if (not orig.get(k)) and v:
            orig[k] = v

def complete_record_via_apis(record, modo='manual', min_title=0.61, min_authors=0.61, min_avg=0.61):
    doi = extract_doi(record.get('DOI', ''))
    isbn = extract_isbn(record.get('ISSN/ISBN', ''))
    issn = extract_issn(record.get('ISSN/ISBN', ''))

    title0 = record.get('Title', '')
    authors0 = record.get('Authors', '')

    for api_name, api_fun in AVAILABLE_APIS:
        args_used = {}
        if doi:   args_used['doi'] = doi
        elif isbn: args_used['isbn'] = isbn
        elif issn: args_used['issn'] = issn
        elif title0: args_used['title'] = title0
        else: continue

        api_result = api_fun(**args_used)
        time.sleep(0.2)

        if not api_result or (not api_result.get('Title') and not api_result.get('Authors')):
            continue

        sim_title = similar(api_result.get('Title', ''), title0)
        sim_authors = similar_any(api_result.get('Authors', ''), authors0)
        avg_sim = (sim_title + sim_authors)/2

        if modo == 'auto':
            if sim_title >= min_title and sim_authors >= min_authors and avg_sim >= min_avg:
                update_record_fields(record, api_result)
                return api_name, "auto"
        else:
            if sim_title == 1.0 and sim_authors == 1.0:
                update_record_fields(record, api_result)
                return api_name, "auto"
            elif avg_sim >= 0.61 and avg_sim < 1.0:
                print(f"\n--- Revisión manual ({api_name}) ---")
                print(f"Título original: {title0.strip()}\n→ Propuesto: {api_result.get('Title','').strip()}")
                print(f"Autores original: {authors0.strip()}\n→ Propuesto: {api_result.get('Authors','').strip()}")
                print(f"Similitud título: {sim_title:.2f}, autores: {sim_authors:.2f}, PROMEDIO: {avg_sim:.2f}")
                resp = input("¿Aceptar estos datos para este registro? (s/n): ").strip().lower()
                if resp == 's':
                    update_record_fields(record, api_result)
                    return api_name, "manual"
                else:
                    break
    return None, None

def complete_missing_fields(records, modo='manual', min_title=0.61, min_authors=0.61, min_avg=0.61):
    total_refs = len([r for r in records if any([not r.get(k) for k in ('Title', 'Authors', 'Year', 'DOI', 'Source')])])
    auto, manual, total = 0, 0, 0
    apis_used = {}
    improved_records = []
    completados = 0
    for idx, rec in enumerate(records):
        missing_fields = [k for k in ('Title', 'Authors', 'Year', 'DOI', 'Source') if not rec.get(k)]
        if missing_fields:
            total += 1
            completados += 1
            progreso = completados / total_refs * 100 if total_refs else 100
            sys.stdout.write(f"\r⏳ Completando registro {completados} de {total_refs} | Progreso: {progreso:.1f}%   ")
            sys.stdout.flush()
            api_used, tipo = complete_record_via_apis(rec, modo, min_title, min_authors, min_avg)
            if tipo == "auto":
                auto += 1
                apis_used.setdefault(f"{api_used}:auto", 0)
                apis_used[f"{api_used}:auto"] += 1
            elif tipo == "manual":
                manual += 1
                apis_used.setdefault(f"{api_used}:manual", 0)
                apis_used[f"{api_used}:manual"] += 1
        improved_records.append(rec)
    print("\n")  # Salto de línea final
    remaining_incomplete = sum(
        1 for rec in improved_records
        if any([not rec.get(k, '') for k in ('Title', 'Authors', 'Year', 'DOI', 'Source')])
    )
    return improved_records, total, auto, manual, remaining_incomplete, apis_used

def save_log(log_path, total_incomplete, completados_auto, completados_manual, faltan, apis_used):
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("=== LOG DE COMPLETADO DE REFERENCIAS ===\n")
        f.write(f"Referencias originalmente incompletas: {total_incomplete}\n")
        f.write(f"Referencias completadas automáticamente: {completados_auto}\n")
        f.write(f"Referencias completadas manualmente: {completados_manual}\n")
        f.write(f"Referencias todavía con campos críticos incompletos: {faltan}\n")
        if apis_used:
            f.write("APIs y tipo de completado:\n")
            for api, count in apis_used.items():
                f.write(f"- {api}: {count} referencias completadas\n")
        else:
            f.write("⚠️  No se pudo completar ningún registro con las APIs empleadas\n")
        f.write("---\nFin.\n")

def ris_to_excel(ris_path, output_path=None):
    if not os.path.exists(ris_path):
        print(f"❌ No se encontró el archivo '{ris_path}'")
        return None, None
    if output_path is None:
        output_path = os.path.splitext(ris_path)[0] + '_output.xlsx'
    records = parse_ris_file(ris_path)
    if not records:
        print("⚠️  No se encontraron registros en el archivo.")
        return None, None
    df = records_to_dataframe(records)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Referencias')
        worksheet = writer.sheets['Referencias']
        for col in worksheet.columns:
            max_length = max(len(str(cell.value or '')) for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 4, 60)
    print(f"✅ Archivo Excel generado: {output_path}")
    return records, output_path

def choose_threshold(nombre, default):
    print(f"\nEl valor predefinido para el umbral de {nombre} es {default:.2f}")
    print("¿Qué deseas hacer?")
    print(f"1. Mantener predefinido [{default:.2f}]")
    print(f"2. No considerar umbral de {nombre}")
    print(f"3. Definir valor manualmente")
    while True:
        opt = input("Escribe 1, 2 o 3: ").strip()
        if opt == '1':
            return default
        elif opt == '2':
            print(f"{nombre}: Umbral desactivado. (Se aceptará cualquier valor para este campo)")
            return 0.0
        elif opt == '3':
            try:
                val = float(input(f"Introduce el valor para umbral de {nombre} (0.00 - 1.00): ").strip())
                if 0.0 <= val <= 1.0:
                    return val
            except Exception:
                print("Valor incorrecto. Debe ser un número entre 0 y 1.")
        else:
            print("Opción inválida, elige 1, 2 o 3.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ris_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        ris_path = input("Ruta del archivo RIS: ")
        output_name = input("Nombre del archivo Excel de salida (sin .xlsx): ") or "resultados"
        output_path = f"{output_name}.xlsx"
    records, excel_path = ris_to_excel(ris_path, output_path)

    if records:
        choice = input("\n¿Intentar completar los campos faltantes con ayuda externa? (s/n): ").strip().lower()
        if choice == 's':
            print("\n¿Quieres modo manual (confirmación humana para coincidencias parciales) o totalmente automático?")
            modo = input("Escribe [manual] o [auto]: ").strip().lower()
            modo = 'auto' if modo.startswith('a') else 'manual'
            min_title, min_authors, min_avg = 0.90, 0.90, 0.90  # defaults

            if modo == 'auto':
                min_title = choose_threshold('TÍTULO', 0.90)
                min_authors = choose_threshold('AUTORES', 0.90)
                min_avg = choose_threshold('PROMEDIO', 0.90)

                improved_records, n_incomplete, n_auto, n_manual, n_faltan, apis_used = complete_missing_fields(
                    records, modo, min_title, min_authors, min_avg
                )
            else:
                improved_records, n_incomplete, n_auto, n_manual, n_faltan, apis_used = complete_missing_fields(records)

            output_full = excel_path.replace('.xlsx', '_full.xlsx')
            pd.DataFrame(improved_records).to_excel(output_full, index=False, engine='openpyxl')
            print(f"\n➡️  Archivo Excel mejorado guardado como: {output_full}")
            log_path = excel_path.replace('.xlsx', '_autocompletado.log.txt')
            save_log(log_path, n_incomplete, n_auto, n_manual, n_faltan, apis_used)
            print(f"📝 Log guardado como: {log_path}")
        else:
            print("Operación finalizada.")