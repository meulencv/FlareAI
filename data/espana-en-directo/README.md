# Faro — webcams de España

Mapa interactivo para encontrar webcams cerca de cualquier punto. Reúne seis
catálogos públicos y una selección inicial de CanariasWebcams, distingue capturas periódicas de reproductores y enlaces, atribuye cada
fuente y conserva la última sincronización cuando un proveedor falla.

**No es un inventario exhaustivo.** La cobertura depende de las fuentes, sus
condiciones, sus coordenadas y su disponibilidad. No busca dispositivos expuestos
por error ni accede a cámaras que requieren autenticación.

## Arranque

Requisitos: **Node.js 24.0 o posterior**, npm y conexión a Internet.

Desde el directorio del proyecto:

```sh
npm ci
npm run build
npm start
```

Abre `http://localhost:3000`. Al arrancar se restaura `data/catalog.json` si existe
y se sincronizan las fuentes que lo necesitan. En el primer inicio, el catálogo
puede tardar uno o dos minutos. Para sincronizar inmediatamente todas las fuentes:

```sh
npm run sync
```

Este comando devuelve código 1 si alguna fuente falla, aunque las demás hayan
funcionado. El detalle aparece en consola y en **Fuentes y cobertura**. Un fallo
conserva las cámaras anteriores de esa fuente. Evita ejecutar sincronizaciones
manuales simultáneas con otro proceso que escriba el mismo catálogo.

Las instrucciones npm del servidor usan `--use-system-ca`: Node confía también
en los certificados instalados en el sistema, sin desactivar la verificación TLS.

`PORT` permite cambiar el puerto. Mantén `data/` en almacenamiento persistente
si despliegas el servidor. No basta con subir el frontend a un alojamiento
estático: las rutas `/api` requieren el proceso Node.

## Uso

- **Clic en el mapa:** fija el punto y ordena todas las coincidencias por distancia
  en línea recta. Elige un radio de 5, 10, 25, 50 o 100 km si quieres limitarlo.
- **Clic en un grupo de marcadores:** acerca el mapa.
- **Clic en una cámara:** abre la captura o el acceso al reproductor.
- **Buscar + Intro:** busca nombres de cámaras, municipios y carreteras.
  Las sugerencias de lugares usan una lista local de ciudades e islas;
  no constituyen un geocodificador de todas las direcciones de España.
  También admite `40.4168, -3.7038`.
- **Mi ubicación:** solicita permiso al navegador. Las coordenadas se usan en
  memoria para calcular distancias; no se envían a nuestro backend.
  Requiere HTTPS o localhost y puede no estar disponible en una vista previa.
- **Filtros:** categoría, fuente, distancia y favoritas.
- **Favoritas:** se guardan en este navegador, sin cuenta.
- **Copiar enlace:** crea un enlace directo a la cámara mediante el fragmento URL.
- **Fuentes y cobertura:** recuentos, exclusiones, licencias y estado de cada
  sincronización. “Sincronizado” se refiere al catálogo, no a cada cámara.

La lista sin punto seleccionado muestra las cámaras dentro de la vista actual
del mapa. Con un punto seleccionado, muestra las más cercanas aunque estén fuera
de la vista. Los botones de región quitan el punto y conservan los demás filtros.

## Imágenes y reproductores

Las cámaras de tráfico y MeteoGalicia son **capturas periódicas**, no vídeo
continuo. El visor renueva la consulta mientras está abierto y la pestaña está
visible. La caché del servidor respeta el intervalo de cada fuente; pulsar
“Consultar” no obliga al proveedor a tomar una foto nueva.

“Recuperada” indica cuándo nuestro servidor descargó la imagen.
“Modificada en origen” es el encabezado HTTP `Last-Modified`, si el proveedor lo
envía. Ninguno garantiza la hora real de captura. MeteoGalicia aporta además una
fecha propia sin zona horaria, que se muestra tal como la publica, en hora
peninsular. Se advierte si `Last-Modified` tiene más de 30 minutos.

Los reproductores se cargan **después de pulsar el botón**, porque contactan con
servicios externos que pueden usar cookies y mostrar publicidad. Si el portal
no publica un iframe compatible, ofrece el enlace a la fuente original.
No se extraen manifiestos ni tokens de vídeo.

## Desarrollo y comprobaciones

```sh
npm run typecheck
npm run lint
npm test
npm run build
npm audit
```

Para editar con recarga automática, ejecuta `npm run dev` y, en otra terminal,
`npm run dev:ui`. Vite escucha en `http://localhost:5173` y envía `/api` al
servidor en el puerto 3000. `npm run dev` sirve la última compilación si existe;
la recarga del frontend la proporciona `dev:ui`.

Los tests no dependen de Internet. Cubren formatos XML/JSON, coordenadas, acceso
público de Hispacams, allowlists, límites de descarga y conservación del catálogo
tras errores y reinicios.

## Arquitectura

- `src/main.ts`: Leaflet, Supercluster, filtros, distancias y visor.
- `src/model.ts`: esquemas Zod y Haversine.
- `src/places.ts`: sugerencias locales de lugares.
- `server/sources.ts`: seis catálogos y una selección de enlaces públicos canarios.
- `server/catalog.ts`: sincronización y escritura atómica de la caché.
- `server/network.ts`: límites de respuesta y allowlists.
- `server/index.ts`: API, caché de imágenes y resolución de iframes.
- `docs/FUENTES.md`: investigación, procedencia y límites de cobertura.
- `docs/VERIFICACION.md`: resultados de las comprobaciones de entrega.

### API

| Ruta | Resultado |
|---|---|
| `GET /api/catalog` | Cámaras normalizadas y estado de las fuentes |
| `GET /api/health` | Número de cámaras cargadas |
| `GET /api/cameras/:id/image` | Imagen permitida, o 404/502 |
| `GET /api/cameras/:id/player` | URL de iframe público admitido, `null`, o error |

La API no acepta una URL arbitraria como parámetro. El proxy de imágenes restringe
dominios/rutas, protocolos y puertos; revalida cada destino de redirección, limita cada imagen a
5 MB y mantiene como máximo ocho descargas simultáneas y 40 imágenes en memoria.
Las respuestas de catálogo tienen un límite de 12 MB. Los XML con entidades o
DOCTYPE se rechazan.

### Añadir fuentes

Añade un adaptador a `server/sources.ts` que devuelva el modelo `Camera`, atribución
y un intervalo de sincronización. Valida el esquema del proveedor, documenta
su licencia y añade solo los hosts/rutas de imágenes necesarios a la allowlist.
Conserva coordenadas originales y marca su precisión cuando la fuente la
documente. La caja geográfica es una validación aproximada; no valida límites
municipales, fronteras ni el emplazamiento físico de una cámara.

Los catálogos se actualizan cada hora, MeteoGalicia cada cinco minutos y
Hispacams/CanariasWebcams una vez al día. Tras un fallo se reintenta a los cinco minutos.
Las consultas remotas reintentan una vez ante un error de descarga.

## Despliegue

Ejecuta los mismos pasos de arranque en un servidor Node, con HTTPS a través de
tu proxy/plataforma y un volumen persistente para `data/`. Un único proceso
escribe el catálogo. Para tráfico elevado, añade límites por cliente en el
proxy y revisa los permisos de redistribución y las cuotas de cada proveedor.
No se ha publicado automáticamente en Internet.

El mapa usa teselas estándar de OpenStreetMap con atribución visible. Respeta su
[política de uso](https://operations.osmfoundation.org/policies/tiles/);
para un servicio con mucho tráfico, configura un proveedor de teselas adecuado.
No hay descargas masivas ni precarga de teselas.

Los derechos sobre imágenes, reproductores y datos corresponden a sus
respectivos proveedores. Ver el detalle de fuentes antes de redistribuirlos.
