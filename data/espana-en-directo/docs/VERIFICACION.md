# Verificación de entrega

Fecha: 19 de septiembre de 2026.

## Catálogo importado

| Fuente | Registros admitidos | Excluidos | Última sincronización |
|---|---:|---:|---|
| DGT | 1.948 | 0 | Correcta |
| Madrid Informo | 357 | 0 | Correcta |
| SCT, incluyendo Barcelona y Terrassa | 130 | 34 | Correcta |
| MeteoGalicia | 31 | 2 | Correcta |
| Open Data Euskadi | 295 | 194 | Correcta |
| Hispacams | 164 | 63 | Correcta |
| CanariasWebcams, selección de Candelaria | 1 | 0 | Página pública comprobada |
| **Total** | **2.926** | **293** | |

Son 2.761 entradas de capturas periódicas, 164 de reproductores potencialmente
integrables y un enlace externo. Los recuentos cambian con el tiempo.
**No son 2.926 cámaras verificadas emitiendo.**

La cobertura canaria se limita a Candelaria, Tenerife. El resto de las islas
no está cubierto por esta importación. En el conjunto nacional también faltan
muchas cámaras y zonas. Las exclusiones de SCT incluyen 29 registros de Andorra
y cinco enlaces duplicados. Las fuentes se explican en `FUENTES.md`.

## Comprobaciones técnicas

| Comprobación | Resultado |
|---|---|
| Instalación de dependencias | Correcta |
| `npm run typecheck` | Sin errores |
| `npm run lint` | Sin errores |
| `npm test` | 19 tests superados |
| `npm run build` | Compilación correcta |
| `npm audit` | 0 vulnerabilidades reportadas al comprobar |
| Sincronización real de seis catálogos | Correcta |
| Comprobación adicional de CanariasWebcams | Correcta |
| Inicio del servidor Node | Correcto |
| `/`, favicon, `/api/catalog`, `/api/health` | Respuestas correctas |
| IDs desconocidos de imagen/reproductor | HTTP 404 |

Los tests cubren distancia Haversine, islas/enclaves, coordenadas inválidas,
formatos de los seis proveedores, iframes diferidos, restricciones de acceso,
redirecciones seguras, límites de respuesta, rechazo de entidades XML y
conservación del catálogo tras fallos/reinicio.

Durante la implementación se detectaron y corrigieron:

- Coordenadas GML con atributos XML, que deben extraer su nodo de texto.
- Iframes públicos diferidos con `src="about:blank"` y `data-lazy-src`.
- Redirección oficial de SCT desde `RenderService` a `TransitCamera`.
- Cámaras municipales sin punto kilométrico.
- Confianza en CA del sistema para las peticiones Node, manteniendo TLS activo.
- Una versión vulnerable de Vite, actualizada a 6.4.3.

## Muestra real de imágenes y reproductores

Comprobada a través de la API del servidor, sin simular respuestas:

| Cámara | Resultado observado |
|---|---|
| DGT, A-62 km 25,3 (`dgt-176130`) | HTTP 200, JPEG, 70.880 bytes |
| Madrid, Plaza de Castilla norte (`madrid-06303`) | HTTP 200, JPEG, 194.240 bytes |
| SCT, C-58 km 0,50 | HTTP 200, JPEG, 434.310 bytes |
| MeteoGalicia, Ribadeo | HTTP 200, JPEG, 54.542 bytes |
| Terrassa, Plaça Doré | HTTP 200, JPEG, 60.746 bytes |
| Barcelona, Plaça Antonio López | HTTP 200, GIF, 43.048 bytes |
| Euskadi, Autonomía/Gordóniz | No disponible; upstream 404, API 502 controlado |
| Euskadi, Iurreta | No disponible en la consulta; API 502 controlado |
| Hispacams, Formentera — Es Pujols | API 200, iframe público de rtsp.me resuelto |
| CanariasWebcams, Candelaria | Página accesible y referencia al iframe público presente; enlace externo |

Los fallos de Euskadi son de las cámaras consultadas: su catálogo sí respondió.
Esto no permite afirmar que todas sus cámaras estén caídas ni que las demás
funcionen. No se hizo un barrido de disponibilidad de cada cámara.

## Pendiente de prueba en navegador

No se ha realizado una prueba manual de la interfaz ni de reproducción de vídeo.
Se han compilado la interfaz y sus tipos, probado la lógica y comprobado las
rutas HTTP e imágenes indicadas arriba.

Una prueba posterior debería recorrer selección de punto, radio, búsqueda,
filtros, agrupación de marcadores, favoritas, enlace compartido, errores de imagen,
reproductor externo y tamaño móvil. El permiso de geolocalización y las
restricciones de iframes dependen además del navegador y del alojamiento.

## Entrega

El ZIP incluye código, dependencias bloqueadas, documentación, tests y una copia
del catálogo de metadatos para que el primer inicio no quede vacío.
No incluye credenciales, node_modules ni imágenes de terceros.
Se arranca con los pasos de `README.md`.

La vista previa funciona mientras la máquina de la sesión esté activa.
No se ha creado un despliegue público permanente ni un PR: no había un
repositorio remoto conectado.
