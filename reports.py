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


def base_notes() -> list[dict]:
    entries = [
        ('base-evidence', 'Contrastar antes de decidir', 'Cruzar la ubicación y los testimonios con los partes de equipos y las fuentes disponibles. Una anomalía térmica es una señal de contraste, no una confirmación oficial de incendio.', ['base-weather', 'base-resources']),
        ('base-weather', 'Viento y territorio', 'Revisar dirección, intensidad y fecha del viento junto a población, vegetación e instalaciones próximas. Separar observaciones actuales de datos históricos y del escenario calculado.', ['base-evidence', 'base-resources']),
        ('base-resources', 'Recursos y accesos', 'Comprobar disponibilidad y recorrido antes de asignar una unidad. Repartir la cobertura entre sedes y conservar alternativas cuando un acceso esté cortado. La proximidad no garantiza el acceso.', ['base-learning']),
        ('base-learning', 'Cerrar el ciclo y aprender', 'Conservar decisiones, partes y resultados con su procedencia. La llegada de un vehículo no confirma la extinción. Al cerrar, vincular el informe y las lecciones observadas para la siguiente revisión.', ['base-evidence']),
    ]
    return [{'id': key, 'title': title, 'text': text, 'kind': 'base', 'source': 'curated_base', 'links': links,
             'reports': []} for key, title, text, links in entries]


def decision_memories(database) -> list[dict]:
    return [{'id': note['id'], 'data': note} for note in base_notes()] + database.documents('memory')[-30:]


def brain_notes(database) -> list[dict]:
    notes = base_notes() + [row['data'] | {'kind': 'memory', 'links': ['base-learning']} for row in database.documents('memory')]
    notes += [row['data'] | {'kind': 'report', 'links': ['base-learning'], 'markdown': report_markdown(row['data'])}
              for row in database.documents('report')]
    return notes


def report_markdown(report: dict) -> str:
    metrics = report['metrics']
    def show(value):
        return 'Sin datos suficientes' if value is None else str(value)
    closed = datetime.fromtimestamp(report['closed_at'], timezone.utc).strftime('%d/%m/%Y · %H:%M UTC')
    lines = [f'# {report["title"]}', '', 'INFORME FINAL · SIMULACRO', '',
        f'Cierre: {closed} · Referencia: {report.get("id", "Sin referencia")}', '',
        '## Resumen ejecutivo', '', report['summary'], '',
        'Este informe recoge el resultado de la operación, los recursos solicitados y la secuencia de decisiones. '
        'Los indicadores de impacto comparan el escenario intervenido con el escenario sin intervención.', '',
        '## Balance de la operación', '',
        f'- Personas asistidas · parte del equipo: {show(metrics["assisted_people"])}',
        f'- Vidas potencialmente salvadas · estimación: {show(metrics["potential_lives_saved"])}',
        f'- Superficie del escenario: {metrics["scenario_area_ha"]} ha',
        f'- Superficie sin intervención · estimación: {metrics["without_intervention_ha"]} ha',
        f'- Superficie preservada · estimación: {metrics["avoided_area_ha"]} ha',
        f'- CO2 evitado · estimación: {show(metrics["avoided_co2_t"])} t', '', '## Valor ambiental y carbono', '',
        'Las empresas pueden comprar y retirar créditos verificados; cada crédito representa una tonelada de CO2 equivalente reducida o retirada. '
        'El carbono evitado de esta simulación es un equivalente teórico, no un crédito certificado. No se ha emitido ningún crédito ni obtenido ingresos.',
        f'Precios hipotéticos: {metrics["model"]["carbon_prices_eur_t"]} EUR/t. Valores hipotéticos: {show(metrics["carbon_value_eur"])} EUR.',
        '', '## Evaluación de testimonios', '', (report.get('assessment') or {}).get('summary', 'No consta una evaluación registrada.'), '', '## Parte de bomberos', '',
        *([f'- {key.replace("_", " ").capitalize()}: {value}' for key, value in report['field_report'].items()] or ['No consta un parte de bomberos.']), '', '## Solicitudes y ejecución', '',
        *([f'- {dict(fire_engine="Bomberos", ambulance="Ambulancia", helicopter="Helicóptero", police="Policía").get(r["kind"], r["kind"])}: {r["fulfilled"]} de {r["quantity"]} unidades; {dict(fulfilled="completada", pending="pendiente").get(r["status"], r["status"])}' for r in report['requests']] or ['No se registraron solicitudes adicionales de recursos.']), '', '## Cronología', '']
    for event in report['events']:
        date = datetime.fromtimestamp(event.get('at', report['closed_at']), timezone.utc).strftime('%H:%M:%S UTC')
        lines.append(f'- {date} · {event["message"]}. {event.get("reason", "")}')
    if not report['events']:
        lines.append('No hay eventos registrados para esta operación.')
    lines.extend(['', '## Metodología y alcance', '', *['- ' + text for text in metrics['limitations']], '',
                  'Parámetros del modelo: ' + json.dumps({k: v for k, v in metrics['model'].items() if k != 'status'}, ensure_ascii=False)])
    return '\n'.join(lines) + '\n'


def pdf_bytes(markdown: str) -> bytes:
    pages: list[bytes] = []
    content = bytearray()
    y = 0
    ink, muted, purple, teal = '0.12 0.16 0.25', '0.36 0.41 0.49', '0.40 0.27 0.73', '0.02 0.44 0.43'

    def rect(x, bottom, width, height, color):
        content.extend(f'{color} rg {x} {bottom} {width} {height} re f\n'.encode())

    def text(value, x, baseline, size=10, bold=False, color=ink):
        escaped = value.encode('cp1252', 'replace').replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)')
        content.extend(f'BT /F{2 if bold else 1} {size} Tf {color} rg 1 0 0 1 {x} {baseline} Tm ('.encode() + escaped + b') Tj ET\n')

    def new_page():
        nonlocal content, y
        if content:
            pages.append(bytes(content))
        content = bytearray()
        rect(0, 0, 595, 842, '1 1 1')
        rect(0, 830, 595, 12, purple)
        text('flareai', 42, 791, 23, True, purple)
        text('INTELLIGENCE & OPERATIONS', 345, 798, 9, True, muted)
        text('INFORME DE OPERACIÓN', 345, 783, 9, color=muted)
        rect(42, 53, 511, 1, '0.88 0.90 0.94')
        text('FlareAI  /  Registro de operación  /  Simulacro', 42, 34, 8, color=muted)
        text(f'{len(pages) + 1:02d}', 530, 34, 9, True, purple)
        y = 750

    def room(height):
        if y - height < 72:
            new_page()

    new_page()
    balance = False
    card_index = 0
    for line in markdown.splitlines():
        if not line.strip():
            y -= 7
            continue
        if line.startswith('# '):
            title_lines = textwrap.wrap(line[2:], 38)
            room(len(title_lines) * 29 + 22)
            for title in title_lines:
                text(title, 42, y, 24, True)
                y -= 29
            y -= 12
        elif line.startswith('## '):
            balance = line[3:] == 'Balance de la operación'
            card_index = 0
            room(80)
            rect(42, y - 17, 511, 30, '0.94 0.92 0.98')
            rect(42, y - 17, 4, 30, purple)
            text(line[3:], 55, y - 6, 12, True, purple)
            y -= 39
        elif balance and line.startswith('- ') and ': ' in line:
            label, value = line[2:].split(': ', 1)
            room(83)
            x = 42 + (card_index % 2) * 261
            rect(x, y - 65, 250, 77, '0.94 0.97 0.97')
            for i, part in enumerate(textwrap.wrap(label, 39)):
                text(part, x + 13, y - 3 - i * 12, 9, color=muted)
            text(value, x + 13, y - 44, 18 if len(value) < 22 else 12, True, teal)
            card_index += 1
            if card_index % 2 == 0:
                y -= 87
        else:
            bullet = line.startswith('- ')
            wrapped = textwrap.wrap(line[2:] if bullet else line, width=94 if bullet else 98, break_long_words=True)
            room(min(len(wrapped), 3) * 14 + 8)
            if bullet:
                rect(44, y + 2, 4, 4, teal)
            for part in wrapped:
                room(14)
                text(part, 56 if bullet else 42, y, 10, color=ink)
                y -= 14
            y -= 5
    pages.append(bytes(content))
    objects: list[bytes] = [b'', b'', b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
                           b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>']
    ids = []
    for page in pages:
        page_id = len(objects) + 1
        content_id = page_id + 1
        ids.append(page_id)
        objects.extend([f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_id} 0 R >>'.encode(),
                        f'<< /Length {len(page)} >>\nstream\n'.encode() + page + b'\nendstream'])
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
    for note in base_notes():
        text = '---\ntags: [flareai, base]\n---\n\n# ' + note['title'] + '\n\n' + note['text']
        text += '\n\nOrigen: conocimiento inicial curado. Disponible en el contexto del director.\n\nRelacionado: '
        text += ' · '.join(f'[[{target}]]' for target in note['links']) + '\n'
        (MEMORY_ROOT / f'{note["id"]}.md').write_text(text, encoding='utf-8')
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
    pending = sum(a.get('incident_id') == identifier for a in director.state['assignments'].values())
    summary = (f'Intervención de simulación finalizada en {record["name"]}. Informe disponible sin esperar al regreso a base. '
               f'Unidades aún ocupadas en regreso, traslado o pendientes de acceso: {pending}. '
               'Se conservan la evidencia, los partes y el cumplimiento de recursos; no implica alta médica.')
    report = {'id': report_id, 'incident_id': identifier, 'session_id': director.session_id, 'title': 'Operación · ' + record['name'],
              'closed_at': now, 'summary': summary, 'pending_units': pending,
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
