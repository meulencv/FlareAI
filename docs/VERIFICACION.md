# Verificación

Datos contrastados inicialmente el **19/09/2026 a las 06:15 UTC**. Renderizador actualizado y verificado alrededor de las **06:40 UTC**.

## Datos reales

- Descarga de los tres CSV globales públicos VIIRS y filtro sobre España.
- Muestra: **135 observaciones agrupadas en 44 zonas**. Estas cifras no equivalen a 44 incendios confirmados.
- NOAA GFS: ciclo **19/09/2026 00 UTC**, validez **06 UTC**, paso **f006**.
- Se decodificaron realmente UGRD, VGRD, GUST y **TMP a 2 m**. ecCodes validó `2t`, unidad K, malla y fechas.
- Igea: 15 observaciones, 4 pasadas; brillo I4 máximo 367 K, equivalente a 93,9 °C; FRP máximo por píxel 37,1 MW.
- En el centro del grupo: viento modelizado 1,9 km/h, racha 2,7 km/h y temperatura ambiente modelizada 10,8 °C para las 06 UTC.
- Huella geométrica aproximada de Igea: 203,7 ha. **No es superficie quemada.** `burned_area_ha` es nulo.
- Imágenes GIBS reales de Igea en color natural y SWIR, fechadas **18/09/2026**, 900×600 píxeles.

El mosaico solicitado para el día 19 aún devolvía una imagen negra opaca. Se detectó este caso, se añadió una validación de cobertura RGB además de transparencia y se recuperó el día 18. La respuesta descartada se conserva en `evidence/rejected-gibs/`; no se presenta como foto válida.

Los valores anteriores pertenecen a la muestra de verificación. Cambiarán cuando entren nuevas observaciones o pasos meteorológicos.

## Pruebas automáticas

**11 pruebas Python**, correctas:

1. Conservación de todas las observaciones del periodo.
2. Identificadores únicos y área quemada no inventada.
3. Conversión Kelvin/Celsius y procedencia del viento.
4. Decodificación del GRIB de temperatura real y comparación con el recorte.
5. Dimensiones, finitud y plausibilidad de temperatura en ambas regiones.
6. Unión de huellas sin duplicar área por un píxel repetido.
7. Agrupación conexa e independencia del orden.
8. Diferencia entre brillo satelital y temperatura ambiente.
9. Ventana reciente vacía cuando el periodo expira.
10. Conservación explícita de la muestra histórica en modo offline y rechazo de imágenes vacías.
11. Servidor HTTP offline real con ambos PNG archivados y acceso externo a GIBS bloqueado mediante mock.

La enumeración agrupa algunas aserciones; el detalle de los 11 métodos ejecutados está en `evidence/tests-python.txt`.

**18 pruebas JavaScript**, correctas:

- Procedencia frente a desplazamiento.
- Geometría del escenario hacia el este con viento del oeste.
- Ausencia de proyección inventada con calma/horizonte cero y rechazo de parámetros inválidos.
- Posicionamiento de observaciones en la imagen, norte arriba.
- Interpolación vectorial que evita el salto angular 0/360.
- Dirección de partículas y ausencia de desplazamiento con calma o sin viento.
- Velocidades, vida útil y presupuestos acotados; semillas dentro de la huella.
- Índice geográfico con islas y huecos.
- Borde detallado determinista con límite de vértices; colas orientadas desde su primer fotograma.
- Renderizador con mapa, reloj y Canvas instrumentados: reproyección conjunta de cabeza y cola al arrastrar; longitud visual estable después de un cambio de zoom; dibujo inmediato sin esperar a `moveend`.
- Pausa, reanudación, pestaña oculta, cambios de movimiento reducido, retirada de capas al filtrar, interruptor de viento y DPR acotado.

Las cinco pruebas del renderizador usan dobles de Canvas y Leaflet bajo Node; verifican operaciones y planificación de fotogramas, no la aceleración gráfica ni la tasa de refresco de dispositivos físicos.

Resultados completos: `evidence/tests-javascript.txt`.

También pasaron Ruff, mypy, compileall, comprobación sintáctica JavaScript y ESLint (`no-undef`, `no-unused-vars`).

## HTTP

`verify_api.py` se ejecutó contra el servidor conectado y contra un servidor offline:

- JSON combinado válido.
- CSV con el mismo número de filas que grupos JSON.
- Temperatura ambiente presente.
- Superficie quemada confirmada nula.
- Imágenes natural/SWIR descargables, tamaño correcto y cobertura suficiente.
- Rechazo de ID ausente, ID desconocido y capa inválida.
- Recursos fuera de la lista pública no servidos.

Evidencias: `evidence/api_ready.json` y `evidence/api_offline.json`. Los hashes y peticiones originales se conservan en `data/evidence/`, `data/firms/` y `data/satellite/`.

## Interfaz y alcance

Se guardaron capturas completas, sin recorte, de la vista nacional y del detalle de Igea. La versión nueva muestra la huella con gradientes, borde animado y chispas; el viento usa partículas geográficas con colas reconstruidas y zoom continuo.

No se ha ejecutado una batería automatizada de navegación end-to-end, pruebas en móviles físicos, medición de FPS, pruebas de carga ni validación de propagación física. El escenario no constituye un modelo científico de incendios. La accesibilidad y las reglas responsive están implementadas, pero no certificadas mediante auditoría.

## Reproducción

Seguir el README. Las pruebas de agrupación y GRIB utilizan las muestras congeladas en `examples/`, para que una descarga posterior no cambie el resultado esperado. Conservar el directorio de evidencias del ciclo incluido.

La integridad de la entrega puede comprobarse desde su carpeta **antes del primer arranque o prueba**; la actualización modifica legítimamente datos y evidencias:

```bash
sha256sum -c SHA256SUMS.txt
```
