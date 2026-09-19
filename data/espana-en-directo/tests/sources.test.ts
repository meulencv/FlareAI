import assert from 'node:assert/strict';
import test from 'node:test';
import { parseCatalunya, parseDgt, parseEuskadi, parseGalicia, parseHispa, parseMadrid, parsePublicPlayer } from '../server/sources.ts';
import { distanceKm, inSpainBounds, normalize } from '../src/model.ts';
import { allowedImage, allowedPlayer, readLimited } from '../server/network.ts';

test('Haversine handles identical points, longitudes across zero and antipodes', () => {
  assert.equal(distanceKm({ lat: 40, lon: -3 }, { lat: 40, lon: -3 }), 0);
  const madridBarcelona = distanceKm({ lat: 40.4168, lon: -3.7038 }, { lat: 41.3874, lon: 2.1686 });
  assert.ok(madridBarcelona > 500 && madridBarcelona < 510);
  assert.ok(Math.abs(distanceKm({ lat: 0, lon: 0 }, { lat: 0, lon: 180 }) - 20015.1) < 1);
});

test('bounding boxes include islands and enclaves and reject projected/nonfinite coordinates', () => {
  for (const [lat, lon] of [[28.46, -16.25], [39.57, 2.65], [35.89, -5.32], [35.29, -2.94]]) {
    assert.equal(inSpainBounds(lat, lon), true);
  }
  for (const [lat, lon] of [[4792953, 500000], [0, 0], [NaN, -3], [48.8, 2.3]]) {
    assert.equal(inSpainBounds(lat, lon), false);
  }
  assert.equal(normalize('Peñíscola · GIJÓN'), 'peniscola · gijon');
});

test('image allowlist rejects arbitrary hosts, credentials, paths and schemes', () => {
  assert.equal(allowedImage('https://informo.madrid.es/cameras/Camara06303.jpg'), true);
  assert.equal(allowedImage('http://mct.gencat.cat/mct2bo/RenderService?sctidcam=nc87.gif'), true);
  for (const url of [
    'http://127.0.0.1/image.jpg', 'file:///etc/passwd',
    'https://informo.madrid.es.evil.example/cameras/Camara06303.jpg',
    'https://user:pass@informo.madrid.es/cameras/Camara06303.jpg',
    'https://informo.madrid.es:444/cameras/Camara06303.jpg',
    'https://informo.madrid.es/secret.jpg',
    'http://informo.madrid.es/cameras/Camara06303.jpg',
  ]) assert.equal(allowedImage(url), false, url);
});

test('players accept only explicitly published embed paths', () => {
  assert.equal(allowedPlayer('https://rtsp.me/embed/abc123/'), true);
  assert.equal(allowedPlayer('https://www.youtube.com/embed/abc123DEF_-'), true);
  for (const url of ['rtsp://camera/live', 'https://rtsp.me/login', 'https://evil.example/embed/a', 'javascript:alert(1)', 'https://rtsp.me.evil.example/embed/a']) {
    assert.equal(allowedPlayer(url), false, url);
  }
});

test('lazy-loaded public players are resolved without admitting unrelated iframes', () => {
  assert.equal(parsePublicPlayer('<iframe src="https://ads.example/embed/123"></iframe><iframe src="about:blank" data-lazy-src="https://rtsp.me/embed/abc123/"></iframe>'), 'https://rtsp.me/embed/abc123/');
  assert.equal(parsePublicPlayer('<iframe src="https://ads.example/embed/123"></iframe>'), null);
});

test('remote response limits work without Content-Length and cancel bad responses', async () => {
  await assert.rejects(readLimited(new Response('123456'), 5), /demasiado grande/);
  await assert.rejects(readLimited(new Response('x', { headers: { 'Content-Length': '100' } }), 5), /demasiado grande/);
  await assert.rejects(readLimited(new Response('failure', { status: 503 })), /HTTP 503/);
  assert.equal((await readLimited(new Response('12345'), 5)).toString(), '12345');
});

test('XML entity declarations cannot reach the parser', () => {
  for (const parse of [parseDgt, parseMadrid, parseCatalunya]) {
    assert.throws(() => parse('<!DOCTYPE foo [<!ENTITY x SYSTEM "file:///etc/passwd">]><foo>&x;</foo>'), /entidades/);
  }
});

test('DGT singleton preserves IDs and kilometer formatting', () => {
  const result = parseDgt(`<d:payload xmlns:d="urn:datex"><d:device id="001"><d:typeOfDevice>camera</d:typeOfDevice><d:deviceUrl>https://etraffic.dgt.es/camarasEtraffic/001.jpg</d:deviceUrl><d:pointLocation><d:supplementaryPositionalDescription><d:roadInformation><d:roadName>A-1</d:roadName><d:roadDestination>Madrid</d:roadDestination></d:roadInformation></d:supplementaryPositionalDescription><d:tpegPointLocation><d:point><d:pointCoordinates><d:latitude>40.5</d:latitude><d:longitude>-3.6</d:longitude></d:pointCoordinates><d:_tpegNonJunctionPointExtension><d:extendedTpegNonJunctionPoint><d:kilometerPoint>02.50</d:kilometerPoint><d:province>MADRID</d:province></d:extendedTpegNonJunctionPoint></d:_tpegNonJunctionPointExtension></d:point></d:tpegPointLocation></d:pointLocation></d:device></d:payload>`);
  assert.equal(result.cameras[0].id, 'dgt-001');
  assert.equal(result.cameras[0].name, 'A-1 · km 02.50');
  assert.equal(result.cameras[0].lat, 40.5);
});

test('Madrid extracts the published image and preserves camera numbers', () => {
  const result = parseMadrid(`<kml><Document><Placemark><description><![CDATA[<img src="https://informo.madrid.es/cameras/Camara06303.jpg?t=1">]]></description><Point><coordinates>-3.68,40.40,0</coordinates></Point><ExtendedData><Data name="Numero"><Value>06303</Value></Data><Data name="Nombre"><Value>Paseo del Prado</Value></Data></ExtendedData></Placemark></Document></kml>`);
  assert.equal(result.cameras[0].id, 'madrid-06303');
  assert.equal(result.cameras[0].imageUrl, 'https://informo.madrid.es/cameras/Camara06303.jpg');
  assert.equal(result.cameras[0].lon, -3.68);
});

test('SCT GML coordinates support attributes and correctly order longitude/latitude', () => {
  const result = parseCatalunya(`<wfs:FeatureCollection xmlns:wfs="urn:wfs" xmlns:gml="urn:gml" xmlns:cite="urn:cite"><gml:featureMember><cite:cameres><cite:geom><gml:Point srsName="EPSG:4326"><gml:coordinates decimal="." cs="," ts=" ">2.1849528,41.45989301</gml:coordinates></gml:Point></cite:geom><cite:carretera>C-58</cite:carretera><cite:municipi>Nus Trinitat</cite:municipi><cite:pk>0.50</cite:pk><cite:link>http://mct.gencat.cat/mct2bo/RenderService?sctidcam=nc87.gif</cite:link></cite:cameres></gml:featureMember></wfs:FeatureCollection>`);
  assert.equal(result.cameras[0].lat, 41.45989301);
  assert.equal(result.cameras[0].lon, 2.1849528);
  assert.equal(result.cameras[0].name, 'C-58 · km 0.50');
});

test('SCT municipal cameras without kilometer values keep their street names', () => {
  const result = parseCatalunya('<FeatureCollection><featureMember><cameres><geom><Point><coordinates>2.0,41.56</coordinates></Point></geom><carretera>Pl Dore</carretera><municipi>Terrassa</municipi><link>https://emap.terrassa.cat/it_terrassa/cam01.jpeg?a=1 &amp;#13;</link></cameres></featureMember></FeatureCollection>');
  assert.equal(result.cameras[0].name, 'Pl Dore');
  assert.equal(result.cameras[0].imageUrl, 'https://emap.terrassa.cat/it_terrassa/cam01.jpeg?a=1');
});

test('Euskadi excludes projected coordinates, missing images and duplicates', () => {
  const cam = { cameraId: '1', sourceId: '2', cameraName: 'Bilbao', latitude: '43.26', longitude: '-2.93', urlImage: 'https://www.trafikoa.eus/static/files/tr/camaras/1.jpg' };
  const result = parseEuskadi({ totalPages: 1, currentPage: 1, cameras: [
    cam, cam, { ...cam, cameraId: '2', latitude: '4792953', longitude: '500000' },
    { ...cam, cameraId: '3', urlImage: undefined },
  ] });
  assert.equal(result.cameras.length, 1);
  assert.equal(result.excluded, 3);
});

test('MeteoGalicia preserves the source timestamp and rejects coordinates at zero', () => {
  const cam = { identificador: 1, nomeCamara: 'Vigo', concello: 'Vigo', provincia: 'Pontevedra', lat: 42.23, lon: -8.72, imaxeCamara: 'https://www.meteogalicia.gal/datosred/camaras/vigo/last.jpg', dataUltimaAct: '2026-09-19T10:00:00' };
  const result = parseGalicia({ listaCamaras: [cam, { ...cam, identificador: 2, lat: 0, lon: 0 }] });
  assert.equal(result.cameras.length, 1);
  assert.equal(result.excluded, 1);
  assert.equal(result.cameras[0].imageTimestamp, '2026-09-19T10:00:00');
});

test('Hispacams excludes protected, members-only, inactive and foreign-host pages', () => {
  const cam = { id: 1, link: 'https://www.hispacams.com/webcams/playa/', title: { rendered: 'Playa &amp; costa' }, meta: { latitud: '\uFEFF43.4', longitud: '-5.6', estado: 'Alta', pmpro_default_level: '' }, content: { protected: false } };
  const result = parseHispa([
    cam,
    { ...cam, id: 2, content: { protected: true } },
    { ...cam, id: 3, meta: { ...cam.meta, pmpro_default_level: '1' } },
    { ...cam, id: 4, meta: { ...cam.meta, estado: 'Mantenimiento' } },
    { ...cam, id: 5, link: 'https://evil.example/webcams/playa/' },
    { ...cam, id: 6, meta: { ...cam.meta, latitud: '50' } },
  ]);
  assert.equal(result.cameras.length, 1);
  assert.equal(result.cameras[0].name, 'Playa & costa');
  assert.equal(result.excluded, 5);
});
