"""Autonomous visual exhibition for Render; no LLM, Twin or telephone calls."""
from __future__ import annotations

import json
import os
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


class SilentProvider:
    ready = False
    responder_ready = False


def enabled() -> bool:
    value = os.environ.get('FLAREAI_VISUAL_DEMO')
    if value is not None:
        return value == '1'
    return bool(os.environ.get('RENDER_SERVICE_ID') or os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('RENDER') == 'true')


class VisualDemo:
    def __init__(self, director) -> None:
        self.director = director
        self.random = random.Random()
        self.next_fire = 0.0
        self.next_message = 0.0
        self.last_save = 0.0
        self.last_revision = -1
        self.locations = [(41.4035, 2.1744, 'Sagrada Família'), (41.414, 2.131, 'Pedralbes'),
                          (41.407, 2.153, 'Gràcia'), (41.399, 2.187, 'Fort Pienc')]
        self.random.shuffle(self.locations)
        self.cycle = 0
        self.review = 0
        self.evidence = json.loads((Path(__file__).parent / "static/visual-evidence/manifest.json").read_text())
        director.state.update(mode='visual_demo', status='watching')
        director.scene.data.update(automatic=False, label='DEMO VISUAL AUTOMÁTICA · decisiones simuladas')
        for n in range(2):
            identifier = f'visual-helicopter-{n}'
            director.state['resources'][identifier] = {
                'id': identifier, 'station_id': identifier, 'name': f'Apoyo aéreo simulado {n + 1}',
                'lat': 41.385 + n * .03, 'lon': 2.13, 'kind': 'helicopter',
                'distance_km': 0, 'simulated_capacity': True, 'coordinate_method': 'visual_demo'}
        director.event('watch', 'Demo automática · Barcelona',
                       'Incendios, decisiones y medios simulados. Puedes cambiar el viento, la potencia y cortar una vía.', simulation=True)

    def spawn(self, now: float) -> None:
        from demo import call_incident
        d = self.director
        lat, lon, name = self.locations[self.cycle % len(self.locations)]
        # Snap to an actual connected road; all land movements use the prepared graph.
        graph = d.router.demo_graph()
        lon, lat = graph.points[graph.nearest([lon, lat])]
        self.cycle += 1
        call = {'location': {'lat': lat, 'lon': lon, 'label': name + ' · simulación', 'precision': 'area'},
                'reported_at': datetime.fromtimestamp(now, timezone.utc).isoformat()}
        item = call_incident(str(uuid.uuid4()), call, d.store.weather)
        item.update(source_kind='scenario', scene_report={'source': 'Demo visual automática · incendio ficticio'}, visual_evidence=self.evidence)
        d.scene.data.setdefault('fixtures', []).append(item)
        d.scene.observe({'incidents': [item]})
        record = d.scene.data['incidents'][item['id']]
        record.update(radius_km=self.random.uniform(.12, .17), medical=True,
                      wind_to=self.random.randrange(360), priority=8.0)
        d.event('report', 'Llamada 112 simulada · incendio en ' + name,
                'Prioridad a la extinción y a los accesos: salen bomberos, ambulancias, policía y apoyo aéreo.',
                incident_id=item['id'], simulation=True)
        self.next_fire = now + self.random.uniform(28, 40)

    def payload(self) -> dict:
        return self.director.scene.overlay({'incidents': []})

    def step(self) -> None:
        d, now = self.director, time.time()
        with d.lock:
            # Keep a bounded, continuous exhibition instead of accumulating old fires.
            closed = {key for key, r in d.scene.data['incidents'].items() if r['phase'] == 'closed'}
            for key in closed:
                d.scene.data['incidents'].pop(key, None)
                d.auto.records.pop(key, None)
            d.scene.data['fixtures'] = [i for i in d.scene.data.get('fixtures', []) if i['id'] not in closed]
            if not d.scene.data['incidents']:
                d.scene.data['closures'].clear()
                d.scene.data['congestion'].clear()
            active = [r for r in d.scene.data['incidents'].values() if r['phase'] not in {'releasing', 'closed'}]
            if len(active) < 2 and now >= self.next_fire:
                self.spawn(now)
            d.advance()
            d.scene.observe(self.payload())
            d.scene.evolve()
            d.scene.maintenance()
        d.auto.tick(self.payload())
        for item in self.payload()['incidents']:
            if item.get('scenario', {}).get('phase') != 'active':
                continue
            if not any(a['resource']['kind'] == 'helicopter' and a['status'] != 'returning'
                       for a in d.auto.assigned(item['id'])):
                d.auto.dispatch(item, {'helicopter': 1}, 'Apoyo aéreo · decisión simulada',
                                'Un helicóptero refuerza la extinción mientras los equipos terrestres aseguran los accesos.')
        with d.lock:
            for a in d.state['assignments'].values():
                signature = (a['id'], a.get('route_revision'), a['status'])
                if a.get('visual_timing') != signature:
                    a['visual_timing'] = signature
                    if a['status'] in {'enroute', 'transporting'}:
                        a['travel_seconds'] = self.random.uniform(18, 32)
            revision = d.scene.data.get('plan_revision', 0)
            changed = revision != self.last_revision
            if now >= self.next_message or changed:
                active = [r for r in d.scene.data['incidents'].values() if r['phase'] == 'active']
                if active:
                    record = self.random.choice(active)
                    suppression = record.get('suppression_power', 0)
                    if changed and self.last_revision >= 0:
                        title = 'Reevaluación simulada · cambian las condiciones'
                        reason = f"Viento hacia {record['wind_to']:.0f}°. Los cortes recalculan las rutas; sin acceso la unidad se detiene. El apoyo aéreo mantiene la extinción."
                    elif suppression:
                        title = f'Extinción en marcha · {record.get("extinguished_pct", 0)} %'
                        reason = f'{suppression} unidades de potencia de extinción trabajando. Mantengo el apoyo hasta apagar el frente y ordeno el regreso.'
                    else:
                        title, reason = self.random.choice([
                            ('Coordinación simulada · equipos en camino', 'Reparto los camiones entre distintos parques y mantengo cobertura sanitaria y policial.'),
                            ('Evaluando accesos · decisión simulada', 'Los vehículos siguen carreteras del mapa. El helicóptero refuerza el ataque al frente.'),
                            ('Prioridad: contener el frente · simulación', 'Observo la dirección del viento y la llegada de medios antes de dar el fuego por apagado.')])
                    kind = 'decision'
                    if not changed:
                        self.review += 1
                        if self.review % 3 == 1:
                            kind, title, reason = 'context', 'Revisando satélite NASA · demo visual', 'Consulto el mosaico de Barcelona y el viento NOAA. La imagen lleva su fecha; no confirma el incendio ficticio.'
                        elif self.review % 3 == 2:
                            kind, title, reason = 'context', 'Revisando cámaras y accesos · demo visual', 'Abro imágenes de cámaras de Barcelona para ilustrar el contraste visual. Los cortes del escenario recalculan las rutas terrestres.'
                    d.event(kind, title, reason, incident_id=record['id'], simulation=True)
                self.last_revision = revision
                self.next_message = now + self.random.uniform(8, 13)
            d.state['status'] = 'watching'
            if now - self.last_save >= 5:
                d.save()
                self.last_save = now
