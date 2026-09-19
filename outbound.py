from __future__ import annotations

import json
import time
import uuid
from copy import deepcopy


class OutboundCalls:
    def __init__(self, director) -> None:
        self.director, self.db = director, director.db
        self.provider = director.store.demo.provider
        self.enabled = bool(getattr(director.store, 'allow_outbound', False))
        self.config = self.db.setting('outbound-workflow')
        director.state['outbound'] = {}
        self.last_poll = 0.0

    @property
    def jobs(self) -> dict:
        return self.director.state['outbound']

    def public_state(self, identifier: str) -> dict:
        job = self.jobs.get(identifier, {'status': 'waiting_arrival'})
        return deepcopy({k: v for k, v in job.items() if k in {'status', 'attempt', 'started_at', 'completed_at', 'message'}})

    def tick(self, payload: dict) -> None:
        now = time.time()
        if now - self.last_poll < 2:
            return
        self.last_poll = now
        for identifier, job in list(self.jobs.items()):
            if job['status'] == 'dialing':
                self.poll(identifier, job)
        if any(job['status'] in {'starting', 'dialing', 'uncertain'} for job in self.jobs.values()):
            return
        incidents = {i['id']: i for i in payload.get('incidents', [])}
        for resource_id, assignment in self.director.state['assignments'].items():
            identifier = assignment.get('incident_id')
            if assignment['resource']['kind'] != 'fire_engine' or assignment['status'] != 'onscene' or identifier not in incidents:
                continue
            job = self.jobs.get(identifier)
            if job and job['status'] != 'retry_backup':
                continue
            if not self.enabled or not self.config.get('published'):
                if not job:
                    self.jobs[identifier] = {'status': 'disabled', 'message': 'Telefonía pendiente de activación autorizada'}
                    self.director.event('outbound_pending', 'Bomberos ha llegado; llamada pendiente', 'La telefonía real está desactivada o no configurada. No se inventará un parte.', incident_id=identifier)
                    self.director.save()
                continue
            self.start(incidents[identifier], resource_id, 1 if job else 0)
            return

    def start(self, incident: dict, resource_id: str, attempt: int) -> None:
        contacts, callers = self.db.contacts(), self.db.contacts(role='caller')
        identifier = incident['id']
        if attempt >= len(contacts) or not callers:
            self.jobs[identifier] = {'status': 'unreachable', 'message': 'No hay más contactos autorizados disponibles', 'attempt': attempt}
            self.director.event('outbound_failed', 'No se ha obtenido el parte de bomberos', 'Se mantiene la operación pendiente; no se inventa una confirmación.', incident_id=identifier)
            self.director.save()
            return
        contact = contacts[attempt]
        report = incident.get('demo_report') or {}
        binding = ({**report['location'], 'run_id': report['run_id']} if report else
                   {'sensor_id': identifier, 'lat': incident['lat'], 'lon': incident['lon'], 'label': incident['name']}) | {'incident_id': identifier, 'resource_id': resource_id}
        job = {'status': 'starting', 'attempt': attempt + 1, 'contact_id': contact['id'], 'resource_id': resource_id,
               'started_at': time.time(), 'request_id': str(uuid.uuid4()), 'binding': binding}
        previous = self.jobs.get(identifier)
        self.jobs[identifier] = job
        try:
            self.director.save()
        except Exception:
            if previous is None:
                self.jobs.pop(identifier, None)
            else:
                self.jobs[identifier] = previous
            raise
        context = {'incident_id': identifier, 'name': incident['name'], 'assessment': self.director.operations.records.get(identifier, {}).get('assessment'),
                   'resources': [a['resource']['kind'] for a in self.director.state['assignments'].values() if a.get('incident_id') == identifier]}
        try:
            result = self.provider.client.request('POST', f'/workflows/{self.config["workflow_id"]}/runs', {
                'environment': 'production', 'payload': {'phone_number': contact['phone'], 'from_number': callers[0]['phone'],
                    'incident_json': json.dumps(context, ensure_ascii=False), 'request_id': job['request_id']}})
            run_id = str(uuid.UUID(result['run_id']))
        except Exception:
            job.update(status='uncertain', message='No se ha podido confirmar el inicio. No se reintenta para evitar una llamada duplicada.')
            self.director.event('outbound_uncertain', 'Inicio de llamada sin confirmar', job['message'], incident_id=identifier)
            self.director.save()
            return
        job.update(status='dialing', run_id=run_id)
        self.director.save()
        self.director.store.demo.register(run_id, role='firefighter', binding=binding)
        self.director.event('outbound_call', 'Llamando al equipo de bomberos' if attempt == 0 else 'Llamando al contacto de respaldo', 'Se solicita situación y necesidades del incidente; llamada telefónica de demo.', incident_id=identifier)
        self.director.save()

    def poll(self, identifier: str, job: dict) -> None:
        result = self.provider.client.request('GET', f'/runs/{job["run_id"]}/sessions?page=1&page_size=10&sort=desc')
        sessions = [s for s in self.provider.module.list_data(result) if s.get('run_id') == job['run_id'] and s.get('type') == 'outbound']
        if not sessions:
            if time.time() - job['started_at'] > 180:
                job.update(status='uncertain', message='Proveedor sin estado de llamada; no se repite automáticamente.')
                self.director.save()
            return
        session = sessions[0]
        status = session.get('status')
        if status in {'missed', 'busy', 'voicemail', 'failed', 'canceled'}:
            job['status'] = 'retry_backup' if job['attempt'] == 1 else 'unreachable'
            job['message'] = 'El contacto principal no atendió; se intentará el respaldo.' if job['attempt'] == 1 else 'Ningún contacto ha aportado un parte.'
            self.director.event('outbound_result', job['message'], 'Resultado telefónico: ' + str(status), incident_id=identifier)
            self.director.save()
        elif status == 'completed':
            demo = self.director.store.demo
            if job['run_id'] not in demo.calls:
                demo.register(job['run_id'], role='firefighter', binding=job['binding'])
            demo.poll_call(job['run_id'])
            has_part = bool(demo.calls[job['run_id']].get('part'))
            job.update(status='completed' if has_part else 'needs_report', completed_at=time.time(),
                       message='Parte recibido' if has_part else 'Conversación finalizada sin parte estructurado; requiere revisión.')
            self.director.event('outbound_result', job['message'], 'La información procede de la llamada vinculada al equipo.', incident_id=identifier)
            self.director.save()
