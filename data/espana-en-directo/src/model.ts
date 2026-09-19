import { z } from 'zod';

export const cameraSchema = z.object({
  id: z.string(),
  source: z.string(),
  name: z.string(),
  place: z.string(),
  lat: z.number().finite(),
  lon: z.number().finite(),
  category: z.enum(['traffic', 'landscape', 'tourism']),
  kind: z.enum(['snapshot', 'player', 'link']),
  pageUrl: z.string().url(),
  imageUrl: z.string().url().optional(),
  imageTimestamp: z.string().optional(),
  refreshSeconds: z.number(),
  coordinateNote: z.string().optional(),
});
export type Camera = z.infer<typeof cameraSchema>;

export const sourceSchema = z.object({
  id: z.string(),
  name: z.string(),
  url: z.string().url(),
  license: z.string(),
  licenseUrl: z.string().url(),
  note: z.string(),
  status: z.enum(['pending', 'ok', 'error']),
  count: z.number(),
  excluded: z.number(),
  checkedAt: z.string().optional(),
  updatedAt: z.string().optional(),
  error: z.string().optional(),
});
export type Source = z.infer<typeof sourceSchema>;
export const catalogSchema = z.object({
  cameras: z.array(cameraSchema),
  sources: z.array(sourceSchema),
});
export type Catalog = z.infer<typeof catalogSchema>;

export function inSpainBounds(lat: number, lon: number): boolean {
  return Number.isFinite(lat) && Number.isFinite(lon) && (
    (lat >= 35.1 && lat <= 44.2 && lon >= -9.7 && lon <= 4.5)
    || (lat >= 27.5 && lat <= 29.6 && lon >= -18.3 && lon <= -13.2)
  );
}

export function distanceKm(a: { lat: number; lon: number }, b: { lat: number; lon: number }): number {
  const rad = Math.PI / 180;
  const h = Math.sin((b.lat - a.lat) * rad / 2) ** 2
    + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin((b.lon - a.lon) * rad / 2) ** 2;
  return 6371.0088 * 2 * Math.atan2(Math.sqrt(Math.min(1, h)), Math.sqrt(Math.max(0, 1 - h)));
}

export const normalize = (s: string): string => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
