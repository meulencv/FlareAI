export function destination(from) {
  return from === null ? null : (from + 180) % 360;
}

export function scenario(incident, hours, rate) {
  if (!Number.isFinite(hours) || !Number.isFinite(rate) || hours < 0 || hours > 6 || rate < 0 || rate > 1) {
    throw new Error("Parámetros de escenario fuera de rango");
  }
  const bearing = destination(incident.weather.wind_from_degrees);
  if (hours === 0 || bearing === null) return null;
  const angle = bearing * Math.PI / 180;
  const advance = hours * rate;
  const radius = Math.sqrt(incident.footprint_ha / 100 / Math.PI);
  const along = radius + advance / 2, across = radius + advance * .14;
  const coordinates = [];
  for (let i = 0; i <= 80; i++) {
    const t = 2 * Math.PI * i / 80;
    const forward = advance / 2 + Math.cos(t) * along;
    const side = Math.sin(t) * across;
    const east = forward * Math.sin(angle) + side * Math.cos(angle);
    const north = forward * Math.cos(angle) - side * Math.sin(angle);
    coordinates.push([incident.lon + east / (111.32 * Math.cos(incident.lat * Math.PI / 180)),
      incident.lat + north / 111.32]);
  }
  return { type: "Polygon", coordinates: [coordinates] };
}

export function imagePoints(detections, bbox) {
  return detections.map(p => ({
    x: (p.lon - bbox[0]) / (bbox[2] - bbox[0]) * 900,
    y: (bbox[3] - p.lat) / (bbox[3] - bbox[1]) * 600,
  })).filter(p => p.x >= 0 && p.x <= 900 && p.y >= 0 && p.y <= 600);
}
