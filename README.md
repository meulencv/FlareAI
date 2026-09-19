# FlareAI

**España, bajo observación.** Mapa blanco con anomalías térmicas NASA, viento y temperatura NOAA, imágenes satelitales y un escenario visual orientado por el viento.

## Arranque

Probado con Python 3.10 en Ubuntu. La interfaz no necesita Node, compilación, clave API ni servicios de mapas externos.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py --host 127.0.0.1 --port 8090
```

Abrir `http://127.0.0.1:8090` en el navegador de **esa máquina**. Para una máquina remota, usar un túnel SSH o un proxy HTTPS. `--host 0.0.0.0` permite conexiones a sus interfaces de red. La vista previa de Devin utiliza este modo; no es un despliegue permanente.

El ZIP incluye datos del **19 de septiembre de 2026** e imágenes del **18 de septiembre**. Al arrancar, el servidor sirve esa caché e intenta actualizarla. Consulta siempre las fechas de cada fuente.

### Sin conexión

```bash
python app.py --offline --host 127.0.0.1 --port 8090
```

Muestra el periodo de la muestra guardada, identificado como tal, aunque hayan transcurrido días. Las imágenes de Igea en ambas capas están guardadas. Otras zonas solo tendrán imagen offline si se consultaron antes con conexión. No se contacta con NASA ni NOAA en este modo.

## Qué puedes hacer

- Seleccionar una superficie de calor o una zona de la lista.
- Buscar provincias y filtrar el caso contrastado en prensa.
- Cambiar entre Península, Baleares, Canarias y Ceuta/Melilla.
- Ver viento, rachas, temperatura ambiente y brillo térmico.
- Pulsar un foco para encuadrar automáticamente su entorno y ver el **mapa de calor de riesgo inmediato alrededor**, de crema a coral. Sin activar capas, listas ni marcadores adicionales.
- Pasar el ratón por el calor para leer qué hay en ese punto: instalaciones, residentes censados, vegetación y distancia a la huella.
- El potencial combina proximidad, población, vegetación, instalaciones y viento vigente. Es una prioridad exploratoria de revisión, no una probabilidad de incendio ni una recomendación operativa. Los datos y los motivos quedan en `/api/context?id=<id>` para análisis posterior por una IA.
- Consultar color natural o SWIR y ampliar la imagen.
- Acercar la huella aproximada de los píxeles.
- Ver bordes de llama, núcleos de calor y chispas que siguen el viento local.
- Explorar corrientes animadas, con zoom continuo centrado en el cursor y reproyección durante el arrastre.
- Pausar las animaciones con **Ⅱ** junto a los controles del mapa. Se respeta la preferencia del sistema de reducir movimiento.
- Pulsar **Escenario**: elegir avance supuesto y reproducir de 0 a 6 horas.
- Exportar JSON con el botón superior, o CSV desde `/api/incidents.csv`.

## Cómo interpretar el mapa

**No todas las señales son incendios forestales.** Se agrupan observaciones térmicas, incluidas posibles industrias y quemas agrícolas. La detección depende del satélite, las nubes, el horario y el tamaño del fenómeno. No es un inventario exhaustivo.

**No conocemos el perímetro quemado.** La cifra de huella térmica aproxima el área cubierta por los píxeles. No equivale a hectáreas quemadas. Por eso la superficie quemada confirmada aparece como «—».

**Las llamas son un tratamiento visual.** El contorno parte de la huella de los píxeles y añade resplandor, ondulación y chispas. La silueta queda anclada al terreno: al hacer zoom escala como el mapa, sin deformarse; las huellas pequeñas se reconocen por su halo, no por un contorno agrandado. El color, la velocidad de animación y las chispas no miden temperatura, transporte de pavesas ni avance del fuego. Para ver el detalle, selecciona **Igea → Acercar a la huella detectada**.

**La imagen es un mosaico diario, no una cámara en directo.** La aplicación busca la fecha más reciente con suficiente cobertura y muestra su fecha.

**Las dos temperaturas significan cosas distintas.** GFS proporciona temperatura ambiente modelizada a 2 m. VIIRS I4 proporciona temperatura de brillo de un píxel; no es temperatura de las llamas.

**El escenario es ilustrativo.** Su velocidad de avance es un supuesto elegido en el control. Solo usa el viento para la dirección; no es un modelo de propagación ni una herramienta de emergencia.

## Contexto territorial sin base de datos

El atlas adjunto se conserva en `data/Espana_Datos_y_Mapas/`, con sus mapas, fuentes, scripts y datos originales. El servidor carga una sola vez el CSV comprimido de 511.226 celdas y el CSV de 44.787 elementos OSM; no instala el pipeline GIS del atlas ni vuelve a descargar sus fuentes. Si esos archivos faltan, el panel avisa de contexto no disponible y el resto del observatorio sigue funcionando.

- **Población:** INE / Eurostat, censo 2021; centros de celdas de 1 km², no ubicaciones de viviendas ni núcleos con nombre. Las edades publicadas pueden no sumar el total por protección estadística.
- **Suelo:** Copernicus CGLS-LC100 2019; porcentajes ponderados por superficie clasificada, conservando ausencia de cobertura.
- **Instalaciones:** OSM / Geofabrik, 18/09/2026; prioridad orientativa por actividad, no riesgo oficial. Puede haber omisiones o varios elementos de un mismo complejo.
- **Viento:** sector de ±30° hacia donde sopla, desde la huella, con un mínimo de 3 km/h. Se desactiva con datos ausentes, errores meteorológicos, validez alejada más de 2 h o ciclo de más de 12 h. En modo offline solo se muestra orientación histórica.

`potential` conserva todas las muestras, instalaciones cercanas, geometrías visuales, factores, puntuación 0–100 y versión del modelo. La escala no es un porcentaje de riesgo: los pesos son heurísticos, aún no calibrados operacionalmente. El suavizado de las áreas no delimita zonas de peligro y la ausencia de color no garantiza seguridad. Las actualizaciones refrescan la capa sin cambiar el encuadre elegido por el usuario.

No se estima población afectada, tiempo de llegada ni evacuaciones. Se conservan los demás campos del atlas, pero sexo, lugar de nacimiento y movilidad no se utilizan para asignar riesgo de incendio. Fuentes y condiciones de reutilización: `data/Espana_Datos_y_Mapas/FUENTES.md` (también en `/atlas/sources`). Las condiciones de GISCO requieren revisión antes de uso comercial.

## Actualización y consumo

| Fuente | Comprobación del servidor | Frecuencia real / detalle |
|---|---:|---|
| NASA FIRMS VIIRS | Cada 30 min | Detecciones según pasadas; pueden llegar horas después |
| NOAA GFS | Cada 10 min | Pasos horarios; ciclos cada 6 h; malla de 0,25° |
| NASA GIBS | Al seleccionar zona y capa | Mosaico diario; caché por zona/capa/hora |
| Navegador | Cada 60 s | Consulta únicamente a este servidor |

Los visitantes comparten una descarga meteorológica y una caché de focos. No se solicita GFS por visitante. El acceso público probado no requiere clave; no constituye una garantía de capacidad infinita ni de disponibilidad.

## Archivos

- `app.py`: servidor y caché compartida.
- `gfs.py`: descarga parcial GRIB2, validación ecCodes e interpolación.
- `detectar.py`: CSV globales FIRMS y filtro geográfico/temporal.
- `incidents.py`: agrupación, provincias, huellas y métricas.
- `satellite.py`: imágenes NASA GIBS con caché y control de cobertura.
- `static/`: interfaz y Leaflet local.
- `static/flow.js`: geometría, partículas, índice geográfico y presupuestos de dibujo.
- `static/flames.js`: renderizador Canvas 2D de fuego y corrientes, sin dependencia de WebGL.
- `static/heat.js`: mapa de calor del entorno (paleta, densidad acumulada y rótulo al pasar el ratón).
- `data/`: datos activos y evidencias originales de las descargas.
- `examples/`: muestra congelada para reproducir pruebas.
- `evidence/`: verificación HTTP y captura de pantalla completa.
- `docs/IMPLEMENTACION.md`: arquitectura, fórmulas, APIs y fuentes.
- `docs/VERIFICACION.md`: alcance y resultados de las comprobaciones.

## Verificar

```bash
python -m pip install -r requirements-dev.txt
python -m unittest -v
ruff check *.py
python -m mypy --ignore-missing-imports *.py
python -m compileall -q *.py
# Solo para las pruebas de JavaScript: Node >= 20; probado con Node 24.
node --test test_*.mjs
npx --yes --package eslint@9.33.0 eslint static/*.js test_*.mjs
```

Con la aplicación arrancada:

```bash
python verify_api.py --url http://127.0.0.1:8090
curl http://127.0.0.1:8090/api/incidents.csv -o zonas.csv
```

Las pruebas HTTP consultan ambos productos de imagen de la primera zona. Con conexión pueden descargar dos imágenes a GIBS. En modo offline usan la caché.

## Implantación

Este servidor es un prototipo reproducible con la biblioteca estándar de Python. Para servicio público persistente, ejecutar un único proceso de adquisición, almacenar cachés y evidencias en un volumen persistente y servir los recursos mediante un proxy HTTPS. Configurar límites de concurrencia y peticiones en el proxy; para tráfico alto, trasladar el servidor a un framework de producción. Evitar iniciar varios escritores sobre el mismo directorio `data/`.

No se han validado instalaciones Windows/macOS ni cargas de producción. Los binarios ecCodes pueden requerir instalación específica en esas plataformas.
