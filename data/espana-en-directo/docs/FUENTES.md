# Fuentes, investigación y cobertura

Investigación y comprobaciones: 19 de septiembre de 2026.

## Catálogos integrados

| Fuente | Catálogo | Medio | Renovación de consulta |
|---|---|---|---|
| DGT | [DATEX II 3.7](https://nap.dgt.es/es/dataset/camaras-dgt-datex2-v3-7) | Captura | 3 minutos |
| Madrid | [Cámaras de tráfico](https://datos.madrid.es/dataset/202088-0-trafico-camaras) | Captura | 5 minutos |
| SCT | [Datos abiertos Cataluña](https://datos.gob.es/es/catalogo/a09002970-camaras-de-trafico-en-las-carreteras-de-cataluna) | Captura | 3 minutos |
| MeteoGalicia | [Webcams](https://www.meteogalicia.gal/web/observacion/camaras) | Captura meteorológica | 2 minutos |
| Euskadi | [Cámaras de administraciones públicas](https://opendata.euskadi.eus/catalogo/-/camaras-de-trafico-de-las-administraciones-publicas-de-euskadi/) | Captura | 3 minutos |
| Hispacams | [Directorio](https://www.hispacams.com/) | Reproductor o enlace original | A petición |
| CanariasWebcams | [Candelaria, Tenerife](https://www.canariaswebcams.es/webcam/club-nautico-candelaria/) | Enlace a la página pública | En origen |

Los intervalos son de consulta en esta aplicación y no prometen la frecuencia de
captura del dispositivo.

### DGT

XML oficial:
https://nap.dgt.es/datex2/v3/dgt/DevicePublication/camaras_datex2_v37.xml

Coordenadas WGS84, carretera, PK, provincia y URL de imagen. La cobertura
documentada excluye Cataluña y País Vasco, que tienen fuentes separadas. Las
marcas de modificación del dispositivo en DATEX no se presentan como fecha de
captura de la imagen.

### Madrid Informo

KML: https://informo.madrid.es/informo/tmadrid/CCTV.kml

Se extraen nombre, número de cámara, coordenadas y la imagen publicada en la
descripción HTML. Se conserva el número con ceros iniciales.
Licencia: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

### Servei Català de Trànsit

XML GML: https://www.gencat.cat/transit/opendata/cameres.xml

Las coordenadas del catálogo usan EPSG:4326 y orden longitud, latitud.
Las imágenes se publican en `http://mct.gencat.cat/mct2bo/RenderService`.
El servicio HTTPS de esas imágenes presentó un error TLS de parámetros DH durante
la investigación; se conserva el enlace HTTP público del catálogo, recuperado
por el backend. No se desactiva la validación de certificados HTTPS.
El catálogo incluye cámaras municipales de Terrassa y Barcelona, que se admiten
con sus rutas públicas específicas. Los registros de Andorra se excluyen:
su host de imágenes no forma parte de las fuentes admitidas de España.

### Open Data Euskadi

API: https://api.euskadi.eus/traffic/v1.0/cameras

Documentación: https://api.euskadi.eus/traffic/api-docs?group=Version_1.0

Se recorren todas las páginas con `_page`. Algunos registros publican coordenadas
proyectadas en campos denominados latitude/longitude; otros no tienen imagen
o utilizan un host/ruta fuera de la allowlist. Se excluyen y se contabilizan.
No se transforma un sistema de coordenadas no documentado.
La disponibilidad del catálogo no garantiza la respuesta de las cámaras.

### MeteoGalicia

JSON: https://servizos.meteogalicia.gal/mgrss/observacion/jsonCamaras.action

[Documentación del formato](https://www.meteogalicia.gal/datosred/infoweb/meteo/docs/rss/JSON_camaras_gl.pdf).
Se muestran municipio, provincia y fecha de captura cuando viene informada.
Se excluyen coordenadas fuera de la caja de España y URLs no admitidas.

### Hispacams

API pública WordPress: https://www.hispacams.com/wp-json/wp/v2/webcams

Se usan metadatos publicados: nombre, coordenadas, estado y página de origen.
Se excluyen cámaras en mantenimiento, en instalación, protegidas y con nivel
de membresía. Solo se buscan iframes publicados en la página pública de la
cámara; se admiten `rtsp.me/embed` y los formatos `/embed` de YouTube.
La existencia del iframe no demuestra que esté emitiendo.

[Aviso legal](https://www.hispacams.com/aviso-legal/).
No se redistribuyen directamente flujos HLS/RTSP ni se extraen tokens.

### CanariasWebcams

Selección manual inicial: Club Náutico La Galera, Candelaria, Tenerife.
La página pública publica el reproductor y un mapa del lugar. Se conserva esa
ubicación como **aproximada**, sin atribuir precisión a la posición del dispositivo.
Como su iframe utiliza HTTP, se abre la página original en vez de integrarlo
dentro de una página HTTPS. Se comprueba que el iframe público sigue publicado
al sincronizar; no se comprueba la emisión del vídeo.

La cobertura canaria inicial es de una sola cámara. Faltan el resto de las
islas y muchos lugares de Tenerife. No es un catálogo regional completo.
[Aviso legal](https://www.canariaswebcams.es/aviso-legal).

## Fuentes investigadas pero no conectadas

- [Windy Webcams API](https://api.windy.com/webcams/docs): requiere API key y
  cumplimiento de su licencia. Algunas URLs de imágenes expiran.
- [SkylineWebcams España](https://www.skylinewebcams.com/es/webcam/espana.html):
  se ofrece el enlace al directorio. Sus
  [condiciones](https://www.skylinewebcams.com/es/terms-of-use.html) restringen
  la extracción/copia de contenido. No se obtuvieron manifiestos ni tokens.
- [Live-Environment-Streams](https://github.com/willytop8/Live-Environment-Streams):
  el README consultado enumeraba 226 entradas para España. Muchos registros
  dependen de tokens y algunos usan coordenadas de ciudad, por lo que no se
  importaron como ubicaciones exactas ni streams garantizados.

## Qué significan los recuentos

- Se cuentan **registros de cámara de cada proveedor**, no dispositivos físicos
  únicos garantizados.
- Hay deduplicación por ID dentro de cada fuente. No se fusionan registros
  entre proveedores por cercanía, pues podrían corresponder a orientaciones
  distintas.
- Las ubicaciones son las publicadas por el proveedor, sin visita de campo.
- La validación geográfica usa cajas aproximadas para Península/Baleares/Ceuta/
  Melilla y Canarias. No hace una prueba punto-en-polígono de la frontera;
  los catálogos integrados están dirigidos a España.
- Las exclusiones pueden deberse al estado de publicación, ubicación, falta de
  imagen, URL no admitida o duplicado. Un error estructural de esquema invalida
  esa sincronización y conserva la última copia válida de la fuente.
- Una instantánea puede estar retrasada o congelada, incluso si devuelve HTTP 200.
  Los encabezados y el reloj incrustado del proveedor son las referencias
  disponibles; no hay comprobación visual automática de movimiento.
- No se comprueba cada cámara periódicamente para evitar cargas masivas. La
  disponibilidad de imagen se comprueba cuando el usuario la abre.

La ampliación requiere nuevos catálogos con ubicaciones y acceso público
documentados. No existe una API que permita afirmar que se han localizado todas
las webcams de España.
