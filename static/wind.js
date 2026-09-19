export function interpolate(grid, lat, lon, key) {
  const x = (lon - grid.west) / grid.step;
  const y = (lat - grid.south) / grid.step;
  if (x < 0 || y < 0 || x > grid.nx - 1 || y > grid.ny - 1) return null;
  const x0 = Math.min(Math.floor(x), grid.nx - 2);
  const y0 = Math.min(Math.floor(y), grid.ny - 2);
  const dx = x - x0, dy = y - y0, i = y0 * grid.nx + x0, a = grid[key];
  return a[i] * (1 - dx) * (1 - dy) + a[i + 1] * dx * (1 - dy)
    + a[i + grid.nx] * (1 - dx) * dy + a[i + grid.nx + 1] * dx * dy;
}

export function sample(regions, lat, lon) {
  for (const grid of regions) {
    const u = interpolate(grid, lat, lon, "u");
    if (u === null) continue;
    const v = interpolate(grid, lat, lon, "v");
    const speed = Math.hypot(u, v);
    return {
      u, v, speed: speed * 3.6, gust: interpolate(grid, lat, lon, "gust") * 3.6,
      from: speed < 0.2 ? null : (Math.atan2(-u, -v) * 180 / Math.PI + 360) % 360,
    };
  }
  return null;
}

export function cardinal(degrees) {
  return degrees === null ? "Calma" : ["N", "NE", "E", "SE", "S", "SO", "O", "NO"][Math.round(degrees / 45) % 8];
}

export function color(speed) {
  const stops = [[0, [222, 239, 221]], [10, [157, 211, 175]], [20, [63, 171, 178]],
    [35, [61, 140, 204]], [50, [237, 181, 89]], [70, [218, 95, 70]]];
  for (let i = 1; i < stops.length; i++) {
    if (speed <= stops[i][0]) {
      const t = Math.max(0, (speed - stops[i - 1][0]) / (stops[i][0] - stops[i - 1][0]));
      const rgb = stops[i][1].map((v, j) => Math.round(stops[i - 1][1][j] * (1 - t) + v * t));
      return `rgb(${rgb.join(",")})`;
    }
  }
  return "rgb(218,95,70)";
}
