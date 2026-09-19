from __future__ import annotations

import hashlib
import json
import math
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEMORY_ROOT = ROOT / 'FlareAI-Memoria'
REPORT_ROOT = ROOT / '.local/operation-reports'
MODEL = {'id': 'illustrative-impact-v1', 'fuel_t_ha': 8.0, 'combustion_fraction': .5,
         'carbon_fraction': .45, 'vegetation_fraction': .7, 'avoided_fatality_fraction': .25,
         'carbon_prices_eur_t': [10.0, 30.0, 60.0],
         'status': 'Supuestos ficticios de demostración, no calibrados. Precios de escenario, no cotización de mercado.'}


def impact(scene: dict, fields: dict, closed_at: float, model: dict | None = None) -> dict:
    model = {**MODEL, **(model or {})}
    maritime = scene.get('maritime', False)
    initial, maximum = (.08, .15) if maritime else (.18, 1.2)
    elapsed = max(0, closed_at - scene.get('started_at', closed_at))
    radius = min(maximum, max(initial, scene.get('peak_radius_km', initial)))
    baseline = min(maximum, initial + elapsed * .0025)
    def area(r):
        return math.pi * r * r * .65 * 100
    affected, without = area(radius), area(max(radius, baseline))
    avoided = max(0, without - affected)
    if fields.get('incendio') == 'descartado':
        affected = without = avoided = 0.0
    co2 = None if maritime else avoided * model['vegetation_fraction'] * model['fuel_t_ha'] * model['combustion_fraction'] * model['carbon_fraction'] * 44 / 12
    assisted = fields.get('personas_asistidas')
    assisted = int(str(assisted)) if str(assisted).isascii() and str(assisted).isdigit() else None
    return {'model': model, 'scenario_area_ha': round(affected, 2), 'without_intervention_ha': round(without, 2),
            'avoided_area_ha': round(avoided, 2), 'avoided_co2_t': round(co2, 2) if co2 is not None else None,
            'assisted_people': assisted, 'potential_lives_saved': (0 if fields.get('incendio') == 'descartado' else round(assisted * model['avoided_fatality_fraction'], 1)) if assisted is not None else None,
            'carbon_value_eur': [round(co2 * price, 2) for price in model['carbon_prices_eur_t']] if co2 is not None else None,
            'issued_credits': 0, 'horizon_seconds': round(elapsed),
            'limitations': ['Superficie del escenario ilustrativo, no perímetro quemado medido ni dato NASA.',
                'Contrafactual con las mismas condiciones iniciales y el mismo horizonte; crecimiento geométrico supuesto, sin calibración física.',
                'Combustible, vegetación y combustión son supuestos de demo; solo CO2, sin otros gases ni emisiones de los vehículos.',
                'Vidas potencialmente salvadas: valor esperado bajo un supuesto ficticio de riesgo evitado del 25%; no resultado clínico.',
                'El carbono evitado no genera créditos vendibles automáticamente. Requiere metodología, adicionalidad y verificación independiente.']}


def report_markdown(report: dict) -> str:
    metrics = report['metrics']
    def show(value):
        return 'Sin datos suficientes' if value is None else str(value)
    lines = [f'# {report["title"]}', '', 'SIMULACRO · Informe de operación', '', report['summary'], '', '## Impacto estimado de demo', '',
        f'- Personas asistidas comunicadas por el equipo: {show(metrics["assisted_people"])}',
        f'- Vidas potencialmente salvadas, estimación ilustrativa: {show(metrics["potential_lives_saved"])}',
        f'- Superficie afectada en el escenario: {metrics["scenario_area_ha"]} ha',
        f'- Escenario sin intervención al mismo horizonte: {metrics["without_intervention_ha"]} ha',
        f'- Superficie evitada estimada: {metrics["avoided_area_ha"]} ha',
        f'- CO2 evitado estimado: {show(metrics["avoided_co2_t"])} t', '', '## Créditos de carbono: oportunidad potencial', '',
        'Las empresas pueden comprar y retirar créditos verificados; cada crédito representa una tonelada de CO2 equivalente reducida o retirada. '
        'El carbono evitado de esta simulación es un equivalente teórico, no un crédito certificado. No se ha emitido ningún crédito ni obtenido ingresos.',
        f'Precios hipotéticos: {metrics["model"]["carbon_prices_eur_t"]} EUR/t. Valores hipotéticos: {show(metrics["carbon_value_eur"])} EUR.',
        'Referencia conceptual: https://verra.org/programs/verified-carbon-standard/verified-carbon-units-vcus/', '', '## Supuestos y límites', '',
        *['- ' + text for text in metrics['limitations']], '', 'Parámetros: ' + json.dumps(metrics['model'], ensure_ascii=False),
        '', '## Evaluación de testimonios', '', (report.get('assessment') or {}).get('summary', 'Sin conclusión registrada.'), '', '## Parte de bomberos', '',
        *[f'- {key}: {value}' for key, value in report['field_report'].items()], '', '## Solicitudes y ejecución', '',
        *[f'- {r["kind"]}: {r["fulfilled"]}/{r["quantity"]}; {r["status"]}' for r in report['requests']], '', '## Cronología', '']
    for event in report['events']:
        date = datetime.fromtimestamp(event.get('at', report['closed_at']), timezone.utc).strftime('%H:%M:%S UTC')
        lines.append(f'- {date} · {event["message"]}. {event.get("reason", "")}')
    return '\n'.join(lines) + '\n'


def pdf_bytes(markdown: str) -> bytes:
    lines = []
    for line in markdown.splitlines():
        lines.extend(textwrap.wrap(line.lstrip('# '), width=92, break_long_words=True) or [''])
    pages = [lines[i:i + 52] for i in range(0, len(lines), 52)] or [[]]
    objects: list[bytes] = [b'', b'', b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>']
    ids = []
    for page in pages:
        page_id = len(objects) + 1
        content_id = page_id + 1
        ids.append(page_id)
        content = b'BT /F1 10 Tf 45 795 Td 14 TL\n'
        for line in page:
            text = line.encode('cp1252', 'replace').replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)')
            content += b'(' + text + b') Tj T*\n'
        content += b'ET'
        objects.extend([f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>'.encode(),
                        f'<< /Length {len(content)} >>\nstream\n'.encode() + content + b'\nendstream'])
    objects[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[1] = f'<< /Type /Pages /Count {len(ids)} /Kids [{" ".join(f"{i} 0 R" for i in ids)}] >>'.encode()
    output = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
    start = len(output)
    output.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        output.extend(f'{offset:010d} 00000 n \n'.encode())
    output.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode())
    return bytes(output)


def sync_memories(database) -> None:
    MEMORY_ROOT.mkdir(exist_ok=True)
    for row in database.documents('memory'):
        identifier = row['id'].removeprefix('memory:')
        if not all(c in '0123456789abcdef' for c in identifier) or len(identifier) != 20:
            continue
        note = row['data']
        text = '---\ntags: [flareai, aprendizaje, simulacion]\n---\n\n# ' + note['title'] + '\n\n' + note['text'] + '\n\n'
        text += 'Procedencia: simulacro, no protocolo operativo.\n\nRelacionado: ' + ' · '.join(f'[[{source}]]' for source in note.get('reports', [])) + '\n'
        (MEMORY_ROOT / f'{identifier}.md').write_text(text, encoding='utf-8')


def finish_operation(director, record: dict) -> dict:
    identifier = record['id']
    report_id = hashlib.sha256(f'{director.session_id}:{identifier}'.encode()).hexdigest()[:24]
    existing = director.db.document('report:' + report_id)
    if existing:
        record['report_id'] = report_id
        record['metrics'] = existing['metrics']
        sync_memories(director.db)
        return existing
    scene = director.scene.data['incidents'][identifier]
    events = [e for e in director.db.director_history(director.session_id)['events'] if e.get('incident_id') == identifier]
    current = [e for e in director.state['events'] if e.get('incident_id') == identifier]
    events = sorted({e['sequence']: e for e in events + current}.values(), key=lambda e: e['sequence'])
    fields = director.store.demo.field_reports.get(identifier, {}).get('fields', {})
    now = time.time()
    report = {'id': report_id, 'incident_id': identifier, 'session_id': director.session_id, 'title': 'Operación · ' + record['name'],
              'closed_at': now, 'summary': f'Operación de simulación cerrada en {record["name"]}. Se conserva la evidencia, los partes y el cumplimiento de recursos.',
              'assessment': record.get('assessment'), 'events': events, 'field_report': fields,
              'requests': list(record['requests'].values()), 'metrics': impact(scene, fields, now),
              'testimonies': director.operations.context(identifier).get('testimonies', [])}
    markdown = report_markdown(report)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    MEMORY_ROOT.mkdir(exist_ok=True)
    (REPORT_ROOT / (report_id + '.pdf')).write_bytes(pdf_bytes(markdown))
    (MEMORY_ROOT / (report_id + '.md')).write_text(markdown, encoding='utf-8')
    for kind, title, text in [
        ('blocked', 'Acceso no garantizado por proximidad', 'En esta operación una unidad no tuvo acceso utilizable. Antes de asignar el parque más cercano, comprobar una ruta disponible y una sede alternativa.'),
        ('reroute', 'Revisar los cortes antes de volver a usar una ruta', 'El escenario requirió un desvío. Una ruta guardada no garantiza que siga siendo transitable tras un corte.'),
        ('outbound_result', 'Disponer de un contacto alternativo', 'El primer contacto no respondió en este ensayo. Mantener un respaldo autorizado y comprobar el resultado antes de repetir una llamada.'),
    ]:
        matches = [e for e in events if e['kind'] == kind and (kind != 'outbound_result' or 'respaldo' in e['message'])]
        if not matches:
            continue
        note_id = hashlib.sha256((title + record['name']).encode()).hexdigest()[:20]
        saved = director.db.document('memory:' + note_id) or {}
        note = {'id': note_id, 'title': title, 'text': text, 'place': record['name'], 'kind': kind, 'at': now,
                'reports': list(dict.fromkeys([*saved.get('reports', []), report_id]))[-20:], 'source': 'simulation_observation'}
        director.db.document('memory:' + note_id, 'memory', note)
    director.db.document('report:' + report_id, 'report', report, director.session_id)
    if hasattr(director.db, 'invalidate'):
        director.db.invalidate('memories', 'brain')
    sync_memories(director.db)
    record['report_id'] = report_id
    record['metrics'] = report['metrics']
    return report
