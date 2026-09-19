import { createHash } from 'node:crypto';
import { load } from 'cheerio';
import { XMLParser } from 'fast-xml-parser';
import { z } from 'zod';
import { type Camera, type Source, cameraSchema, inSpainBounds } from '../src/model.ts';
import { allowedImage, allowedPlayer, getJson, getText } from './network.ts';

interface ImportResult { cameras: Camera[]; excluded: number }
interface Adapter { info: Source; interval: number; run: () => Promise<ImportResult> }
const num = z.coerce.number().finite();
const text = z.coerce.string();
const parser = new XMLParser({ ignoreAttributes: false, removeNSPrefix: true, parseTagValue: false });
const many = <T extends z.ZodType<unknown>>(schema: T) => z.preprocess(v => Array.isArray(v) ? v : [v], z.array(schema));
const xmlText = z.union([z.string(), z.object({ '#text': z.string() }).transform(v => v['#text'])]);
const hash = (s: string): string => createHash('sha256').update(s).digest('hex').slice(0, 16);
const asText = (s: string): string => load(s).text().trim();

function xml(s: string): unknown {
  if (/<!DOCTYPE|<!ENTITY/i.test(s)) throw new Error('XML con entidades no permitido');
  return parser.parse(s) as unknown;
}

function filter(cameras: Camera[], total = cameras.length): ImportResult {
  const unique = new Map<string, Camera>();
  for (const c of cameras) {
    if (cameraSchema.safeParse(c).success && inSpainBounds(c.lat, c.lon) && (c.kind !== 'snapshot' || (c.imageUrl && allowedImage(c.imageUrl)))) {
      unique.set(c.id, c);
    }
  }
  return { cameras: [...unique.values()], excluded: total - unique.size };
}

export function parsePublicPlayer(body: string): string | null {
  const html = load(body);
  return html('iframe').toArray()
    .flatMap(node => [html(node).attr('src'), html(node).attr('data-lazy-src')])
    .map(url => url?.trim() || '')
    .find(allowedPlayer) || null;
}

const dgtDevice = z.object({
  '@_id': text,
  typeOfDevice: z.string(),
  deviceUrl: z.string().optional(),
  pointLocation: z.object({
    supplementaryPositionalDescription: z.object({ roadInformation: z.object({
      roadName: z.string(), roadDestination: z.string().optional(),
    }) }),
    tpegPointLocation: z.object({ point: z.object({
      pointCoordinates: z.object({ latitude: num, longitude: num }),
      _tpegNonJunctionPointExtension: z.object({ extendedTpegNonJunctionPoint: z.object({
        kilometerPoint: text, province: z.string(),
      }) }),
    }) }),
  }),
});

export function parseDgt(body: string): ImportResult {
  const root = z.object({ payload: z.object({ device: many(dgtDevice) }) }).parse(xml(body));
  return filter(root.payload.device.filter(d => d.typeOfDevice === 'camera' && d.deviceUrl).map(d => {
    const point = d.pointLocation.tpegPointLocation.point;
    const extra = point._tpegNonJunctionPointExtension.extendedTpegNonJunctionPoint;
    const road = d.pointLocation.supplementaryPositionalDescription.roadInformation;
    return {
      id: `dgt-${d['@_id']}`, source: 'dgt', name: `${road.roadName} · km ${extra.kilometerPoint}`,
      place: `${extra.province}${road.roadDestination ? ` · ${road.roadDestination}` : ''}`,
      lat: point.pointCoordinates.latitude, lon: point.pointCoordinates.longitude,
      category: 'traffic', kind: 'snapshot', imageUrl: d.deviceUrl,
      pageUrl: 'https://www.dgt.es/conoce-el-estado-del-trafico/camaras-de-trafico/',
      refreshSeconds: 180,
    };
  }), root.payload.device.length);
}

const madridPlacemark = z.object({
  description: z.string(),
  Point: z.object({ coordinates: z.string() }),
  ExtendedData: z.object({ Data: many(z.object({ '@_name': z.string(), Value: text })) }),
});
export function parseMadrid(body: string): ImportResult {
  const root = z.object({ kml: z.object({ Document: z.object({ Placemark: many(madridPlacemark) }) }) }).parse(xml(body));
  return filter(root.kml.Document.Placemark.map(p => {
    const [lon, lat] = p.Point.coordinates.trim().split(',').map(Number);
    const fields = Object.fromEntries(p.ExtendedData.Data.map(d => [d['@_name'], d.Value]));
    const image = load(p.description)('img').attr('src');
    return {
      id: `madrid-${fields.Numero}`, source: 'madrid', name: fields.Nombre,
      place: 'Madrid', lat, lon, category: 'traffic', kind: 'snapshot',
      imageUrl: image ? image.split('?')[0] : undefined,
      pageUrl: 'https://informo.madrid.es/', refreshSeconds: 300,
    };
  }));
}

const catalunyaCam = z.object({
  geom: z.object({ Point: z.object({ coordinates: xmlText }) }),
  carretera: text, municipi: text, pk: text.optional(), link: z.string(),
});
export function parseCatalunya(body: string): ImportResult {
  const root = z.object({ FeatureCollection: z.object({
    featureMember: many(z.object({ cameres: catalunyaCam })),
  }) }).parse(xml(body));
  return filter(root.FeatureCollection.featureMember.map(({ cameres: c }) => {
    const [lon, lat] = c.geom.Point.coordinates.split(',').map(Number);
    const link = asText(c.link);
    return {
      id: `sct-${hash(link)}`, source: 'sct', name: `${c.carretera}${c.pk ? ` · km ${c.pk}` : ''}`,
      place: c.municipi.trim(), lat, lon, imageUrl: link,
      category: 'traffic', kind: 'snapshot', refreshSeconds: 180,
      pageUrl: 'https://mct.gencat.cat/',
    };
  }));
}

const galiciaSchema = z.object({ listaCamaras: z.array(z.object({
  identificador: num, nomeCamara: z.string(), concello: z.string(), provincia: z.string(),
  lat: num, lon: num, imaxeCamara: z.string(), dataUltimaAct: z.string().optional(),
})) });
export function parseGalicia(raw: unknown): ImportResult {
  return filter(galiciaSchema.parse(raw).listaCamaras.map(c => ({
    id: `galicia-${c.identificador}`, source: 'galicia', name: c.nomeCamara,
    place: `${c.concello}, ${c.provincia}`, lat: c.lat, lon: c.lon,
    category: 'landscape', kind: 'snapshot', imageUrl: c.imaxeCamara,
    imageTimestamp: c.dataUltimaAct,
    pageUrl: 'https://www.meteogalicia.gal/web/observacion/camaras',
    refreshSeconds: 120,
  })));
}

const euskadiPage = z.object({
  totalPages: z.number().int().min(1).max(100), currentPage: z.number(),
  cameras: z.array(z.object({
    cameraId: text, sourceId: text, cameraName: z.string().default('Cámara'),
    latitude: z.string().optional(), longitude: z.string().optional(),
    address: z.string().optional(), road: z.string().optional(), urlImage: z.string().optional(),
  })),
});
export function parseEuskadi(raw: unknown): ImportResult {
  const { cameras } = euskadiPage.parse(raw);
  return filter(cameras.map(c => ({
    id: `euskadi-${c.sourceId}-${c.cameraId}`, source: 'euskadi', name: c.cameraName,
    place: `${c.address || 'Euskadi'}${c.road ? ` · ${c.road}` : ''}`,
    lat: Number(c.latitude), lon: Number(c.longitude),
    imageUrl: c.urlImage, kind: 'snapshot', category: 'traffic',
    pageUrl: 'https://www.trafikoa.euskadi.eus/', refreshSeconds: 180,
  })));
}

const hispaSchema = z.array(z.object({
  id: z.number(), link: z.string().url(), title: z.object({ rendered: z.string() }),
  meta: z.object({
    latitud: z.string().optional(), longitud: z.string().optional(), estado: z.string().optional(),
    pmpro_default_level: z.string().optional(),
  }),
  content: z.object({ protected: z.boolean() }).optional(),
}));
export function parseHispa(raw: unknown): ImportResult {
  const entries = hispaSchema.parse(raw);
  return filter(entries.filter(c =>
    c.meta.estado === 'Alta' && !c.content?.protected && !c.meta.pmpro_default_level
    && c.link.startsWith('https://www.hispacams.com/webcams/'),
  ).map(c => ({
    id: `hispa-${c.id}`, source: 'hispa', name: asText(c.title.rendered),
    place: 'Hispacams · turismo y naturaleza',
    lat: Number(c.meta.latitud?.replace('\uFEFF', '')), lon: Number(c.meta.longitud?.replace('\uFEFF', '')),
    category: 'tourism', kind: 'player', pageUrl: c.link, refreshSeconds: 0,
    coordinateNote: 'Ubicación publicada por Hispacams; no comprobada sobre el terreno.',
  })), entries.length);
}

function info(id: string, name: string, url: string, license: string, licenseUrl: string, note: string): Source {
  return { id, name, url, license, licenseUrl, note, status: 'pending', count: 0, excluded: 0 };
}

export const adapters: Adapter[] = [
  {
    info: info('dgt', 'DGT', 'https://nap.dgt.es/es/dataset/camaras-dgt-datex2-v3-7',
      'Datos públicos DGT · citar la fuente', 'https://www.dgt.es/contenido/aviso-legal/',
      'Red estatal, excepto Cataluña y País Vasco. La fecha del dispositivo no es la fecha de la imagen.'),
    interval: 3600000,
    run: async () => parseDgt(await getText('https://nap.dgt.es/datex2/v3/dgt/DevicePublication/camaras_datex2_v37.xml')),
  },
  {
    info: info('madrid', 'Madrid · Informo', 'https://datos.madrid.es/dataset/202088-0-trafico-camaras',
      'CC BY 4.0 · Ayuntamiento de Madrid', 'https://creativecommons.org/licenses/by/4.0/',
      'Capturas de tráfico publicadas cada cinco minutos.'),
    interval: 3600000,
    run: async () => parseMadrid(await getText('https://informo.madrid.es/informo/tmadrid/CCTV.kml')),
  },
  {
    info: info('sct', 'Trànsit · Cataluña', 'https://datos.gob.es/es/catalogo/a09002970-camaras-de-trafico-en-las-carreteras-de-cataluna',
      'Datos abiertos · Generalitat de Catalunya', 'https://administraciodigital.gencat.cat/ca/dades/dades-obertes/informacio-practica/llicencies/',
      'El servicio de imágenes publica enlaces HTTP; el servidor los recupera sin modificar su contenido.'),
    interval: 3600000,
    run: async () => parseCatalunya(await getText('https://www.gencat.cat/transit/opendata/cameres.xml')),
  },
  {
    info: info('galicia', 'MeteoGalicia', 'https://www.meteogalicia.gal/web/observacion/camaras',
      'MeteoGalicia · Xunta de Galicia', 'https://www.xunta.gal/aviso-legal-do-portal-da-xunta?langId=es_ES',
      'Paisajes y meteorología. La fecha de captura es la publicada por MeteoGalicia, hora peninsular.'),
    interval: 300000,
    run: async () => parseGalicia(await getJson('https://servizos.meteogalicia.gal/mgrss/observacion/jsonCamaras.action')),
  },
  {
    info: info('euskadi', 'Open Data Euskadi', 'https://opendata.euskadi.eus/catalogo/-/camaras-de-trafico-de-las-administraciones-publicas-de-euskadi/',
      'Open Data Euskadi · administraciones de Euskadi', 'https://opendata.euskadi.eus/general/-/informacion-legal-opendata/',
      'API paginada completa. Se excluyen registros sin imagen admitida o con coordenadas proyectadas cuyo sistema no se documenta. Algunas cámaras no responden.'),
    interval: 3600000,
    run: async () => {
      const first = euskadiPage.parse(await getJson('https://api.euskadi.eus/traffic/v1.0/cameras'));
      const result = parseEuskadi(first);
      for (let page = 2; page <= first.totalPages; page++) {
        const data = euskadiPage.parse(await getJson(`https://api.euskadi.eus/traffic/v1.0/cameras?_page=${page}`));
        if (data.currentPage !== page) throw new Error('Paginación inesperada');
        const part = parseEuskadi(data);
        result.cameras.push(...part.cameras);
        result.excluded += part.excluded;
      }
      return { ...result, cameras: [...new Map(result.cameras.map(c => [c.id, c])).values()] };
    },
  },
  {
    info: info('canarias', 'CanariasWebcams', 'https://www.canariaswebcams.es/',
      'Enlace público · derechos de CanariasWebcams y su proveedor', 'https://www.canariaswebcams.es/aviso-legal',
      'Selección manual: Club Náutico de Candelaria, Tenerife. Su reproductor HTTP se abre en la web original. La ubicación corresponde al lugar señalado en el mapa del proveedor y es aproximada. No cubre todo el archipiélago.'),
    interval: 86400000,
    run: async () => {
      const pageUrl = 'https://www.canariaswebcams.es/webcam/club-nautico-candelaria/';
      const html = load(await getText(pageUrl));
      if (!html('iframe[src="http://demos.wolkam.com/candelaria.html"]').length) {
        throw new Error('El proveedor ha cambiado el reproductor público');
      }
      return { excluded: 0, cameras: [{
        id: 'canarias-candelaria', source: 'canarias', name: 'Club Náutico La Galera · Candelaria',
        place: 'Candelaria, Tenerife', lat: 28.361047103065854, lon: -16.367410084354923,
        category: 'tourism', kind: 'link', pageUrl, refreshSeconds: 0,
        coordinateNote: 'Ubicación aproximada del club en el mapa del proveedor, no del dispositivo. Reproductor externo HTTP.',
      }] };
    },
  },
  {
    info: info('hispa', 'Hispacams', 'https://www.hispacams.com/',
      'Directorio público · reproductor y derechos del proveedor', 'https://www.hispacams.com/aviso-legal/',
      'Webcams de empresas, particulares e instituciones publicadas para el público. Solo metadatos y reproductores públicos integrables; no se extraen flujos protegidos.'),
    interval: 86400000,
    run: async () => {
      const url = 'https://www.hispacams.com/wp-json/wp/v2/webcams?per_page=100&_fields=id,link,title,meta.latitud,meta.longitud,meta.estado,meta.pmpro_default_level,content.protected';
      const result: ImportResult = { cameras: [], excluded: 0 };
      for (let page = 1; page <= 20; page++) {
        const data = hispaSchema.parse(await getJson(`${url}&page=${page}`));
        const part = parseHispa(data);
        result.cameras.push(...part.cameras);
        result.excluded += part.excluded;
        if (data.length < 100) return result;
      }
      throw new Error('El catálogo excede el límite de paginación');
    },
  },
];
